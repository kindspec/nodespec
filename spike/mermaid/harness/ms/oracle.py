# SPDX-License-Identifier: MIT
"""The oracle (PRE-REGISTRATION.md §5), Appendix C's lints, and §5.5's
exposure. Pure functions of models; nothing here reads a merge result except
`judge`, and `exposure` takes the three inputs only.

Each reading this module takes where §5 does not settle a detail is named
R-<tag> in a comment and listed in the harness README under "Readings".
"""
from .model import CLASS_OF

NONE = None
_KEYED = {"exist", "ntext", "stitle", "etext", "link", "shape", "nhold", "shold", "eref", "styles"}
A_CATS = {"I1", "I2", "I3", "I4", "G1", "G2", "G3", "G4"}
MC_GROUP = {"relation": "G2", "membership": "G3", "text": "G4", "shape": "C", "style": "D"}


# ------------------------------------------------------------ units and keys

def keyed_by(u):
    """§4.2: the key a unit is keyed by, or None."""
    p = u[0]
    if p in _KEYED:
        return u[1]
    if p == "class":
        return u[1][0]
    if p == "estyle" and isinstance(u[1], str):
        return u[1]
    return None


def value_refs(u, v):
    """§4.2: the keys a unit holds as a value: an edge's ends. A
    membership's holder is not a reference (§4.2)."""
    p = u[0]
    if p in ("ecount",) or (p == "estyle" and isinstance(u[1], tuple)):
        return {u[1][0], u[1][1]}
    if p == "eref" and v is not None:
        return {v[0], v[1]}
    return set()


def refers(u, v):
    """§4.2: keys a unit refers to: keyed by, or held as a value."""
    k = keyed_by(u)
    return ({k} if k is not None else set()) | value_refs(u, v)


def unit_keys(u, v):
    """Every key of a unit (§5.3, I1's objects)."""
    return refers(u, v)


def present_keys(m):
    return {u[1] for u in m if u[0] == "exist"}


# ------------------------------------------------------------------ deciding

def decide(B, O, T):
    """§5.1: (decided {unit: value or None}, model conflicts {unit}, undecided
    memberships {unit}). The order unit is decided like any other."""
    dec, mc = {}, set()
    for u in set(B) | set(O) | set(T):
        b, o, t = B.get(u), O.get(u), T.get(u)
        if o == t:
            dec[u] = o
        elif o == b:
            dec[u] = t
        elif t == b:
            dec[u] = o
        else:
            mc.add(u)
    absent = {u[1] for u, v in dec.items() if u[0] == "exist" and v is None}
    undecided = set()
    # §4.2: a membership is undecided, not a conflict, when its decided
    # holder or any of its holder values in B, O or T is decided absent.
    for u in [u for u in set(dec) | mc if u[0] in ("nhold", "shold")]:
        vals = {B.get(u), O.get(u), T.get(u)}
        if u in dec:
            vals.add(dec[u])
        if any(v and v in absent for v in vals):
            undecided.add(u)
            dec.pop(u, None)
            mc.discard(u)
    return dec, mc, undecided


def refusals(B, O, T, dec, mc):
    """§5.2: [(kind, key, [units])]."""
    absent = {u[1] for u, v in dec.items() if u[0] == "exist" and v is None}
    out = []
    dang = {}
    for u, v in dec.items():
        if v is None or u[0] == "order":
            continue
        for k in refers(u, v):
            if k in absent:
                dang.setdefault(k, []).append(u)
    for k, us in sorted(dang.items()):
        out.append(("dangling", k, sorted(us, key=repr)))
    keysB, keysO, keysT = present_keys(B), present_keys(O), present_keys(T)
    for k in sorted((keysO & keysT) - keysB):
        diff = [u for u in set(O) | set(T) if keyed_by(u) == k and O.get(u) != T.get(u)]
        if diff:
            out.append(("collision", k, sorted(diff, key=repr)))
    for k in sorted(keysB):
        for X, Y in ((O, T), (T, O)):
            if k in present_keys(X):
                continue
            # R-delmod: "changes a unit keyed by it" -- the other leg holds the
            # unit with a value other than the base's (an add or a change). A
            # removal on the other leg agrees with the delete and is not a
            # change (census/v4/synth_oracle.py reads it the same way).
            ch = [u for u in Y if keyed_by(u) == k and Y.get(u) != B.get(u)]
            if ch:
                out.append(("delete/modify", k, sorted(ch, key=repr)))
                break
    return out


def exposure(B, O, T):
    """§5.5, from B, O and T only: (exposed, reason)."""
    keysB = present_keys(B)
    for X, Y, leg in ((O, T, "O"), (T, O, "T")):
        removed = keysB - present_keys(X)
        for u, v in Y.items():
            if u[0] == "order" or v is None or v == B.get(u):
                continue
            hit = refers(u, v) & removed
            if hit:
                return True, f"leg {'T' if leg == 'O' else 'O'} adds or changes {u!r}, which refers to " \
                              f"{sorted(hit)[0]!r}, removed by leg {leg}"
    for k in sorted((present_keys(O) & present_keys(T)) - keysB):
        if any(keyed_by(u) == k and O.get(u) != T.get(u) for u in set(O) | set(T)):
            return True, f"both legs add {k!r} with a differing unit"
    return False, None


# ---------------------------------------------------------------------- lints

def lint_failures(model, db, stratum=None, fence_ok=True, path=None):
    """Appendix C on one state: {(lint, object)}. db is H's parse of the
    state's diagram (None for a merged file whose diagram is not judged)."""
    out = set()
    if stratum == "D" and not fence_ok:
        out.add(("L6", "path:" + (path or "")))
    if model is None or db is None:
        return out
    nodes = {u[1] for u, v in model.items() if u[0] == "exist" and "node" in v}
    for k in nodes:
        if k not in db.node_statements:
            out.add(("L1", k))
        sts = db.node_statements.get(k, [])
        if len({lab for lab, _ in sts if lab is not None}) > 1 or len({s for _, s in sts if s is not None}) > 1:
            out.add(("L2", k))
    held = {}
    for _, ids in db.block_mentions:
        for i in ids:
            if i in nodes:
                held[i] = held.get(i, 0) + 1
    for i, n in held.items():
        if n > 1:
            out.add(("L3", i))  # R-L3: mentioned directly in two blocks
    for u, v in model.items():
        if u[0] == "exist" and len(v) > 1:
            out.add(("L4", u[1]))
    for i in db.swallowed:
        out.add(("L4", i))
    # R-L5: a duplicate edge's failing objects are its two ends (and its id).
    for u, v in model.items():
        if u[0] == "ecount" and v > 1:
            out.add(("L5", u[1][0]))
            out.add(("L5", u[1][1]))
    for eid, n in db.edge_id_attempts.items():
        if n > 1:
            out.add(("L5", eid))
            for e in db.edges:
                if e["want_id"] == eid:
                    out.add(("L5", e["start"]))
                    out.add(("L5", e["end"]))
    return out


# ------------------------------------------------------------------- judging

def _edge_objs(u, v):
    if u[0] == "ecount" or (u[0] == "estyle" and isinstance(u[1], tuple)):
        return {u[1][0], u[1][1]}
    e = keyed_by(u)
    objs = {e} if e is not None else set()
    if v is not None and u[0] == "eref":
        objs |= {v[0], v[1]}
    return objs


def _rec(cat, objs, tier, units, detail):
    return {"category": cat, "objects": sorted(o for o in objs if o), "tier": tier,
            "units": [repr(u) for u in units], "detail": detail}


def judge(B, O, T, M, lint_new):
    """§5.3-§5.4 on a merged state in the subset. lint_new: the set of
    (lint, object) failures of M absent from all three inputs. Returns
    (records, decided, mc). Every record carries category, objects, tier."""
    dec, mc, undecided = decide(B, O, T)
    recs = []
    ident = set()
    names = {"dangling": "I1", "collision": "I2", "delete/modify": "I3"}
    for kind, k, us in refusals(B, O, T, dec, mc):
        if kind == "dangling":
            objs = {k}
            for u in us:
                objs |= unit_keys(u, dec.get(u))
        else:
            objs = {k}
        recs.append(_rec(names[kind], objs, "A", [("exist", k)] + us, kind))
        ident.add(k)
    # I4: a kind clash the merge introduced.
    for k in sorted({u[1] for u in set(B) | set(O) | set(T) | set(M) if u[0] == "exist"}):
        u = ("exist", k)
        if any(len(X.get(u) or ()) > 1 for X in (B, O, T)):
            continue
        mk = M.get(u)
        d = dec.get(u) if u in dec else "MC"
        if (mk and len(mk) > 1) or (mk and d not in (None, "MC") and mk != d):
            recs.append(_rec("I4", {k}, "A", [u], f"merged kinds {mk}, decided {d}"))
            ident.add(k)

    def related(u, v):
        return bool(refers(u, v) & ident)

    for u in sorted(set(dec) | set(M), key=repr):
        if u in mc or u in undecided:
            continue
        d, m = dec.get(u), M.get(u)
        if d == m:
            continue
        p = u[0]
        if p == "order":
            recs.append(_rec("S-ORDER", set(), "-", [u], "statement order"))
            continue
        if related(u, d) or related(u, m):
            continue  # R-ident: an identity record's consequences are not structure records
        if p == "exist":
            kinds = set(d or ()) | set(m or ())
            if "node" in kinds and "node" in set(d or ()) ^ set(m or ()):
                recs.append(_rec("G1", {u[1]}, "A", [u], f"decided {d}, merged {m}"))
            if "edge" in kinds and "edge" in set(d or ()) ^ set(m or ()):
                ref = ("eref", u[1])
                recs.append(_rec("G2", _edge_objs(ref, dec.get(ref) or M.get(ref)) | {u[1]}, "A", [u],
                                 "lost" if d else "extra"))
            continue  # R-subgraph: a subgraph's existence shows as G4 on its title
        if p in ("eref", "ecount"):
            if p == "ecount":
                dd, mm = d or 0, m or 0
                recs.append(_rec("G2", _edge_objs(u, d), "A", [u],
                                 f"lost {dd - mm}" if mm < dd else f"extra {mm - dd}"))
            elif d is not None and m is not None:
                recs.append(_rec("G2", _edge_objs(u, d) | _edge_objs(u, m), "A", [u], f"ends {d} -> {m}"))
            continue
        if p in ("nhold", "shold"):
            recs.append(_rec("G3", {u[1], d, m}, "A", [u], f"holder {d!r} -> {m!r}"))
        elif p in ("ntext", "stitle", "link", "etext"):
            recs.append(_rec("G4", {u[1]}, "A", [u], f"{d!r} -> {m!r}"))
        elif p == "shape":
            recs.append(_rec("C", {u[1]}, "C", [u], f"{d!r} -> {m!r}"))
        elif p == "estyle":
            recs.append(_rec("S-LINKSTYLE", _edge_objs(u, d), "D", [u], f"{d!r} -> {m!r}"))
        elif p == "classdef":
            recs.append(_rec("D", {"classdef:" + u[1]}, "D", [u], f"{d!r} -> {m!r}"))
        elif p in ("class", "styles"):
            recs.append(_rec("D", {keyed_by(u)}, "D", [u], f"{d!r} -> {m!r}"))
    for u in sorted(mc, key=repr):
        m = M.get(u)
        legs = (O.get(u), T.get(u))
        if u[0] == "exist" or related(u, m) or related(u, O.get(u)) or related(u, T.get(u)):
            continue
        cls = CLASS_OF[u[0]]
        if cls == "order":
            if m not in legs:
                recs.append(_rec("S-ORDER", set(), "-", [u], "statement order (conflict)"))
            continue
        if m in legs:
            recs.append(_rec("MC-ineligible", set(), "-", [u], "merged value is a leg's"))
            continue
        grp = MC_GROUP[cls]
        if grp == "G3":
            objs = {u[1], m} | {x for x in legs if x}
        elif grp == "G2":
            objs = _edge_objs(u, m)
        else:
            objs = {keyed_by(u) or ("classdef:" + u[1] if u[0] == "classdef" else None)}
        tier = {"G2": "A", "G3": "A", "G4": "A", "C": "C", "D": "D"}[grp]
        recs.append(_rec("MC", objs, tier, [u], f"group {grp}; legs {legs!r}, merged {m!r}"))
        recs[-1]["group"] = grp
    # §5.4: an A record one of whose objects newly fails a lint is tier B.
    failing = {o for _, o in lint_new}
    for r in recs:
        if r["tier"] == "A" and failing & set(r["objects"]):
            r["tier"] = "B"
            r["lints"] = sorted(f"{l}:{o}" for l, o in lint_new if o in r["objects"])
    return recs, dec, mc
