# SPDX-License-Identifier: Apache-2.0 OR MIT
"""SPEC.md draft 0, as a checker: `check(data)` returns the refusals that apply.

The work is in three passes, in the order SPEC.md §9's applicability rule sets:

1. the whole file (§3): `bad-encoding` and `lone-cr` stop everything, and
   `leading-bom` is reported and the mark set aside;
2. each line on its own (§4.2 to §4.10): a line is either refused, and then
   contributes nothing else, or it is a statement that declares and names;
3. the file rules (§4.6, §5 to §7), over the statements of lines that were not
   refused.
"""

import re
from dataclasses import dataclass, field

from . import grammar as g

#: §9's identifiers, in its order. The order is not a precedence.
IDENTIFIERS = (
    "bad-encoding",
    "leading-bom",
    "lone-cr",
    "conflict-marker",
    "no-header",
    "malformed-line",
    "not-admitted",
    "reserved-id",
    "stray-direction",
    "subgraph-without-id",
    "declaration-in-edge",
    "duplicate-declaration",
    "undeclared-id",
    "wrong-kind",
    "kind-clash",
    "edge-id-on-group",
    "duplicate-edge",
    "too-many-edges",
    "declaration-in-block",
    "statement-in-block",
    "nested-block",
    "unbalanced-block",
    "member-twice",
    "membership-cycle",
    "direction-outside-block",
    "direction-twice",
    "link-style",
    "class-not-last",
    "styled-twice",
)

#: §9: the entries that are about an id, and are reported with one.
ID_ENTRIES = frozenset(
    {
        "reserved-id",
        "duplicate-declaration",
        "undeclared-id",
        "wrong-kind",
        "kind-clash",
        "edge-id-on-group",
        "member-twice",
        "membership-cycle",
        "styled-twice",
    }
)

#: §4.6: Mermaid's default edge limit, which the profile keeps.
MAX_EDGES = 500

NODE, SUBGRAPH, EDGE, CLASS = "node", "subgraph", "edge", "class"


@dataclass(frozen=True)
class Finding:
    """One refusal: its §9 identifier, the id it concerns where §9 gives one,
    and a message that names entities, never offsets."""

    identifier: str
    id: str | None
    message: str

    def __str__(self):
        return f"{self.message} [{self.identifier}]"


# --- §4.4: reserved ids --------------------------------------------------------

_RESERVED = g.KEYWORDS | {"hasOwnProperty", "direction"}
_EDGE_ID_FORM = re.compile(r"L_[A-Za-z0-9_]+_[A-Za-z0-9_]+_[0-9]+")


def is_reserved(i):
    return i in _RESERVED or _EDGE_ID_FORM.fullmatch(i) is not None


# --- §4.9: stray-direction -----------------------------------------------------

# What Mermaid's lexer counts as whitespace (§4.9).
_MWS = "\t\n\x0b\x0c\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008"
_MWS += "\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
_STRAY = re.compile("direction[" + _MWS + "]+(?:TB|BT|RL|LR|TD)")


def is_stray_direction(line):
    return _STRAY.search(line) is not None or line.rstrip(_MWS).endswith("direction")


# --- messages ------------------------------------------------------------------


def _show(line, limit=60):
    out = []
    for c in line:
        o = ord(c)
        if c == "`":
            out.append("\\`")
        elif o < 0x20 or o == 0x7F or 0x80 <= o < 0xA0 or c in "\u2028\u2029\ufeff":
            out.append(f"\\u{o:04x}")
        else:
            out.append(c)
    s = "".join(out)
    if len(s) > limit:
        s = s[: limit - 1] + "…"
    return f"`{s}`"


# --- what a line contributes -----------------------------------------------------


@dataclass
class Stmt:
    """A statement line that no line rule refused."""

    kind: str  # node subgraph end member direction edge classdef class style
    decls: list = field(default_factory=list)  # (id, kind)
    names: list = field(default_factory=list)  # (id, allowed kinds, place)
    edges: list = field(default_factory=list)  # (start, end, link, label, edge id)
    member: str | None = None
    holder: str | None = None
    targets: tuple = ()  # of a style or a class line
    edge: g.Edge | None = None


@dataclass
class _Block:
    id: str
    direction: bool = False


_NODE_OR_SUBGRAPH = frozenset({NODE, SUBGRAPH})
_CLASS_TARGET = frozenset({NODE, SUBGRAPH, EDGE})
_CLASS_ONLY = frozenset({CLASS})


def _first_word(line):
    s = line.lstrip(g.WSP_CHARS)
    for i, c in enumerate(s):
        if c in g.WSP_CHARS:
            return s[:i]
    return s


_ACC = re.compile(r"[ \t]*(?:accTitle[ \t]*:|accDescr[ \t]*[:{])")


def _edge_stmt(e):
    """The Stmt of an edge statement that matched `edge-stmt` (§4.6)."""
    st = Stmt("edge", edge=e)
    for grp in e.groups:
        for i in grp:
            st.names.append((i, _NODE_OR_SUBGRAPH, "an edge"))
    for k, ln in enumerate(e.links):
        if ln.edge_id is not None:
            st.decls.append((ln.edge_id, EDGE))
        label = None if ln.label is None else ln.label.strip(g.WSP_CHARS)
        for a in e.groups[k]:
            for b in e.groups[k + 1]:
                st.edges.append((a, b, ln.link, label, ln.edge_id))
    return st


def _ids_in(st):
    """Every id that stands in a statement, in order, for reserved-id (§4.4)."""
    return list(dict.fromkeys([i for i, _ in st.decls] + [i for i, _, _ in st.names]))


def _classify(line, block):
    """§4.3's rules for a statement line after the header.

    Returns (Stmt, None) for a statement, or (None, (identifier, message)).
    """
    fw = _first_word(line)
    shown = _show(line.strip(g.WSP_CHARS))
    # 1. subgraph
    if fw == "subgraph":
        if block is not None:
            return None, ("nested-block", f"the subgraph line {shown} stands inside a block")
        sid = g.subgraph_line(line)
        if sid is not None:
            st = Stmt("subgraph", decls=[(sid, SUBGRAPH)])
            return st, None
        if g.is_subgraph_without_id(line):
            return None, ("subgraph-without-id", f"the subgraph line {shown} has no explicit id")
        return None, ("malformed-line", f"the subgraph line {shown} is not well formed")
    # 2. end
    if fw == "end":
        if g.is_end_line(line):
            if block is None:
                return None, ("unbalanced-block", "an `end` closes no open block")
            return Stmt("end"), None
        return None, ("malformed-line", f"the line {shown} is not `end` alone")
    # 3. direction
    if fw == "direction":
        if g.is_direction_stmt(line):
            if block is None:
                return None, (
                    "direction-outside-block",
                    f"the direction statement {shown} stands at the top level",
                )
            if block.direction:
                return None, (
                    "direction-twice",
                    f"the block `{block.id}` holds a second direction statement",
                )
            return Stmt("direction"), None
        return None, ("malformed-line", f"the line {shown} is not a direction statement")
    # 4. classDef, class, style
    if fw in ("classDef", "class", "style"):
        if block is not None:
            return None, (
                "statement-in-block",
                f"the `{fw}` statement {shown} stands inside the block `{block.id}`",
            )
        if fw == "classDef":
            cid = g.classdef_stmt(line)
            if cid is not None:
                return Stmt("classdef", decls=[(cid, CLASS)]), None
        elif fw == "class":
            c = g.class_stmt(line)
            if c is not None:
                targets, cls = c
                st = Stmt("class", targets=targets)
                st.names = [(t, _CLASS_TARGET, "a class line's target") for t in targets]
                st.names.append((cls, _CLASS_ONLY, "a class line's class"))
                return st, None
        else:
            sid = g.style_stmt(line)
            if sid is not None:
                st = Stmt("style", targets=(sid,))
                st.names = [(sid, _NODE_OR_SUBGRAPH, "a style line")]
                return st, None
        return None, ("malformed-line", f"the `{fw}` line {shown} is not well formed")
    # 5. linkStyle
    if fw == "linkStyle":
        return None, ("link-style", f"the line {shown} is a linkStyle")
    # 6. click, accTitle, accDescr
    if fw == "click" or _ACC.match(line):
        return None, ("not-admitted", f"the line {shown} is not admitted")
    # 7. node statement
    n = g.node_stmt(line)
    if n is not None:
        if block is not None:
            return None, (
                "declaration-in-block",
                f"the node `{n.id}` is declared inside the block `{block.id}`",
            )
        return Stmt("node", decls=[(n.id, NODE)]), None
    # 8. edge statement
    e = g.edge(line)
    if e is not None:
        if block is not None:
            return None, (
                "statement-in-block",
                f"the edge statement {shown} stands inside the block `{block.id}`",
            )
        return _edge_stmt(e), None
    # 9. edge-decl
    e = g.edge(line, shapes=True)
    if e is not None:
        if block is not None:
            return None, (
                "statement-in-block",
                f"the edge statement {shown} stands inside the block `{block.id}`",
            )
        return None, ("declaration-in-edge", f"the edge statement {shown} declares a node")
    # 10. member line
    m = g.member_line(line)
    if m is not None:
        if block is not None:
            st = Stmt("member", member=m, holder=block.id)
            st.names = [(m, _NODE_OR_SUBGRAPH, "a member line")]
            return st, None
        return None, ("malformed-line", f"the bare id `{m}` stands at the top level")
    # 11. a Markdown string (`:::` and `@{` were refused by §4.2 rule 3)
    if '"`' in line:
        return None, ("not-admitted", f"the line {shown} is not admitted")
    # 12.
    return None, ("malformed-line", f"the line {shown} matches no statement")


# §4.2 rule 3: a directive, class shorthand or shape data, anywhere in a line.
_RULE_3 = ("%%{", ":::", "@{")


def _rule_3_text(line):
    """The first of §4.2 rule 3's texts that the line holds, or None."""
    for t in _RULE_3:
        if t in line:
            return t
    return None


def _decode(data):
    """§3. Returns (text, findings, stop)."""
    if isinstance(data, str):
        try:
            raw = data.encode("utf-8")
        except UnicodeEncodeError:
            return None, [Finding("bad-encoding", None, "the file is not well-formed UTF-8")], True
    else:
        raw = bytes(data)
    out = []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = None
        out.append(Finding("bad-encoding", None, "the file is not well-formed UTF-8"))
    if re.search(rb"\r(?!\n)", raw):
        out.append(Finding("lone-cr", None, "the file holds a CR that is not followed by LF"))
    if out:
        return None, out, True
    if text.startswith("\ufeff"):
        out.append(Finding("leading-bom", None, "the file begins with a byte-order mark"))
        text = text[1:]
    return text, out, False


def _lines(text):
    """§3: a line ends at LF or CRLF; the last line need not end with one."""
    if text == "":
        return []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return [ln[:-1] if ln.endswith("\r") else ln for ln in lines]


def check(data):
    """Check one nodespec file, given as bytes or as text.

    Returns a list of Finding. An empty list means the file is in the profile.
    """
    text, findings, stop = _decode(data)
    if stop:
        return findings
    lines = _lines(text)
    out = list(findings)

    def refuse(identifier, message, id=None):
        out.append(Finding(identifier, id, message))

    # §4.2 rule 1: front matter, refused together.
    front = 0
    if lines and lines[0].strip(g.WSP_CHARS) == "---":
        front = len(lines)
        for j in range(1, len(lines)):
            if lines[j].strip(g.WSP_CHARS) == "---":
                front = j + 1
                break
        refuse("not-admitted", "the file begins with front matter")

    stmts = []  # (line index, Stmt), for lines that were not refused
    header_seen = False
    block = None
    for i, line in enumerate(lines):
        # §4.9: stray-direction applies whatever else applies, to any line
        # but a comment, a front matter line or a line that matches
        # `direction-stmt`. A line §4.2 rule 3 refuses is not a comment,
        # since rule 3 classifies it before rule 5 is tried.
        rule_3 = _rule_3_text(line)
        stray = (
            i >= front
            and not (g.is_comment(line) and rule_3 is None)
            and not g.is_direction_stmt(line)
            and is_stray_direction(line)
        )
        if stray:
            refuse(
                "stray-direction",
                f"Mermaid would read part of the line {_show(line.strip(g.WSP_CHARS))} "
                "as a direction statement",
            )
        if i < front:
            continue
        # §4.2 rules 2 to 5.
        if line[:7] in ("<" * 7, "=" * 7, ">" * 7, "|" * 7):
            refuse("conflict-marker", f"the line {_show(line)} is a conflict marker")
            continue
        if rule_3 is not None:
            refuse("not-admitted", f"the line {_show(line.strip(g.WSP_CHARS))} holds `{rule_3}`")
            continue
        if g.is_blank(line) or g.is_comment(line):
            continue
        # §4.3: the first statement line is the header's place.
        if not header_seen:
            header_seen = True
            if not g.is_header(line):
                refuse("no-header", f"the first statement line {_show(line)} is not a header")
            continue
        st, refusal = _classify(line, block)
        if refusal is not None:
            refuse(refusal[0], refusal[1])
            continue
        if st.kind == "edge":
            # §4.6: an edge id on a link with `&` on either side.
            grps = st.edge.groups
            grouped = [
                ln.edge_id
                for k, ln in enumerate(st.edge.links)
                if ln.edge_id is not None and (len(grps[k]) > 1 or len(grps[k + 1]) > 1)
            ]
            if grouped:
                for eid in dict.fromkeys(grouped):
                    refuse(
                        "edge-id-on-group",
                        f"the edge id `{eid}` stands on a link with `&` beside it",
                        eid,
                    )
                continue
        if stray:
            continue
        # §4.4: reserved-id, only on a line nothing else refuses.
        reserved = [x for x in _ids_in(st) if is_reserved(x)]
        if st.kind == "classdef" and st.decls[0][0] == "node":
            reserved.append("node")
        if st.kind == "class" and st.names[-1][0] == "node":
            reserved.append("node")
        if reserved:
            for x in dict.fromkeys(reserved):
                refuse("reserved-id", f"`{x}` is reserved and cannot be an id here", x)
            continue
        stmts.append((i, st))
        if st.kind == "subgraph":
            block = _Block(st.decls[0][0])
        elif st.kind == "end":
            block = None
        elif st.kind == "direction":
            block.direction = True

    if not header_seen:
        refuse("no-header", "the file holds no statement line, so no header")
    if block is not None:
        refuse("unbalanced-block", f"the block `{block.id}` is never closed")
    _file_rules(stmts, refuse)
    return out


def _file_rules(stmts, refuse):
    """§4.6, §5, §6 and §7, over the statements of lines that were not refused."""
    decls = {}
    for _, st in stmts:
        for i, kind in st.decls:
            decls.setdefault(i, []).append(kind)

    # §5.1, §5.3
    for i in sorted(decls):
        kinds = decls[i]
        for kind in sorted(set(kinds)):
            if kinds.count(kind) > 1:
                refuse("duplicate-declaration", f"the {kind} `{i}` is declared twice", i)
                break
        if len(set(kinds)) > 1:
            both = " and as ".join(sorted(set(kinds)))
            refuse("kind-clash", f"`{i}` is declared as {both}", i)

    # §5.2
    undeclared, wrong = {}, {}
    for _, st in stmts:
        for i, allowed, place in st.names:
            if i not in decls:
                undeclared.setdefault(i, place)
            elif not set(decls[i]) & allowed:
                wrong.setdefault(i, (place, decls[i][0]))
    for i in sorted(undeclared):
        refuse("undeclared-id", f"`{i}` is named by {undeclared[i]} and declared nowhere", i)
    for i in sorted(wrong):
        place, kind = wrong[i]
        refuse("wrong-kind", f"{place} names `{i}`, which is declared as a {kind}", i)

    # §4.6
    edges = [e for _, st in stmts for e in st.edges]
    seen = {}
    for a, b, link, label, eid in edges:
        if eid is None:
            key = (a, b, link, label)
            seen[key] = seen.get(key, 0) + 1
    for (a, b, link, label), n in sorted(seen.items(), key=lambda kv: repr(kv[0])):
        if n > 1:
            lab = "" if label is None else f" labelled {_show(label)}"
            refuse("duplicate-edge", f"the edge `{a} {link} {b}`{lab} is written twice")
    if len(edges) > MAX_EDGES:
        refuse("too-many-edges", f"the file makes {len(edges)} edges, more than {MAX_EDGES}")

    # §6
    members = {}
    holds = {}
    for _, st in stmts:
        if st.kind == "member":
            members[st.member] = members.get(st.member, 0) + 1
            holds.setdefault(st.member, set()).add(st.holder)
    for i in sorted(members):
        if members[i] > 1:
            refuse("member-twice", f"`{i}` is named on more than one member line", i)
    for i in sorted(_on_cycles(holds)):
        refuse("membership-cycle", f"the subgraph `{i}` holds itself through its holders", i)

    # §7
    last_other = max((i for i, st in stmts if st.kind != "class"), default=-1)
    for i, st in stmts:
        if st.kind == "class" and i < last_other:
            refuse(
                "class-not-last",
                f"the class line giving `{st.names[-1][0]}` is followed by a statement "
                "that is not a class line",
            )
    for kind in ("style", "class"):
        count = {}
        for _, st in stmts:
            if st.kind == kind:
                for t in set(st.targets):
                    count[t] = count.get(t, 0) + 1
        for t in sorted(count):
            if count[t] > 1:
                refuse("styled-twice", f"`{t}` is the target of two {kind} lines", t)


def _on_cycles(holds):
    """The ids that lie on a cycle of the holder relation (§6)."""
    on = set()
    for start in holds:
        stack, seen = list(holds[start]), set()
        while stack:
            x = stack.pop()
            if x == start:
                on.add(start)
                break
            if x in seen:
                continue
            seen.add(x)
            stack.extend(holds.get(x, ()))
    return on
