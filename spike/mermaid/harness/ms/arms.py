# SPDX-License-Identifier: MIT
"""§8: Arm 0, M (M-merge, M-PR), P and S, on one opened corpus.

Each arm enumerates case specs from history, evaluates each case (inputs,
exposure, merge, records, X), and returns case dicts ready for the
aggregator. Outputs are redacted (§7.3, private individuals) by `redact`
before they are written anywhere committed.
"""
import collections
import hashlib
import json
import re

from . import case as C
from . import corpus as K
from . import fence as FN
from . import gitops as G
from . import history as HI
from . import replay as RP
from . import sgen as SG
from . import xrun as XR


class Ctx:
    """One opened corpus."""

    def __init__(self, label, stratum_rows, repo_path, pin, status, individual, salt, tmp_root=None):
        self.label, self.pin, self.status = label, pin, status
        self.individual, self.salt = individual, salt
        self.repo = HI.Repo(repo_path)
        self.tmp_root = tmp_root
        self.walked = HI.walk(self.repo, pin)
        self.sel = HI.select(self.repo, pin, self.walked)
        self.selected = self.sel["selected"]
        # §7.5's authors are built from every commit identity in the
        # corpus (merges and pull-request heads included) before any case
        # asks for one, so a later identity cannot re-join an earlier answer.
        self.authors = HI.Authors()
        for ln in self.repo.out("log", "--all", "--format=%an%x09%ae").splitlines():
            n, _, e = ln.partition("\t")
            self.authors.add(n, e)

    def author(self, sha):
        """(author, is a bot) of a commit, or (None, False) for no commit."""
        if sha is None:
            return None, False
        out = self.repo.out("log", "-1", "--format=%an%x09%ae", sha).strip().split("\t")
        n, e = out[0], out[1] if len(out) > 1 else ""
        return self.authors.of(n, e), HI.is_bot(n, e)

    def last_changer(self, base, leg, path):
        """§7.5: the last commit on the leg that changed the path. Never a
        merge commit: the last non-merge commit that changed it, else the
        leg's last non-merge commit, else none."""
        out = self.repo.out("log", "-1", "--no-merges", "--format=%H", "--full-history", f"{base}..{leg}",
                            "--", path).strip()
        if not out:
            out = self.repo.out("log", "-1", "--no-merges", "--format=%H", f"{base}..{leg}").strip()
        return out or None

    def text(self, commit, path):
        b = self.repo.blob_at(commit, path)
        return None if b is None else HI.text_of(self.repo, b)


# ------------------------------------------------------------------ evaluate

def evaluate(ctx, spec, stratum, texts, merge_fn, R, extractor, truth=None):
    """One case. texts: base, o, t (file texts); merge_fn() -> gitops.Merge."""
    case = {"arm": spec["arm"], "corpus": ctx.label, "stratum": stratum, "path": spec["path"],
            "spec": spec, "authors": spec.get("authors", []), "bots": spec.get("bots", 0)}
    if any(t is None for t in texts):
        case.update(excluded="undecodable", decided=False, exposed=False, inputs_in_subset=False,
                    key=None, outcome=None, records=[])
        return case
    prep = C.prepare(stratum, *texts, R)
    case["key"] = prep.get("key")
    case["diff_key"] = prep.get("diff_key")
    case["inputs_in_subset"] = "states" in prep and all(s.status == "in" for s in prep["states"])
    case["exposed"] = bool(prep.get("exposed"))
    case["exposure_reason"] = prep.get("exposure_reason")
    if prep["excluded"] and not prep.get("legs_change"):
        case.update(excluded=prep["excluded"], decided=False, outcome=None, records=[])
        return case
    if prep["excluded"]:
        # A leg that does not change the model: not decided, still merged so
        # an exposed case's outcome is known.
        case["excluded"] = prep["excluded"]
    m = merge_fn()
    res = C.outcome(prep, texts, m, R, path=spec["path"], truth=truth)
    case.update(outcome=res["outcome"], why=res.get("why"), records=res["records"], merge_argv=m.argv)
    if truth is not None and "records_unfiltered" in res:
        case["records_unfiltered"] = res["records_unfiltered"]
    case["decided"] = decided_of(case.get("excluded"), res["outcome"], res["records"])
    if res["outcome"] is not None and extractor:
        merged = C.decode(m.merged) if m.merged is not None else ""
        xo, xf = XR.run_x(extractor, stratum, list(texts) + [merged or ""])
        # X is compared with H's records before P's truth filter (§10.5, §8.3).
        agree, detail = XR.compare(res.get("records_unfiltered", res["records"]), case["exposed"], xo, xf)
        case.update(x_agree=agree, x_detail=detail, x_records=(xo or {}).get("records", []),
                    x_tier_a=sorted(XR.x_tier_a_structure(xo)))
    return case


def decided_of(excluded, outcome, records):
    """§7.5: inputs in the subset and both legs changing the model (not
    excluded), an outcome of E or a merged state in the subset, and no
    UNRELIABLE record."""
    return (not excluded and outcome in ("E", "JUDGED")
            and not any(r.get("unreliable") for r in records))


# --------------------------------------------------------------------- arm M

def arm_m(ctx, R, extractor, prs=None, which=("M-merge", "M-PR")):
    cases, counts = [], {}
    specs = []
    if "M-merge" in which:
        mc, counts["M-merge"] = HI.merge_cases(ctx.repo, ctx.pin, ctx.selected)
        specs += mc
    if "M-PR" in which and prs is not None:
        pc, counts["M-PR"] = HI.pr_cases(ctx.repo, ctx.pin, ctx.selected, prs)
        specs += pc
    merges = {}
    for sp in specs:
        path = sp["path"]
        stratum = ctx.selected[path]
        texts = [ctx.text(sp[k], path) for k in ("base", "o", "t")]
        authors, bots = [], 0
        for leg in ("o", "t"):
            a, bot = ctx.author(ctx.last_changer(sp["base"], sp[leg], path))
            if a is not None:
                authors.append(a)
            bots += bot
        sp = dict(sp, authors=sorted(set(authors)), bots=bots)

        def merge_fn(sp=sp):
            k = (sp["o"], sp["t"])
            if k not in merges:
                paths = sorted({s["path"] for s in specs if (s["o"], s["t"]) == k})
                merges[k] = G.merge_commits(ctx.repo.path, sp["o"], sp["t"], paths, ctx.tmp_root)
            return merges[k][sp["path"]]
        c = evaluate(ctx, sp, stratum, texts, merge_fn, R, extractor)
        if c.get("outcome") in ("JUDGED", "G0", "OUT-OF-SUBSET", "DUP-TITLE", "E") and "merge" in sp:
            rec = ctx.repo.blob_at(sp["merge"], sp["path"])
            mm = merge_fn()
            c["reproduction"] = ("clean" if c["outcome"] != "E" else "E") + (
                ", equals the recorded blob" if mm.merged is not None and rec is not None and
                HI.blob_hash(C.decode(mm.merged) or "") == rec else ", differs from the recorded blob")
        cases.append(c)
    return cases, counts


# --------------------------------------------------------------------- arm P

def arm_p(ctx, R, extractor):
    triples, counts = HI.p_triples(ctx.repo, ctx.selected, ctx.walked[1])
    counts.update({"non-commuting": 0, "constructible": 0})
    cases = []
    for tr in triples:
        path = tr["path"]
        stratum = ctx.selected[path]
        vs = tr["versions"]
        a, b = tr["a"], tr["b"]
        base, o, truth = (HI.text_of(ctx.repo, vs[x][1]) for x in (0, a, a + b))
        if None in (base, o, truth):
            continue
        try:
            t = RP.replay(base, o, truth)
        except RP.NonCommuting as e:
            counts["non-commuting"] += 1
            cases.append({"arm": "P", "corpus": ctx.label, "stratum": stratum, "path": path,
                          "excluded": f"non-commuting: {e}", "decided": False, "key": None, "records": [],
                          "spec": _pspec(tr), "outcome": None})
            continue
        counts["constructible"] += 1
        authors, bots = [], 0
        for sha in (vs[a][0], vs[a + b][0]):
            au, bot = ctx.author(sha)
            authors.append(au)
            bots += bot
        sp = dict(_pspec(tr), arm="P", path=path, authors=sorted(set(authors)), bots=bots)
        c = evaluate(ctx, sp, stratum, [base, o, t],
                     lambda: G.merge_texts(path, base.encode(), o.encode(), t.encode(), ctx.tmp_root),
                     R, extractor, truth=truth)
        c["path_i"] = [path, tr["seg"], tr["i"]]
        c["rank"] = {(1, 1): 0, (1, 3): 1, (3, 1): 2}[(a, b)]
        cases.append(c)
    return cases, counts


def _pspec(tr):
    return {"arm": "P", "path": tr["path"], "seg": tr["seg"], "i": tr["i"], "a": tr["a"], "b": tr["b"],
            "commits": [c for c, _ in tr["versions"]]}


# --------------------------------------------------------------------- arm S

def s_bases(ctxs, R):
    """§8.4: distinct in-subset texts of selected paths, ranked; 100 lowest
    per stratum. R-s-bases: every version of every selected path."""
    seen = {}
    for ctx in ctxs:
        for path, st in ctx.selected.items():
            for seg in HI.segments(ctx.walked[1].get(path, [])):
                for _, blob in seg:
                    if (st, blob) in seen:
                        continue
                    txt = HI.text_of(ctx.repo, blob)
                    if txt is None:
                        continue
                    d, _ = FN.diagram_of(st, txt)
                    if d is None:
                        continue
                    from . import subset as SS
                    if SS.classify(d, R.get(d)).status != "in":
                        continue
                    seen[(st, blob)] = (ctx, path, txt)
    out = {}
    for (st, blob), v in seen.items():
        out.setdefault(st, []).append((SG.rank_key(st, blob), blob, v))
    return {st: sorted(v)[:100] for st, v in out.items()}


def _splice(stratum, file_text, new_diagram):
    if stratum == "F":
        return new_diagram
    body = FN.fences(file_text)[0][0]
    i = file_text.index(body)
    return file_text[:i] + new_diagram + file_text[i + len(body):]


def arm_s(bases, mix, R, extractor, tmp_root=None):
    """§8.4. Returns (cases, rates). Rates are properties of the generator."""
    cases = []
    fails = 0
    for st, items in sorted(bases.items()):
        for _, blob, (ctx, path, txt) in items:
            d, _ = FN.diagram_of(st, txt)
            for k in (1, 3):
                for pair in range(10):
                    legs = []
                    for leg in ("O", "T"):
                        new, ops = SG.leg(d, k, mix, SG.seed_of(st, blob, k, pair, leg))
                        legs.append(None if new is None else _splice(st, txt, new))
                    if None in legs:
                        fails += 1
                        continue
                    sp = {"arm": "S", "path": path, "blob": blob, "k": k, "pair": pair, "authors": []}
                    o, t = legs
                    c = evaluate(ctx, sp, st, [txt, o, t],
                                 lambda o=o, t=t: G.merge_texts(path, txt.encode(), o.encode(), t.encode(),
                                                                tmp_root), R, extractor)
                    cases.append(c)
    rates = {}
    for st in sorted({c["stratum"] for c in cases}):
        cs = [c for c in cases if c["stratum"] == st and c.get("inputs_in_subset")]
        ex = [c for c in cs if c.get("exposed")]
        ida = [c for c in ex if any(r["category"] in ("I1", "I2", "I3", "I4") and r["tier"] == "A"
                                    for r in c["records"])]
        conf = [c for c in ida if any(r["category"] in ("I1", "I2", "I3", "I4") and r["tier"] == "A" and
                                      (r["category"], tuple(sorted(r["objects"]))) in XR.norm_records(
                                          c.get("x_records") or []) for r in c["records"])]
        rates[st] = {"label": "a property of the edit generator (Appendix B.2), not of real editing",
                     "n": len(cs), "exposed": len(ex),
                     "exposed_E": sum(1 for c in ex if c.get("outcome") == "E"),
                     "exposed_B": sum(1 for c in ex if any(r["tier"] == "B" for r in c["records"])),
                     "exposed_A": sum(1 for c in ex if any(r["tier"] == "A" for r in c["records"])),
                     "identity_a": len(ida), "x_confirmed_identity_a": len(conf)}
    rates["generator_failures"] = fails
    return cases, rates


# ---------------------------------------------------------------------- Arm 0

def arm0(ctx, R, prs=None):
    """§8.1 for one corpus, per stratum, from the pin and from inputs only."""
    from . import subset as SS
    out = {}
    pin_tree = {}
    for path, st in ctx.selected.items():
        b = ctx.repo.blob_at(ctx.pin, path)
        if b is not None:
            pin_tree[path] = (st, b)
    for st in ("F", "D"):
        paths = sorted(p for p, s in ctx.selected.items() if s == st)
        blobs = sorted({b for p, (s, b) in pin_tree.items() if s == st})
        stats = collections.Counter()
        refused = collections.Counter()
        kinds = collections.Counter()
        for b in blobs:
            txt = HI.text_of(ctx.repo, b)
            d = FN.diagram_of(st, txt)[0] if txt is not None else None
            if d is None:
                refused["no diagram at the pin"] += 1
                continue
            r = R.get(d)
            s = SS.classify(d, r)
            stats["parses"] += bool(r.get("parse"))
            if s.status == "in":
                stats["in_subset"] += 1
            else:
                refused[s.status + ": " + (s.reason or "")[:120]] += 1
            if s.db is not None:
                db = s.db
                for vid in db.vertices:
                    if vid not in db.node_statements:
                        kinds["implicit nodes"] += 1
                kinds["nodes declared more than once"] += sum(1 for v in db.node_statements.values() if len(v) > 1)
                kinds["edge ids"] += sum(1 for e in db.edges if e["user"])
                kinds["linkStyle edges"] += sum(1 for e in db.edges if e["style"])
                kinds["subgraphs"] += len(db.subgraphs)
                kinds["subgraphs without an explicit id"] += sum(1 for _, ex in db.headers if not ex)
                subs = {sg["id"] for sg in db.subgraphs}
                kinds["nested subgraphs"] += sum(1 for sg in db.subgraphs for n in sg["nodes"] if n in subs)
            if s.status == "duptitle":
                kinds["blobs out of the subset for a repeated untitled title"] += 1
        out[st] = {"selected_paths": len(paths), "distinct_blobs_at_pin": len(blobs),
                   "r_parses": stats["parses"], "in_subset": stats["in_subset"],
                   "coverage": (stats["in_subset"] / len(blobs)) if blobs else None,
                   "refused": dict(sorted(refused.items())), "statement_kinds": dict(sorted(kinds.items()))}
    # M cases and exposure, from inputs only.
    mcases, mcounts = HI.merge_cases(ctx.repo, ctx.pin, ctx.selected)
    pcases, pcounts = HI.pr_cases(ctx.repo, ctx.pin, ctx.selected, prs) if prs is not None else ([], None)
    exposed = collections.Counter()
    onefence = collections.Counter()
    for sp in mcases + pcases:
        st = ctx.selected[sp["path"]]
        texts = [ctx.text(sp[k], sp["path"]) for k in ("base", "o", "t")]
        if None in texts:
            continue
        prep = C.prepare(st, *texts, R)
        if prep["excluded"] and prep["excluded"].startswith("one-fence"):
            onefence[sp["arm"]] += 1
        if prep.get("exposed"):
            exposed[sp["arm"]] += 1
    triples, tcounts = HI.p_triples(ctx.repo, ctx.selected, ctx.walked[1])
    nc = sum(1 for tr in triples if _noncommuting(ctx, tr))
    mix = collections.Counter()
    edits = 0
    for path, st in ctx.selected.items():
        for seg in HI.segments(ctx.walked[1].get(path, [])):
            for (c0, b0), (c1, b1) in zip(seg, seg[1:]):
                t0, t1 = HI.text_of(ctx.repo, b0), HI.text_of(ctx.repo, b1)
                d0 = FN.diagram_of(st, t0)[0] if t0 else None
                d1 = FN.diagram_of(st, t1)[0] if t1 else None
                if d0 is None or d1 is None:
                    continue
                s0, s1 = SS.classify(d0, R.get(d0)), SS.classify(d1, R.get(d1))
                if s0.status == "in" and s1.status == "in" and s0.model != s1.model:
                    edits += 1
                    mix.update(SG.classify_edit(s0.model, s1.model))
    authors = collections.Counter()
    bots = 0
    for path in ctx.selected:
        for c, st_, _ in ctx.walked[1].get(path, []):
            if st_ == "M":
                a, bot = ctx.author(c)
                authors[a] += 1
                bots += bot
    total = sum(authors.values())
    out["history"] = {"M-merge": mcounts, "M-PR": pcounts, "excluded by the one-fence rule": dict(onefence),
                      "exposed M cases": dict(exposed),
                      "P": dict(tcounts, **{"non-commuting": nc, "constructible": len(triples) - nc}),
                      "modifying edits": total, "top author share": (max(authors.values()) / total) if total else None,
                      "bot share": (bots / total) if total else None,
                      "classified edits": edits, "edit mix": dict(sorted(mix.items()))}
    out["selection_excluded"] = dict(collections.Counter(ctx.sel["excluded"].values()))
    return out


def _noncommuting(ctx, tr):
    vs, a, b = tr["versions"], tr["a"], tr["b"]
    t = [HI.text_of(ctx.repo, vs[x][1]) for x in (0, a, a + b)]
    if None in t:
        return True
    try:
        RP.replay(*t)
        return False
    except RP.NonCommuting:
        return True


def frozen_mix(arm0_outputs):
    """§8.4: Arm 0's frozen mix if at least 100 real edits were classified,
    else Appendix B's fixed mix."""
    mix = collections.Counter()
    n = 0
    for o in arm0_outputs:
        h = o.get("history", {})
        n += h.get("classified edits", 0)
        mix.update(h.get("edit mix", {}))
    if n >= 100 and sum(mix.values()):
        return dict(mix), f"Arm 0's frozen mix ({n} classified edits)"
    return dict(SG.FALLBACK_MIX), f"Appendix B's fixed mix ({n} classified edits, fewer than 100)"


# ----------------------------------------------------------------- redaction

def redact(case, ctx_or_meta):
    """§7.3 and the private-individuals rule. Read-only corpus: every id,
    label, title and path segment hashed. Individually owned corpus: commits
    hashed with the salt, path segments and record content hashed (R-redact-
    individual: texts and paths of a private individual's repository are
    treated like a read-only corpus's)."""
    status, individual, salt = ctx_or_meta
    c = json.loads(json.dumps(case, default=str))
    # Authors are union-find roots built from names and emails: never
    # published, for any corpus (R-redact-authors).
    c["authors"] = ["a:" + hashlib.sha256(a.encode()).hexdigest()[:16] for a in c.get("authors") or []]
    if "authors" in c.get("spec", {}):
        c["spec"]["authors"] = c["authors"]
    hide = status == "read-only" or individual
    if individual:
        sp = c.get("spec", {})
        for k in ("merge", "o", "t", "base"):
            if k in sp:
                sp[k] = K.h_commit(salt, sp[k])
        if "commits" in sp:
            sp["commits"] = [K.h_commit(salt, x) for x in sp["commits"]]
        if c.get("merge_argv"):
            c["merge_argv"] = [K.h_commit(salt, x) if re.fullmatch(r"[0-9a-f]{40}", x) else x
                               for x in c["merge_argv"]]
    if hide:
        hp = "/".join(K.h_value(s) for s in c["path"].split("/"))
        c["path"] = hp
        if "spec" in c:
            c["spec"]["path"] = hp
            if "path_i" in c:
                c["path_i"][0] = hp
        for key in ("records", "records_unfiltered", "x_records"):
            for r in c.get(key) or []:
                r["objects"] = [K.h_value(str(o)) for o in r.get("objects") or []]
                for f in ("units", "detail", "lints"):
                    r.pop(f, None)
        c["x_tier_a"] = [[e[0], [K.h_value(str(o)) for o in e[1]]] for e in c.get("x_tier_a") or []]
        for f in ("why", "exposure_reason", "x_detail", "excluded", "merge_argv"):
            if isinstance(c.get(f), str):
                c[f] = "(redacted: " + hashlib.sha256(c[f].encode()).hexdigest()[:16] + ")"
    return c


def redact_arm0(o, meta):
    """Arm 0's refusal reasons quote diagram text (an R message, an H/R
    difference): for a read-only or individually owned corpus each is
    replaced by its status and a hash."""
    status, individual, salt = meta
    if not (status == "read-only" or individual):
        return o
    for st in ("F", "D"):
        if st in o:
            ref = {}
            for k, v in o[st]["refused"].items():
                kk = k.split(":", 1)[0] + ": (redacted " + hashlib.sha256(k.encode()).hexdigest()[:16] + ")"
                ref[kk] = ref.get(kk, 0) + v
            o[st]["refused"] = ref
    return o
