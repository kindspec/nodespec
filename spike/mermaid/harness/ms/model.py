# SPDX-License-Identifier: MIT
"""The model (PRE-REGISTRATION.md §4.1, §4.2, Appendix A), mapped the same way
from R's output and from H's parse, and the subset test (§4.3).

A model is a dict {unit: value}. Every unit is a tuple whose first element
names its property; the property fixes its class (§4.1):

  ("exist", k)            identity    sorted tuple of k's kinds
  ("ntext", k)            text        a node's label, outer whitespace trimmed
  ("stitle", k)           text        a subgraph's title, trimmed
  ("etext", e)            text        a user-id edge's label, exact
  ("link", k)             text        a node's click target (link, target)
  ("shape", k)            shape       a node's shape, or "none"
  ("nhold", k)            membership  a node's holder key, or "" for none
  ("shold", k)            membership  a subgraph's holder key, or ""
  ("eref", e)             relation    a user-id edge's (from, to, kind)
  ("ecount", (f, t, kind, label))  relation  count of edges with no user id
  ("class", (k, c))       style       a class assignment
  ("styles", k)           style       a node's `style` list
  ("classdef", c)         style       a class definition's styles
  ("estyle", edge key)    style       linkStyle styles of the edge(s) so keyed
  ("order",)              order       (node keys, edge keys), in R's order

Keys are strings: a node id, an explicit subgraph id, "title:" + title for a
subgraph Mermaid numbers itself, or a user-defined edge id. Edge kinds are
normalized (Appendix A): "<line>:<head at start>><head at end>", extra length
dropped.
"""
import re

CLASS_OF = {"exist": "identity", "ntext": "text", "stitle": "text", "etext": "text", "link": "text",
            "shape": "shape", "nhold": "membership", "shold": "membership", "eref": "relation",
            "ecount": "relation", "class": "style", "styles": "style", "classdef": "style",
            "estyle": "style", "order": "order"}

_LINE = {"normal": "solid", "thick": "thick", "dotted": "dotted", "invisible": "invisible"}
_HEADS = {"arrow_open": ("none", "none"), "arrow_point": ("none", "arrow"),
          "arrow_circle": ("none", "circle"), "arrow_cross": ("none", "cross"),
          "double_arrow_point": ("arrow", "arrow"), "double_arrow_circle": ("circle", "circle"),
          "double_arrow_cross": ("cross", "cross")}
_AUTO = re.compile(r"subGraph\d+")


class OutOfSubset(Exception):
    """args[0]: the reason, counted by Arm 0."""


class DupTitle(OutOfSubset):
    """Two subgraphs Mermaid numbers itself share a title (§4.1, §5.3)."""


def edge_kind(etype, stroke):
    if etype not in _HEADS or stroke not in _LINE:
        raise OutOfSubset(f"edge kind {etype}/{stroke}")
    a, b = _HEADS[etype]
    return f"{_LINE[stroke]}:{a}>{b}"


def build(raw, explicit_ids, node_statement_ids):
    """raw: {"vertices": [...], "edges": [...], "subgraphs": [...],
    "classdefs": {name: [styles]}} in R's field names. explicit_ids: the
    subgraph ids whose header gave an id. node_statement_ids: the ids with a
    node statement (Appendix A: a vertex named by a subgraph id with no node
    statement is an edge end referring to the subgraph)."""
    M = {}
    subs = raw["subgraphs"]
    skey = {}
    for s in subs:
        if s["id"] in explicit_ids:
            skey[s["id"]] = s["id"]
        else:
            skey[s["id"]] = "title:" + s["title"]
    keys = list(skey.values())
    if len(set(keys)) != len(keys):
        dup = [k for k in keys if keys.count(k) > 1]
        if all(k.startswith("title:") for k in dup):
            raise DupTitle("two untitled subgraphs share a title")
        raise OutOfSubset("two subgraphs with one key")
    vkey = {}
    kinds = {}
    for v in raw["vertices"]:
        vid = v["id"]
        if vid in skey and vid not in node_statement_ids:
            continue  # an edge end that refers to the subgraph
        vkey[vid] = vid
        kinds.setdefault(vid, set()).add("node")
    for s in subs:
        kinds.setdefault(skey[s["id"]], set()).add("subgraph")

    def end(x):
        if x in vkey:
            return x
        if x in skey:
            return skey[x]
        raise OutOfSubset("an edge end that names no node or subgraph (an edge id)")

    ekeys = []
    for e in raw["edges"]:
        f, t, kind = end(e["start"]), end(e["end"]), edge_kind(e["type"], e["stroke"])
        if e["user"]:
            k = e["id"]
            kinds.setdefault(k, set()).add("edge")
            M[("eref", k)] = (f, t, kind)
            if e["text"]:
                M[("etext", k)] = e["text"]
        else:
            k = (f, t, kind, e["text"])
            M[("ecount", k)] = M.get(("ecount", k), 0) + 1
        ekeys.append(k)
        if e.get("style"):
            M.setdefault(("estyle", k), []).append(tuple(e["style"]))
    for u in [u for u in M if u[0] == "estyle"]:
        M[u] = tuple(sorted(M[u]))
    for k, ks in kinds.items():
        M[("exist", k)] = tuple(sorted(ks))
    for v in raw["vertices"]:
        vid = v["id"]
        if vid not in vkey:
            continue
        M[("ntext", vid)] = (v["text"] if v["text"] is not None else vid).strip()
        M[("shape", vid)] = v["type"] or "none"
        if v.get("link") is not None:
            M[("link", vid)] = (v["link"], v.get("linkTarget"))
        for c in v["classes"]:
            if c != "clickable":
                M[("class", (vid, c))] = True
        if v["styles"]:
            M[("styles", vid)] = tuple(v["styles"])
    for s in subs:
        M[("stitle", skey[s["id"]])] = s["title"].strip()
    holder = {}
    for s in subs:  # R's list is in closing order: the first to close holds it
        for n in s["nodes"]:
            k = vkey.get(n) or skey.get(n)
            if k is not None:
                holder.setdefault(k, skey[s["id"]])
    for k, ks in kinds.items():
        if "node" in ks:
            M[("nhold", k)] = holder.get(k, "")
        if "subgraph" in ks:
            M[("shold", k)] = holder.get(k, "")
    for c, st in raw["classdefs"].items():
        M[("classdef", c)] = tuple(st)
    M[("order",)] = (tuple(vkey), tuple(ekeys))
    return M


# ---------------------------------------------------------------- from R

def raw_from_r(r):
    """R's JSON (r/rmodel.mjs) as a raw model. Appendix A's out-of-subset
    forms that only R's output shows are refused here: icon and image nodes."""
    if not r.get("flowchart"):
        raise OutOfSubset("not a flowchart")
    vs = []
    for v in r["vertices"]:
        if v.get("icon") is not None or v.get("img") is not None:
            raise OutOfSubset("icon or image node")
        vs.append({"id": v["id"], "text": v["text"], "type": v["type"], "classes": v["classes"],
                   "styles": v["styles"], "link": v["link"], "linkTarget": v["linkTarget"]})
    es = [{"id": e["id"], "user": e["isUserDefinedId"], "start": e["start"], "end": e["end"],
           "type": e["type"], "stroke": e["stroke"], "text": e["text"], "style": e["style"]}
          for e in r["edges"]]
    return {"vertices": vs, "edges": es, "subgraphs": r["subgraphs"],
            "classdefs": {c["id"]: c["styles"] for c in r["classDefs"]}}


def from_r(r):
    """Appendix A's model from R. A subgraph id Mermaid numbered itself is
    `subGraphN`; H refuses an explicit id of that form, so here it marks a
    header without an id. A vertex with no type stands for no node statement
    (H decides that from the text, and V1 compares the two)."""
    raw = raw_from_r(r)
    explicit = {s["id"] for s in raw["subgraphs"] if not _AUTO.fullmatch(s["id"])}
    stmt = {v["id"] for v in raw["vertices"] if v["type"] is not None}
    return build(raw, explicit, stmt)


# ---------------------------------------------------------------- from H

def raw_from_h(db):
    vs = [dict(v) for v in db.vertices.values()]
    es = [dict(e) for e in db.edges]
    return {"vertices": vs, "edges": es, "subgraphs": [dict(s, nodes=list(s["nodes"])) for s in db.subgraphs],
            "classdefs": {k: list(v) for k, v in db.classdefs.items()}}


def from_h(db):
    for eid in db.edge_id_uses:
        for e in db.edges:
            if eid in (e["start"], e["end"]) and eid not in db.vertices:
                raise OutOfSubset("an edge end that names a user-defined edge id")
    explicit = {sid for sid, ex in db.headers if ex}
    return build(raw_from_h(db), explicit, set(db.node_statements))


def describe_diff(a, b, limit=3):
    out = []
    for u in sorted(set(a) | set(b), key=repr):
        if a.get(u) != b.get(u):
            out.append(f"{u!r}: H={a.get(u)!r} R={b.get(u)!r}")
            if len(out) >= limit:
                break
    return out
