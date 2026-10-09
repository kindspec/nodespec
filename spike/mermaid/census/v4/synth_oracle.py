"""Synthetic check of draft v4's oracle rules on hand-made three-way cases. Not the harness.

usage: python3 -I synth_oracle.py <cases-dir> [<case> ...]

Each case directory holds b.mmd, o.mmd, t.mmd (or a repo r/ with commits titled b, o, t).
The merge is run here, with stock git in a fresh hermetic repository (synthetic texts only).
The model comes from R (rwrap/rmodel.mjs, Mermaid 12.1.0), mapped as Appendix A says:
  - subgraph key: its id, or "title:"+title when R numbered it (header had no explicit id);
  - a vertex whose id is a subgraph id and has no shape is an edge end referring to the subgraph;
  - membership: first subgraph in R's list holding the key.
Oracle (§5): three-way per unit; refusal cases (§5.2) with v4's rule that a membership holder is
not a reference: a membership whose decided holder is decided absent is undecided.
Categories: E, I1, I2, I3, G1, G2, G3, G4; lint L1 (implicit node) for tier B.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_RULE = os.environ.get("OLD_RULE") == "1"  # control: v3 treated a holder as a reference
HOLD = {}
HDR = re.compile(r"^\s*subgraph\s+(.*)$")
EXPL = re.compile(r'^[^\s\[\]"(){}]+\s*(\[.*|\(.*|\{.*)?$')


def R(text):
    r = subprocess.run(["node", os.path.join(HERE, "rwrap", "rmodel.mjs")], input=text, capture_output=True, text=True)
    if r.returncode == 3:
        sys.exit("R aborted: toolchain fault")
    return json.loads(r.stdout)


def model(text):
    d = R(text)
    if not d.get("parse"):
        return None
    # subgraph keys: explicit id vs numbered by R, decided from header form in document order
    hdrs = [m.group(1).strip() for ln in text.splitlines() if (m := HDR.match(ln))]
    auto_ids = set()
    # R numbers only headers without an explicit id; map in closing order is not header order,
    # so decide per subgraph by checking whether its id appears as an explicit header token.
    explicit = {h.split("[")[0].split("(")[0].strip() for h in hdrs if EXPL.match(h) and not h.startswith('"')}
    key = {}
    for s in d["subgraphs"]:
        key[s["id"]] = s["id"] if s["id"] in explicit else "title:" + s["title"]
    if len(set(key.values())) != len(key):
        return "DUP-TITLE"  # two untitled subgraphs share a title: out of the subset
    sub_ids = set(key)
    M = {"exist": {}, "text": {}, "shape": {}, "title": {}, "edge": {}, "hold": {}}
    implicit = set()
    for v in d["vertices"]:
        if v["id"] in sub_ids and v["type"] is None:
            continue  # edge end referring to a subgraph
        M["exist"][v["id"]] = "node"
        M["text"][v["id"]] = v["text"].strip()
        M["shape"][v["id"]] = v["type"] or "none"
        if v["type"] is None:
            implicit.add(v["id"])
    for s in d["subgraphs"]:
        M["exist"][key[s["id"]]] = "subgraph"
        M["title"][key[s["id"]]] = s["title"].strip()
    for s in d["subgraphs"]:
        for n in s["nodes"]:
            k = key.get(n, n)
            M["hold"].setdefault(k, key[s["id"]])
    for e in d["edges"]:
        a, b = key.get(e["start"], e["start"]), key.get(e["end"], e["end"])
        ek = (a, b, e["type"], e["stroke"], e["text"])
        M["edge"][ek] = M["edge"].get(ek, 0) + 1
    M["implicit"] = implicit
    return M


def units(M):
    u = {}
    for k, v in M["exist"].items():
        u[("exist", k)] = v
    for c in ("text", "shape", "title", "hold"):
        for k, v in M[c].items():
            u[(c, k)] = v
    for k, v in M["edge"].items():
        u[("edge", k)] = v
    return u


def refers(unit):
    """Keys a unit refers to as a reference (v4: a membership holder is not a reference)."""
    c, k = unit
    if c == "edge":
        return {k[0], k[1]}
    if OLD_RULE and c == "hold":
        return {HOLD[unit]}  # v3 rule, for the control only: a holder is a reference
    return set()


def keyed(unit):
    c, k = unit
    return k if c != "edge" else None


def oracle(B, O, T):
    ub, uo, ut = units(B), units(O), units(T)
    dec, mc = {}, set()
    for u in set(ub) | set(uo) | set(ut):
        b, o, t = ub.get(u), uo.get(u), ut.get(u)
        if o == t:
            v = o
        elif o == b:
            v = t
        elif t == b:
            v = o
        else:
            mc.add(u)
            continue
        if v is not None:
            dec[u] = v
    present = {k for (c, k) in dec if c == "exist"}
    # membership whose decided holder is decided absent: undecided
    for u in [u for u in dec if u[0] == "hold"]:
        HOLD[u] = dec[u]
        if dec[u] not in present and not OLD_RULE:
            del dec[u]
    # v4.1: a membership unit any of whose B/O/T holder values is decided absent is
    # undecided, and not a model conflict
    if not OLD_RULE and os.environ.get("V40") != "1":  # V40=1: control, the v4.0 rule
        for u in [u for u in mc if u[0] == "hold"]:
            vals = {ub.get(u), uo.get(u), ut.get(u)} - {None}
            if any(v not in present for v in vals):
                mc.discard(u)
        for u in [u for u in dec if u[0] == "hold"]:
            vals = {ub.get(u), uo.get(u), ut.get(u)} - {None}
            if any(v not in present for v in vals):
                del dec[u]
    refusals = []
    for u in dec:
        for k in refers(u):
            if k not in present:
                refusals.append(("dangling", k, u))
    for u in mc:
        if u[0] == "exist" and ub.get(u) is None:
            refusals.append(("collision", u[1], u))
    for k in {k for (c, k) in set(ub) if c == "exist"}:
        for X, Y in ((uo, ut), (ut, uo)):
            if ("exist", k) not in X and any(keyed(u) == k and Y.get(u) != ub.get(u) for u in Y):
                refusals.append(("delete/modify", k, None))
    return dec, mc, refusals


def merge(b, o, t):
    with tempfile.TemporaryDirectory() as d:
        env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "HOME": d, "XDG_CONFIG_HOME": d,
               "PATH": os.environ["PATH"], "GIT_AUTHOR_NAME": "s", "GIT_AUTHOR_EMAIL": "s@s",
               "GIT_COMMITTER_NAME": "s", "GIT_COMMITTER_EMAIL": "s@s"}
        g = lambda *a: subprocess.run(["git", "-C", d, *a], env=env, capture_output=True, text=True)
        g("init", "-q", "-b", "main")
        for name, txt, base in (("b", b, None), ("o", o, "main"), ("t", t, "main")):
            if base:
                g("checkout", "-q", "-B", name, "main")
            open(os.path.join(d, "c.mmd"), "w").write(txt)
            g("add", "c.mmd")
            g("commit", "-q", "-m", name)
        g("checkout", "-q", "t")
        r = g("merge", "-q", "--no-edit", "o")
        m = open(os.path.join(d, "c.mmd")).read()
        unmerged = g("ls-files", "-u").stdout.strip()
        return r.returncode, m, unmerged


def classify(b, o, t):
    rc, m, unmerged = merge(b, o, t)
    if "<<<<<<<" in m or unmerged:
        return "E (conflict)", []
    B, O, T, Mm = model(b), model(o), model(t), model(m)
    if any(X in (None, "DUP-TITLE") for X in (B, O, T)):
        return "excluded (an input is not in the subset)", []
    if Mm is None:
        return "E (merged text does not parse)", []
    if Mm == "DUP-TITLE":
        return "DUP-TITLE (merged state, listed, never decided)", []
    dec, mc, refusals = oracle(B, O, T)
    um = units(Mm)
    recs = []
    for kind, k, u in refusals:
        cat = {"dangling": "I1", "collision": "I2", "delete/modify": "I3"}[kind]
        new_l1 = k in Mm["implicit"] and not any(k in X["implicit"] for X in (B, O, T))
        recs.append((cat, k, "tier B (new L1)" if new_l1 else "tier A"))
    ref_keys = {r[1] for r in refusals}
    for u, v in dec.items():
        if um.get(u) != v and not (set([u[1]]) & ref_keys if u[0] != "edge" else refers(u) & ref_keys):
            cat = {"exist": "G1", "edge": "G2", "hold": "G3", "text": "G4", "title": "G4", "shape": "C"}[u[0]]
            recs.append((cat, u[1], "decided=%r merged=%r" % (v, um.get(u))))
    for u in mc:
        if u[0] == "exist":
            continue  # existence conflicts are refusal cases above
        mv = um.get(u)
        legs = (units(O).get(u), units(T).get(u))
        if mv not in legs:  # eligible MC: merged value is neither leg's value
            grp = {"edge": "G2", "hold": "G3", "text": "G4", "title": "G4", "shape": "C"}[u[0]]
            recs.append(("MC->" + grp, u[1], "legs=%r merged=%r" % (legs, mv)))
    for u in um:
        if u not in dec and u not in mc and u[0] in ("exist", "edge") and not (set([u[1]]) & ref_keys if u[0] != "edge" else refers(u) & ref_keys):
            recs.append(({"exist": "G1", "edge": "G2"}[u[0]], u[1], "present, decided absent"))
    return "clean", recs


def load(cdir):
    if os.path.exists(os.path.join(cdir, "b.mmd")):
        return [open(os.path.join(cdir, f + ".mmd")).read() for f in "bot"]
    r = os.path.join(cdir, "r")
    out = []
    for s in "bot":
        h = subprocess.run(["git", "-C", r, "log", "--all", "--format=%H %s"], capture_output=True, text=True).stdout
        c = [ln.split()[0] for ln in h.splitlines() if ln.split()[1] == s][0]
        out.append(subprocess.run(["git", "-C", r, "show", f"{c}:c.mmd"], capture_output=True, text=True).stdout)
    return out


cases = sys.argv[2:] or sorted(os.listdir(sys.argv[1]))
for c in cases:
    b, o, t = load(os.path.join(sys.argv[1], c))
    status, recs = classify(b, o, t)
    print(f"{c}: {status}; records: {recs if recs else 'none'}")
