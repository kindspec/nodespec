# SPDX-License-Identifier: MIT
"""One three-way case, end to end: inputs, exposure, merge outcome, records.

`prepare` reads the inputs only (one-fence rule, subset, legs change the
model, exposure); `outcome` then reads the merge result. Exposure is fixed
before the merge result is read (§5.5), and V3 checks that changing the
merged file does not change it.
"""
import hashlib

from . import fence as FN
from . import gitops as G
from . import oracle as OR
from . import subset as SS


def case_key(texts):
    """§7.5: the sha256 of the three input texts, in order (for D, the fence
    bodies), as UTF-8, each followed by a NUL."""
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8") + b"\0")
    return h.hexdigest()


def diff_key(prep):
    """§7.5: "Two cases with identical pairs of model diffs are one case."
    The pair of (base -> leg) model diffs, as a sha256."""
    B, O, T = (prep["states"][i].model for i in range(3))

    def d(X):
        return sorted((repr(u), repr(B.get(u)), repr(X.get(u))) for u in set(B) | set(X) if B.get(u) != X.get(u))
    return hashlib.sha256(repr((d(O), d(T))).encode()).hexdigest()


def decode(b):
    try:
        return b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None


def prepare(stratum, base, o, t, R):
    """Inputs only. base/o/t: file texts (str). R: rbridge.RCache.
    Returns a dict; "excluded" names why when the case is not evaluable."""
    out = {"stratum": stratum, "excluded": None}
    diags = []
    for name, txt in (("base", base), ("o", o), ("t", t)):
        d, why = FN.diagram_of(stratum, txt)
        if d is None:
            out["excluded"] = f"one-fence rule: {name}: {why}" if stratum == "D" else f"{name}: {why}"
            return out
        diags.append(d)
    out["diagrams"] = diags
    out["key"] = case_key(diags)
    rs = R.get_many(diags)
    states = [SS.classify(d, r) for d, r in zip(diags, rs)]
    out["states"] = states
    if any(s.status != "in" for s in states):
        out["excluded"] = "out of subset: " + "; ".join(
            f"{n}: {s.status} {s.reason}" for n, s in zip(("base", "o", "t"), states) if s.status != "in")
        return out
    B, O, T = (s.model for s in states)
    out["legs_change"] = (O != B, T != B)
    out["exposed"], out["exposure_reason"] = OR.exposure(B, O, T)
    out["diff_key"] = diff_key(out)
    if not all(out["legs_change"]):
        out["excluded"] = "a leg does not change the model"
    return out


def lints_of(stratum, state, text=None, path=None):
    fence_ok = True
    if stratum == "D" and text is not None:
        fence_ok = FN.diagram_of("D", text)[0] is not None
    return OR.lint_failures(state.model if state else None, state.db if state else None, stratum,
                            fence_ok, path)


def outcome(prep, inputs, merge, R, path="", truth=None):
    """prep: from prepare (not excluded). inputs: the three file texts.
    merge: gitops.Merge for the path. truth: P's later version, file text.
    Returns {"outcome", "records", ...}."""
    stratum = prep["stratum"]
    res = {"outcome": None, "records": [], "exposed": prep["exposed"]}
    mtxt = decode(merge.merged) if merge.merged is not None else None
    if merge.merged is None:
        res.update(outcome="E", why="the merged path is absent")
        return res
    if mtxt is None:
        res.update(outcome="E", why="the merged file is not UTF-8")
        return res
    if merge.unmerged or G.has_new_marker(mtxt, inputs):
        res.update(outcome="E", why="conflict")
        return res
    d, why = FN.diagram_of(stratum, mtxt)
    if d is None:
        # G0, always tier B (§5.4); the merged state is not judged further.
        res.update(outcome="G0", why=why)
        res["records"] = [{"category": "G0", "objects": ["path:" + path], "tier": "B", "units": [],
                           "detail": why}]
        return res
    r = R.get(d)
    if not r.get("parse"):
        res.update(outcome="E", why=f"R does not parse the merged diagram: {r.get('cls')}")
        return res
    ms = SS.classify(d, r)
    res["merged_status"] = ms.status
    if ms.status == "duptitle":
        res.update(outcome="DUP-TITLE", why=ms.reason)
        return res
    if ms.status != "in":
        res.update(outcome="OUT-OF-SUBSET", why=ms.reason)
        return res
    B, O, T = (s.model for s in prep["states"])
    lint_in = set()
    for s, txt in zip(prep["states"], inputs):
        lint_in |= lints_of(stratum, s, txt, path)
    lint_m = lints_of(stratum, ms, mtxt, path)
    lint_new = lint_m - lint_in
    recs, dec, mc = OR.judge(B, O, T, ms.model, lint_new)
    res["outcome"] = "JUDGED"
    res["lint_new"] = sorted(f"{a}:{b}" for a, b in lint_new)
    # H's records before §8.3's truth filter: what X, which never sees the
    # truth (Appendix D), is compared with (§10.5).
    res["records_unfiltered"] = [dict(r) for r in recs]
    if truth is not None:
        recs = p_filter(recs, prep, ms.model, truth, R, dec)
    res["records"] = recs
    return res


def p_filter(recs, prep, M, truth_text, R, dec):
    """§8.3: a record is a P record only if the merged model also differs
    from the truth's model on that unit; one whose unit neither leg touched
    and whose decided value differs from the truth is UNRELIABLE.
    R-p-units: a record's units are those `judge` lists for it."""
    stratum = prep["stratum"]
    d, _ = FN.diagram_of(stratum, truth_text)
    if d is None:
        for r in recs:
            r["unreliable"] = "the truth has no diagram"
        return recs
    ts = SS.classify(d, R.get(d))
    if ts.status != "in":
        for r in recs:
            r["unreliable"] = f"the truth is not in the subset: {ts.status}"
        return recs
    TR = ts.model
    B, O, T = (s.model for s in prep["states"])
    out = []
    for r in recs:
        units = [eval_unit(u) for u in r["units"]]
        if not any(M.get(u) != TR.get(u) for u in units):
            continue  # equal to the truth: not a P record
        if any(B.get(u) == O.get(u) == T.get(u) and TR.get(u) != dec.get(u, B.get(u)) for u in units):
            r["unreliable"] = "a unit neither leg touched differs from the truth"
        out.append(r)
    return out


def eval_unit(s):
    """Units travel as repr strings in records; they are tuples of str, int,
    bool and nested tuples, so literal_eval reads them back."""
    import ast
    return ast.literal_eval(s)
