# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The productions of SPEC.md §4.1, one function per production.

Each function takes one line, without its line ending, and returns what the
production reads from it, or None when the production does not match the
whole line. The constraints §4.1 lists beside the ABNF are part of the
productions here, so a line that breaks one does not match.
"""

import re
from dataclasses import dataclass

# --- character classes (§4.1) ----------------------------------------------

WSP_CHARS = " \t"
_WSP = r"[ \t]"

# U+2028 and U+2029 are left out of every class (§4.2).
_NONASCII = r"\u00a0-\u2027\u202a-\ud7ff\ue000-\U0010ffff"
# A label character: not [ ] ( ) { } | " @
_LCHAR = r"[\t\x20\x21\x23-\x27\x2a-\x3f\x41-\x5a\x5c\x5e-\x7a\x7e" + _NONASCII + "]"
# An lchar that is not WSP, - / or \
_LEAD = r"[\x21\x23-\x27\x2a-\x2c\x2e\x30-\x3f\x41-\x5a\x5e-\x7a\x7e" + _NONASCII + "]"
_QCHAR = r"[\t\x20\x21\x23-\x7e" + _NONASCII + "]"
_CCHAR = r"[\t\x20-\x7e" + _NONASCII + "]"
_COMMENT_FIRST = r"[\t\x20-\x7a\x7c-\x7e" + _NONASCII + "]"

_ID = r"[A-Za-z0-9_]+"
_DIR = r"(?:TB|TD|BT|LR|RL)"
_LABEL = r"(?:" + _WSP + "*" + _LEAD + _LCHAR + '*|"' + _QCHAR + '+")'

ID_RE = re.compile(_ID)


def label_ok(label):
    """The label constraints §4.1 and §4.5 add to `unquoted` and `quoted`."""
    if label.startswith('"'):
        text = label[1:-1]
        return (
            any(c not in WSP_CHARS for c in text)
            and not text.startswith("`")
            and not text.endswith("=")
        )
    return "~~~" not in label


# --- §4.2: blank, comment, header ------------------------------------------

_BLANK = re.compile(_WSP + "*")
_COMMENT = re.compile(_WSP + "*%%" + _COMMENT_FIRST + _CCHAR + "*")
_HEADER = re.compile(_WSP + "*(?:flowchart|graph)(?:" + _WSP + "+" + _DIR + ")?" + _WSP + "*")


def is_blank(line):
    return _BLANK.fullmatch(line) is not None


def is_comment(line):
    # A comment does not hold `="` (§4.2 rule 5).
    return _COMMENT.fullmatch(line) is not None and '="' not in line


def is_header(line):
    return _HEADER.fullmatch(line) is not None


# --- §4.5: shapes ------------------------------------------------------------

# (open, close, Mermaid's type), the classic fourteen.
SHAPES = (
    ("(((", ")))", "doublecircle"),
    ("([", "])", "stadium"),
    ("[[", "]]", "subroutine"),
    ("[(", ")]", "cylinder"),
    ("((", "))", "circle"),
    ("{{", "}}", "hexagon"),
    ("[/", "/]", "lean_right"),
    ("[\\", "\\]", "lean_left"),
    ("[/", "\\]", "trapezoid"),
    ("[\\", "/]", "inv_trapezoid"),
    ("[", "]", "square"),
    ("(", ")", "round"),
    (">", "]", "odd"),
    ("{", "}", "diamond"),
)
_SHAPE_RES = tuple(
    (re.compile(re.escape(o) + "(" + _LABEL + ")" + re.escape(c)), t) for o, c, t in SHAPES
)


def match_shape(s, pos):
    """A `shape` starting at `pos`: (end, shape type, label), or None."""
    for rx, typ in _SHAPE_RES:
        m = rx.match(s, pos)
        if m and label_ok(m.group(1)):
            return m.end(), typ, m.group(1)
    return None


# --- §4.3 and §4.5: node statements, member lines, end, direction -----------

_LEAD_ID = re.compile(_WSP + "*(" + _ID + ")")
_TRAIL = re.compile(_WSP + "*")
_MEMBER = re.compile(_WSP + "*(" + _ID + ")" + _WSP + "*")
_END = re.compile(_WSP + "*end" + _WSP + "*")
_DIRECTION = re.compile(_WSP + "*direction" + _WSP + "+" + _DIR + _WSP + "*")


@dataclass(frozen=True)
class NodeStmt:
    id: str
    shape: str


def node_stmt(line):
    m = _LEAD_ID.match(line)
    if not m:
        return None
    sh = match_shape(line, m.end())
    if not sh or not _TRAIL.fullmatch(line, sh[0]):
        return None
    return NodeStmt(m.group(1), sh[1])


def member_line(line):
    m = _MEMBER.fullmatch(line)
    return m.group(1) if m else None


def is_end_line(line):
    return _END.fullmatch(line) is not None


def is_direction_stmt(line):
    return _DIRECTION.fullmatch(line) is not None


# --- §4.6: edge statements and edge-decl ------------------------------------

_LINK = (
    r"(?:-{2,}>|-{3,}|-{2,}o|-{2,}x|<-{2,}>|o-{2,}o|x-{2,}x"
    r"|-\.+->|-\.+-|={2,}>|={3,}|~{3,})"
)
_LINK_AT = re.compile(r"[ \t]+(?:(" + _ID + r")@)?(" + _LINK + r")(?=[| \t])")
_EDGE_LABEL = re.compile(r"\|(" + _LABEL + r")\|")
_AMP = re.compile(r"[ \t]+&[ \t]+")
_WSP1 = re.compile(_WSP + "+")


@dataclass(frozen=True)
class Link:
    edge_id: str | None
    link: str
    label: str | None  # the text between the `|`s, as written


@dataclass(frozen=True)
class Edge:
    groups: tuple  # tuple of tuples of ids
    links: tuple  # tuple of Link, one between each two groups


def _group(s, pos, shapes):
    """A `group` (or a `dgroup` when `shapes`) at `pos`: (end, ids)."""
    ids = []
    while True:
        m = ID_RE.match(s, pos)
        if not m:
            return None
        ids.append(m.group(0))
        pos = m.end()
        if shapes:
            sh = match_shape(s, pos)
            if sh:
                pos = sh[0]
        a = _AMP.match(s, pos)
        if not a:
            return pos, tuple(ids)
        pos = a.end()


def edge(line, shapes=False):
    """`edge-stmt`, or `edge-decl` when `shapes`. None when it does not match."""
    pos = _TRAIL.match(line).end()
    g = _group(line, pos, shapes)
    if not g:
        return None
    pos, ids = g
    groups, links = [ids], []
    while True:
        if _TRAIL.fullmatch(line, pos):
            break
        m = _LINK_AT.match(line, pos)
        if not m:
            return None
        pos = m.end()
        label = None
        lm = _EDGE_LABEL.match(line, pos)
        if lm:
            if not label_ok(lm.group(1)):
                return None
            label, pos = lm.group(1), lm.end()
        w = _WSP1.match(line, pos)
        if not w:
            return None
        g = _group(line, w.end(), shapes)
        if not g:
            return None
        pos, ids = g
        links.append(Link(m.group(1), m.group(2), label))
        groups.append(ids)
    if not links:
        return None
    return Edge(tuple(groups), tuple(links))


# --- §4.7: subgraph lines ----------------------------------------------------

_SUBGRAPH = re.compile(
    _WSP + "*subgraph" + _WSP + "+(" + _ID + ")(?:" + _WSP + r"*\[(" + _LABEL + r")\])?"
)
_SUBGRAPH_REST = re.compile(_WSP + "*subgraph" + _WSP + "*")


def subgraph_line(line):
    """The subgraph's id, or None."""
    m = _SUBGRAPH.fullmatch(line)
    if not m or (m.group(2) is not None and not label_ok(m.group(2))):
        return None
    return m.group(1)


def is_subgraph_without_id(line):
    """§4.7's test, for a line whose first word is `subgraph`."""
    text = line[_SUBGRAPH_REST.match(line).end() :]
    if text == "" or text.startswith('"'):
        return True
    bracket = text.find("[")
    before = text if bracket < 0 else text[:bracket].rstrip(WSP_CHARS)
    return any(c in WSP_CHARS for c in before)


# --- §4.8: classDef, class, style -------------------------------------------

_CLASSDEF = re.compile(_WSP + "*classDef" + _WSP + "+(" + _ID + ")" + _WSP + "+(.*?)" + _WSP + "*")
_STYLE = re.compile(_WSP + "*style" + _WSP + "+(" + _ID + ")" + _WSP + "+(.*?)" + _WSP + "*")
_CLASS = re.compile(
    _WSP + "*class" + _WSP + "+(" + _ID + "(?:," + _ID + ")*)" + _WSP + "+(" + _ID + ")"
)

# The 17 words of §4.4, which a style `name` may not be or begin with before `-`.
KEYWORDS = frozenset(
    "end graph flowchart subgraph style class classDef click linkStyle interpolate "
    "call href default _self _blank _parent _top".split()
)
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)*")
_COLOUR = re.compile(r"#[0-9A-Fa-f]+")
_NUMBER = re.compile(r"(?:-?[0-9]+(?:\.[0-9]+)?|\.[0-9]+)([a-z]+)?%?")


def _name_ok(name):
    if _NAME.fullmatch(name) is None:
        return False
    head = name.split("-", 1)[0]
    if name == "v" or head == "v" or head in KEYWORDS:
        return False
    return name != "swimlane-beta" and not name.startswith("swimlane-beta-")


def _word_ok(word):
    if _COLOUR.fullmatch(word):
        return True
    m = _NUMBER.fullmatch(word)
    if m:
        return m.group(1) != "v"
    return _name_ok(word[1:] if word.startswith("!") else word)


_SPACES = re.compile(" +")


def style_list_ok(text):
    """`style-list`, with §4.1's constraints on `unit` and `name`."""
    for item in text.split(","):
        prop, colon, value = item.partition(":")
        if not colon or not _name_ok(prop) or prop in ("accTitle", "accDescr"):
            return False
        # name ":" *SP value, and value = word *( 1*SP word ): only spaces,
        # never a tab, and a space before a `,` leaves an empty word.
        words = _SPACES.split(value.lstrip(" "))
        if not all(w and _word_ok(w) for w in words):
            return False
    return True


def classdef_stmt(line):
    m = _CLASSDEF.fullmatch(line)
    if not m or not style_list_ok(m.group(2)):
        return None
    return m.group(1)


def style_stmt(line):
    m = _STYLE.fullmatch(line)
    if not m or not style_list_ok(m.group(2)):
        return None
    return m.group(1)


def class_stmt(line):
    """(targets, class), or None."""
    m = _CLASS.fullmatch(line)
    if not m:
        return None
    return tuple(m.group(1).split(",")), m.group(2)
