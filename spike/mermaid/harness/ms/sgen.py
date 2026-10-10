# SPDX-License-Identifier: MIT
"""Appendix B.2: scripted edits for arm S, and the classification of real
edits into the same operations for Arm 0's edit mix (§8.1).

S's rates are properties of THIS generator (§8.4), never of real editing.
The generator works on diagram lines, using H's parse to know the ids. New
statements go after the last statement of their kind, or inside the target
subgraph's block, so both legs insert at the same place (B.2).

R-sgen: B.2 names the operations, not their exact text. The forms used are
written in each op below; an op that does not apply to a text is redrawn, up
to 20 times, and a leg that still fails is a generator failure, counted.
"""
import hashlib
import random
import re

from . import hparse as H
from . import model as MD

OPS = ("relabel", "add edge", "add node", "delete edge", "rename id", "delete node", "retarget",
       "change membership", "restyle", "change shape", "add subgraph")
FALLBACK_MIX = {"relabel": 20, "add edge": 18, "add node": 15, "delete edge": 8, "rename id": 8,
                "delete node": 7, "retarget": 6, "change membership": 6, "restyle": 5, "change shape": 4,
                "add subgraph": 3}
_EDGE = re.compile(r"(--|==|-\.|~~~)")


def seed_of(stratum, blob_sha, k, pair, leg):
    """§8.4: the first 16 hex digits of sha256(...) as an integer."""
    s = f"nodespec-mermaid:S:{stratum}:{blob_sha}:{k}:{pair}:{leg}"
    return int(hashlib.sha256(s.encode()).hexdigest()[:16], 16)


def rank_key(stratum, blob_sha):
    return hashlib.sha256(f"nodespec-mermaid:S:{stratum}:{blob_sha}".encode()).hexdigest()


def _tok(i):
    return re.compile(r"(?<![A-Za-z0-9_\-.&:#*])" + re.escape(i) + r"(?![A-Za-z0-9_])")


def _nodes(text):
    db = H.parse(text)
    m = MD.from_h(db)
    nodes = sorted(u[1] for u, v in m.items() if u[0] == "exist" and "node" in v)
    return db, m, nodes


def _last(lines, pred):
    idx = [i for i, ln in enumerate(lines) if pred(ln)]
    return idx[-1] if idx else len(lines) - 1


def _indent(lines):
    for ln in lines[1:]:
        if ln.strip():
            return re.match(r"\s*", ln).group(0)
    return "  "


def apply_op(op, text, rng):
    """One edit; returns the new text, or None if the op does not apply."""
    lines = text.split("\n")
    trail = lines[-1] == ""
    if trail:
        lines = lines[:-1]
    db, m, nodes = _nodes(text)
    ind = _indent(lines)
    body = range(1, len(lines))
    new_id = "n" + format(rng.getrandbits(24), "06x")

    def done(ls):
        return "\n".join(ls) + ("\n" if trail else "")
    if op == "add node":
        at = _last(lines, lambda ln: re.search(r"[\[\(\{>]", ln) and not ln.strip().startswith(("%%", "subgraph")))
        lines.insert(at + 1, f"{ind}{new_id}[Node {new_id}]")
        return done(lines)
    if op == "add edge" and len(nodes) >= 2:
        a, b = rng.sample(nodes, 2)
        at = _last(lines, lambda ln: _EDGE.search(ln) is not None)
        lines.insert(at + 1, f"{ind}{a} --> {b}")
        return done(lines)
    if op == "relabel" and nodes:
        n = rng.choice(nodes)
        rx = re.compile(r"(" + _tok(n).pattern + r"\[)([^\]\[\"]*)(\])")
        for i in body:
            if rx.search(lines[i]):
                lines[i] = rx.sub(lambda mm: mm.group(1) + f"Label {new_id}" + mm.group(3), lines[i], count=1)
                return done(lines)
        return None
    if op == "rename id" and nodes:
        n = rng.choice(nodes)
        rx = _tok(n)
        for i in body:
            if not lines[i].lstrip().startswith("%%"):
                lines[i] = rx.sub(new_id, lines[i])
        return done(lines)
    if op == "delete node" and nodes:
        n = rng.choice(nodes)
        rx = _tok(n)
        kept = [lines[0]] + [ln for ln in lines[1:] if not rx.search(ln)]
        return done(kept) if len(kept) < len(lines) else None
    if op == "delete edge":
        idx = [i for i in body if _EDGE.search(lines[i]) and not lines[i].strip().startswith(("%%", "linkStyle"))]
        if not idx:
            return None
        del lines[rng.choice(idx)]
        return done(lines)
    if op == "retarget" and len(nodes) >= 2:
        idx = [i for i in body if _EDGE.search(lines[i]) and not lines[i].strip().startswith("%%")]
        if not idx:
            return None
        i = rng.choice(idx)
        ends = [n for n in nodes if _tok(n).search(lines[i])]
        if not ends:
            return None
        old = ends[-1]
        new = rng.choice([n for n in nodes if n != old])
        ms = list(_tok(old).finditer(lines[i]))
        last = ms[-1]
        lines[i] = lines[i][:last.start()] + new + lines[i][last.end():]
        return done(lines)
    if op == "change membership" and nodes and db.subgraphs:
        n = rng.choice(nodes)
        ends = [i for i, ln in enumerate(lines) if ln.strip() == "end"]
        if not ends:
            return None
        lines.insert(rng.choice(ends), f"{ind}{ind}{n}")
        return done(lines)
    if op == "add subgraph" and nodes:
        n = rng.choice(nodes)
        lines += [f"{ind}subgraph {new_id} [Group {new_id}]", f"{ind}{ind}{n}", f"{ind}end"]
        return done(lines)
    if op == "change shape" and nodes:
        n = rng.choice(nodes)
        rx = re.compile(r"(" + _tok(n).pattern + r")\[([^\]\[\"()]*)\]")
        for i in body:
            if rx.search(lines[i]):
                lines[i] = rx.sub(lambda mm: mm.group(1) + "(" + mm.group(2) + ")", lines[i], count=1)
                return done(lines)
        return None
    if op == "restyle" and nodes:
        n = rng.choice(nodes)
        at = _last(lines, lambda ln: ln.strip().startswith(("style ", "classDef ", "class ")))
        lines.insert(at + 1, f"{ind}style {n} fill:#{rng.getrandbits(24):06x}")
        return done(lines)
    return None


def draw(mix, rng):
    ops = sorted(mix)
    total = sum(mix[o] for o in ops)
    x = rng.random() * total
    for o in ops:
        x -= mix[o]
        if x < 0:
            return o
    return ops[-1]


def leg(text, k, mix, seed):
    """k edits drawn from mix with random.Random(seed). Returns (text, ops) or
    (None, why)."""
    rng = random.Random(seed)
    ops = []
    for _ in range(k):
        for _try in range(20):
            op = draw(mix, rng)
            try:
                new = apply_op(op, text, rng)
            except (H.Refuse, MD.OutOfSubset):
                new = None
            if new is not None and new != text:
                text = new
                ops.append(op)
                break
        else:
            return None, "no op applied in 20 draws"
    return text, ops


# ------------------------------------------------------- Arm 0's edit mix

def classify_edit(B, A):
    """A real modifying edit's model diff, as Appendix B's operations (a
    multiset). R-mix: a node removed and one added with the same label is a
    rename; an edge removed and one added sharing one end is a retarget."""
    out = []
    nodes = lambda M: {u[1] for u, v in M.items() if u[0] == "exist" and "node" in v}
    subs = lambda M: {u[1] for u, v in M.items() if u[0] == "exist" and "subgraph" in v}
    nb, na = nodes(B), nodes(A)
    gone, new = sorted(nb - na), sorted(na - nb)
    for g in list(gone):
        lab = B.get(("ntext", g))
        twin = next((n for n in new if A.get(("ntext", n)) == lab and lab not in (g, None)), None)
        if twin:
            out.append("rename id")
            gone.remove(g)
            new.remove(twin)
    out += ["delete node"] * len(gone) + ["add node"] * len(new)
    out += ["add subgraph"] * len(subs(A) - subs(B))
    for k in sorted(nb & na):
        if B.get(("ntext", k)) != A.get(("ntext", k)):
            out.append("relabel")
        if B.get(("shape", k)) != A.get(("shape", k)):
            out.append("change shape")
        if B.get(("nhold", k)) != A.get(("nhold", k)):
            out.append("change membership")
    edges = lambda M: {(u[1][0], u[1][1]) for u, v in M.items() if u[0] == "ecount" for _ in range(v)} | \
        {v[:2] for u, v in M.items() if u[0] == "eref"}
    eb, ea = edges(B), edges(A)
    rem, add = sorted(eb - ea), sorted(ea - eb)
    for r in list(rem):
        tw = next((x for x in add if (x[0] == r[0]) != (x[1] == r[1])), None)
        if tw:
            out.append("retarget")
            rem.remove(r)
            add.remove(tw)
    out += ["delete edge"] * len(rem) + ["add edge"] * len(add)
    if any(B.get(u) != A.get(u) for u in set(B) | set(A) if MD.CLASS_OF[u[0]] == "style"):
        out.append("restyle")
    return out
