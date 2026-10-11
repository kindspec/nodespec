#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
"""extract2 -- the blind second extractor X (Appendix D).

    python3 -I extract2.py <stratum> <base> <o> <t> <merged>

Prints one JSON object: the decided values, the exposure, and every record
with its category, objects and tier.  Pure stdlib.  Every place where the
specification left a choice is listed in CHOICES.md, keyed by the section.
"""

import json
import re
import sys
from collections import Counter, defaultdict


# --------------------------------------------------------------------------
# Sentinels and failures
# --------------------------------------------------------------------------

class _Absent:
    def __repr__(self):
        return "ABSENT"


class _Conflict:
    def __repr__(self):
        return "CONFLICT"


ABSENT = _Absent()
CONFLICT = _Conflict()


class HFail(Exception):
    """H refuses a text.

    kind is one of:
      noparse      -- R certainly does not parse it (section 4.4)
      unsupported  -- outside the subset (Appendix A); R may parse it
      notflowchart -- a Mermaid diagram, but not a flowchart (G0)
    """

    def __init__(self, kind, reason, **extra):
        Exception.__init__(self, reason)
        self.kind = kind
        self.reason = reason
        self.extra = extra


def unsupported(reason, **extra):
    raise HFail("unsupported", reason, **extra)


def noparse(reason):
    raise HFail("noparse", reason)


# --------------------------------------------------------------------------
# Lexical pieces of the subset (Appendix A)
# --------------------------------------------------------------------------

ID_RE = re.compile(r"[A-Za-z0-9_](?:[A-Za-z0-9_]|-(?![->.])|\.(?![-.]))*")
CLASSNAME_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")
HEADER_RE = re.compile(r"(flowchart-elk|flowchart|graph)(?:[ \t]+(TB|TD|BT|LR|RL))?[ \t]*$")
SUBGRAPH_DIRS = ("TB", "BT", "LR", "RL")
BR_RE = re.compile(r"<br\s*/?>", re.I)
ENTITY_RE = re.compile(r"#[A-Za-z0-9_]+;")
STYLE_LINE_RE = re.compile(r"style.*:\S*#.*;")
CLASSDEF_LINE_RE = re.compile(r"classDef.*:\S*#.*;")
# A bare "=======" line is not a marker on its own: in Markdown it underlines
# a heading, and git never writes one without a "<<<<<<<" line before it.
CONFLICT_RE = re.compile(r"^(<{7}|>{7}|\|{7})(?: |$)", re.M)
FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*mermaid(?:-example)?\b", re.I)

RESERVED_IDS = {"subgraph", "graph", "flowchart", "flowchart-elk", "style",
                "class", "classDef", "linkStyle", "click", "direction",
                "accTitle", "accDescr", "call", "href", "default"}

OTHER_DIAGRAMS = {
    "sequenceDiagram", "classDiagram", "classDiagram-v2", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "gantt", "pie", "journey", "gitGraph",
    "mindmap", "timeline", "quadrantChart", "requirementDiagram", "sankey",
    "sankey-beta", "xychart", "xychart-beta", "block", "block-beta",
    "packet", "packet-beta", "architecture", "architecture-beta",
    "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
    "kanban", "radar-beta", "treemap", "treemap-beta", "info", "zenuml",
}

# The short names and aliases of the documented shape table
# (mermaid-12.1.0-flowchart.md, "Complete List of New Shapes").
SHAPE_NAMES = set("""
bang browser bucket notch-rect card notched-rectangle cloud hourglass collate
bolt com-link lightning-bolt brace brace-l comment brace-r braces console
lean-r in-out lean-right lean-l lean-left out-in datastore data-store cyl
cylinder database db diam decision diamond question delay
half-rounded-rectangle h-cyl das horizontal-cylinder lin-cyl disk
lined-cylinder curv-trap curved-trapezoid display div-rect div-proc
divided-process divided-rectangle doc document rounded event tri extract
triangle folder directory fork join win-pane internal-storage window-pane
f-circ filled-circle junction lin-doc lined-document lin-rect lin-proc
lined-process lined-rectangle shaded-process notch-pent loop-limit
notched-pentagon flip-tri flipped-triangle manual-file sl-rect manual-input
sloped-rectangle trap-t inv-trapezoid manual trapezoid-top docs documents
st-doc stacked-document st-rect processes procs stacked-rectangle odd flag
paper-tape person hex hexagon prepare trap-b priority trapezoid
trapezoid-bottom rect proc process rectangle circle circ sm-circ
small-circle start dbl-circ double-circle fr-circ framed-circle stop
bow-rect bow-tie-rectangle stored-data fr-rect framed-rectangle subproc
subprocess subroutine cross-circ crossed-circle summary tag-doc
tagged-document tag-rect tag-proc tagged-process tagged-rectangle stadium
pill terminal text
""".split())

# Classic shape brackets: (opener, [(closer, R type)]), longest opener first.
SHAPES = [
    ("(((", [(")))", "doublecircle")]),
    ("((", [("))", "circle")]),
    ("([", [("])", "stadium")]),
    ("(", [(")", "round")]),
    ("[[", [("]]", "subroutine")]),
    ("[(", [(")]", "cylinder")]),
    ("[/", [("/]", "lean_right"), ("\\]", "trapezoid")]),
    ("[\\", [("\\]", "lean_left"), ("/]", "inv_trapezoid")]),
    ("[", [("]", "square")]),
    ("{{", [("}}", "hexagon")]),
    ("{", [("}", "diamond")]),
    (">", [("]", "odd")]),
]

# The arrows Appendix A admits, as (line, start head, end head).
ALLOWED_KINDS = {
    ("solid", "none", "arrow"), ("solid", "none", "none"),
    ("solid", "none", "circle"), ("solid", "none", "cross"),
    ("solid", "arrow", "arrow"), ("solid", "circle", "circle"),
    ("solid", "cross", "cross"),
    ("dotted", "none", "arrow"), ("dotted", "none", "none"),
    ("thick", "none", "arrow"), ("thick", "none", "none"),
    ("invisible", "none", "none"),
}
HEADS = {">": "arrow", "<": "arrow", "o": "circle", "x": "cross"}

FULL_LINKS = [
    ("solid", re.compile(r"([<ox]?)(-{2,})([>ox])")),
    ("solid", re.compile(r"([<ox]?)(-{3,})()")),
    ("thick", re.compile(r"([<ox]?)(={2,})([>ox])")),
    ("thick", re.compile(r"([<ox]?)(={3,})()")),
    ("dotted", re.compile(r"([<ox]?)(-\.+-)([>ox]?)")),
    ("invisible", re.compile(r"()(~{3,})()")),
]
START_LINKS = [
    ("solid", re.compile(r"([<ox]?)--(?![->])"), re.compile(r"\s*(-{2,})([->ox])")),
    ("thick", re.compile(r"([<ox]?)==(?![=>])"), re.compile(r"\s*(={2,})([=>ox])")),
    ("dotted", re.compile(r"([<ox]?)-\.(?![-.])"), re.compile(r"\s*(\.+-)([>ox]?)")),
]


def norm_text(raw, quoted, what):
    """A label, title or edge text as R holds it (sanitized, trimmed)."""
    if quoted and raw.startswith("`"):
        unsupported("Markdown-string %s" % what)
    if "\n" in raw:
        unsupported("multi-line %s" % what)
    text = BR_RE.sub("<br>", raw)
    if re.search(r"[<>&]", text.replace("<br>", "")):
        unsupported("HTML-like text in %s" % what)
    if not quoted:
        if re.search(r"[\[\](){}|\"`;]", text):
            unsupported("bracket or quote in unquoted %s" % what)
        if re.search(r"--|==|-\.|\.-|~~", text):
            unsupported("link-like text in unquoted %s" % what)
        if re.search(r"(?<![A-Za-z0-9_])end(?![A-Za-z0-9_])", text):
            unsupported("lowercase 'end' in unquoted %s" % what)
    text = text.strip()
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1]
    if text == "":
        unsupported("empty %s" % what)
    return text


def check_id(ident):
    if ident == "end":
        noparse("lowercase 'end' used as an id")
    if ident in RESERVED_IDS:
        unsupported("keyword %r used as an id" % ident)
    return ident


def split_statements(line):
    """Split one line at ';' outside quotes and brackets."""
    out, cur, depth, inq = [], [], 0, False
    for ch in line:
        if inq:
            cur.append(ch)
            if ch == '"':
                inq = False
            continue
        if ch == '"':
            inq = True
        elif ch in "[({":
            depth += 1
        elif ch in "])}":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            out.append("".join(cur))
            cur = []
            continue
        cur.append(ch)
    if inq:
        unsupported("unterminated string")
    out.append("".join(cur))
    return [s.strip() for s in out if s.strip()]


def parse_styles(rest, what):
    rest = rest.strip()
    if not rest:
        unsupported("%s without styles" % what)
    if re.search(r'[\\"]', rest):
        unsupported("escape or quote in %s" % what)
    parts = [p.strip() for p in rest.split(",")]
    if any(p == "" for p in parts):
        unsupported("empty style in %s" % what)
    return parts


def parse_shape_data(body):
    """The `@{ shape: ..., label: ... }` form, as a one-line flow mapping."""
    items, cur, inq = [], [], False
    for ch in body:
        if ch == '"':
            inq = not inq
        if ch == "," and not inq:
            items.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if inq:
        unsupported("unterminated string in @{...}")
    items.append("".join(cur))
    doc = {}
    for item in items:
        item = item.strip()
        if not item:
            continue
        m = re.match(r'([A-Za-z]+)\s*:\s*(.*)$', item)
        if not m:
            unsupported("unreadable @{...} entry")
        key, val = m.group(1), m.group(2).strip()
        if key not in ("shape", "label"):
            unsupported("@{...} key %r" % key)
        if key in doc:
            unsupported("repeated @{...} key")
        if val.startswith('"'):
            if len(val) < 2 or not val.endswith('"') or '"' in val[1:-1] or "\\" in val:
                unsupported("unreadable quoted @{...} value")
            val = val[1:-1]
        else:
            if re.search(r"""[\[\]{}'"#&*!|>%@`]|:\s""", val) or val == "":
                unsupported("unreadable plain @{...} value")
            if re.fullmatch(r"(?i)true|false|null|~|[-+]?(\d[\d_]*)?(\.\d*)?([eE][-+]?\d+)?|[-+]?\.(inf|nan)", val):
                unsupported("non-string @{...} value")
        doc[key] = val
    if "label" in doc:
        if doc["label"].startswith("`") or "\n" in doc["label"]:
            unsupported("Markdown-string label in @{...}")
        if doc["label"] == "":
            unsupported("empty label in @{...}")
    if "shape" in doc:
        shape = doc["shape"]
        if shape != shape.lower() or "_" in shape:
            noparse("No such shape: %s" % shape)
        if shape not in SHAPE_NAMES:
            unsupported("shape %r not in the documented table" % shape)
    return doc


# --------------------------------------------------------------------------
# H: the parser, mirroring R's flowchart database as Appendix A maps it
# --------------------------------------------------------------------------

class Vertex:
    __slots__ = ("text", "type", "classes", "styles", "link", "target")

    def __init__(self):
        self.text = None
        self.type = None
        self.classes = []
        self.styles = []
        self.link = ABSENT
        self.target = ABSENT


class Edge:
    __slots__ = ("start", "end", "kind", "text", "id", "user", "style")


class Subgraph:
    __slots__ = ("rid", "key", "explicit", "title", "nodes", "dir", "seq")


class Block:
    __slots__ = ("seq", "explicit", "title", "mentions", "dir")


class Db:
    """One parsed diagram: R's database plus what the lints read."""

    def __init__(self):
        self.direction = "TB"
        self.vertices = {}
        self.edges = []
        self.edge_ids = set()
        self.subgraphs = []
        self.classdefs = {}
        self.link_default = None
        self.has_stmt = set()
        self.node_stmts = defaultdict(list)
        self.mentions = []          # (id, innermost block seq or None)
        self.style_targets = []
        self.written_uids = []
        self.edge_stmts = []        # (written uid or None, start, end, kind, text)
        self.sub_count = 0
        self.block_seq = 0

    # R's addVertex
    def add_vertex(self, ident, text=None, vtype=None, styles=None, doc=None):
        if ident in self.edge_ids:
            return False
        v = self.vertices.get(ident)
        if v is None:
            v = self.vertices[ident] = Vertex()
        if text is not None:
            v.text = text
        elif v.text is None:
            v.text = ident
        if vtype is not None:
            v.type = vtype
        if styles:
            v.styles.extend(styles)
        if doc:
            if "shape" in doc:
                v.type = doc["shape"]
            if doc.get("label"):
                v.text = doc["label"]
        return True

    # R's setClass, for what Appendix A maps (vertex classes)
    def set_class(self, ids, cls):
        for ident in ids:
            if ident in self.vertices:
                self.vertices[ident].classes.append(cls)

    # R's addLink / addSingleLink
    def add_link(self, starts, ends, kind, text, uid):
        for s in starts:
            for e in ends:
                use = uid if (s == starts[-1] and e == ends[0]) else None
                self.add_single_link(s, e, kind, text, use)
                self.edge_stmts.append((use, s, e, kind, text))

    def add_single_link(self, s, e, kind, text, uid):
        edge = Edge()
        edge.start, edge.end, edge.kind = s, e, kind
        edge.text = text if text is not None else ""
        edge.style = None
        if uid and uid not in self.edge_ids:
            edge.id, edge.user = uid, True
        else:
            n = sum(1 for x in self.edges if x.start == s and x.end == e)
            edge.id = "L_%s_%s_%d" % (s, e, 0 if n == 0 else n + 1)
            edge.user = False
        if len(self.edges) >= 100000:
            noparse("Edge limit exceeded")
        self.edges.append(edge)
        self.edge_ids.add(edge.id)


class Parser:
    def __init__(self, text):
        self.text = text
        self.db = Db()
        self.stack = []

    # -- whole text ------------------------------------------------------
    def parse(self):
        text = self.text
        for line in text.split("\n"):
            probe = CLASSDEF_LINE_RE.sub(lambda m: m.group(0)[:-1], STYLE_LINE_RE.sub(lambda m: m.group(0)[:-1], line))
            if ENTITY_RE.search(probe):
                unsupported("entity code #...; (R encodes it before parsing)")
        lines = text.split("\n")
        i = 0
        # front matter
        if lines and lines[0].rstrip() == "---":
            j = 1
            while j < len(lines) and lines[j].rstrip() != "---":
                j += 1
            if j >= len(lines):
                noparse("unterminated front matter")
            i = j + 1
        # leading blank lines, comments and directives
        while i < len(lines):
            s = lines[i].strip()
            if s == "" or (s.startswith("%%") and not s.startswith("%%{")):
                i += 1
            elif s.startswith("%%{"):
                if not re.fullmatch(r"%%\{.*\}%%", s):
                    unsupported("multi-line or malformed directive")
                i += 1
            else:
                break
        if i >= len(lines):
            noparse("no diagram header")
        head_line = lines[i].strip()
        head, sep, rest = head_line.partition(";")
        self.header(head.strip())
        body = [(i + 1, rest)] if sep else []
        body += [(n + 1, lines[n]) for n in range(i + 1, len(lines))]
        for _lineno, line in body:
            s = line.strip()
            if s == "" or (s.startswith("%%") and not s.startswith("%%{")):
                continue
            if s.startswith("%%{"):
                unsupported("directive after the header")
            if "%%" in s and not s.startswith("%%"):
                unsupported("inline %% comment")
            for stmt in split_statements(s):
                self.statement(stmt)
        if self.stack:
            noparse("subgraph without end")
        self.finish()
        return self.db

    def header(self, head):
        m = HEADER_RE.match(head)
        if m:
            d = m.group(2) or "TB"
            self.db.direction = "TB" if d == "TD" else d
            return
        word = head.split()[0] if head.split() else ""
        if word in OTHER_DIAGRAMS:
            raise HFail("notflowchart", "diagram type %s" % word)
        if word in ("flowchart", "flowchart-elk", "graph"):
            unsupported("header outside the subset: %r" % head)
        if word.lower() in ("flowchart", "flowchart-elk", "graph"):
            noparse("mixed-case header %r" % word)
        noparse("unknown diagram header %r" % head)

    # -- statements -------------------------------------------------------
    def statement(self, s):
        word = s.split(None, 1)[0]
        rest = s[len(word):].strip()
        if word == "subgraph":
            return self.subgraph_open(rest)
        if word == "end":
            if rest:
                unsupported("text after end")
            return self.subgraph_close()
        if word == "direction":
            if not self.stack:
                unsupported("direction statement outside a subgraph")
            if rest not in SUBGRAPH_DIRS:
                unsupported("subgraph direction %r" % rest)
            self.stack[-1].dir = rest
            return
        if word == "classDef":
            m = re.match(r"([A-Za-z0-9_-]+(?:,[A-Za-z0-9_-]+)*)\s+(.*)$", rest)
            if not m:
                unsupported("classDef form")
            styles = parse_styles(m.group(2), "classDef")
            for name in m.group(1).split(","):
                self.db.classdefs.setdefault(name, []).extend(styles)
            return
        if word == "class":
            m = re.match(r"(\S+)\s+([A-Za-z0-9_][A-Za-z0-9_-]*)$", rest)
            if not m:
                unsupported("class statement form")
            ids = m.group(1).split(",")
            for ident in ids:
                if not ID_RE.fullmatch(ident):
                    unsupported("class target %r" % ident)
            self.db.set_class(ids, m.group(2))
            return
        if word == "style":
            m = re.match(r"(\S+)\s+(.*)$", rest)
            if not m or not ID_RE.fullmatch(m.group(1)):
                unsupported("style statement form")
            ident = check_id(m.group(1))
            styles = parse_styles(m.group(2), "style")
            self.db.style_targets.append(ident)
            self.db.add_vertex(ident, styles=styles)
            return
        if word == "linkStyle":
            return self.link_style(rest)
        if word == "click":
            return self.click(rest)
        if word in ("accTitle", "accDescr") or word.startswith("accTitle:") or word.startswith("accDescr"):
            unsupported("accessibility statement")
        return self.vertex_statement(s)

    def subgraph_open(self, rest):
        if not rest:
            unsupported("subgraph without id or title")
        b = Block()
        self.db.block_seq += 1
        b.seq = self.db.block_seq
        b.mentions = []
        b.dir = None
        m = re.match(r"([A-Za-z0-9_][^\s\[\]\"]*)\s*\[(.*)\]$", rest)
        if m:
            ident, raw = m.group(1), m.group(2)
            if not ID_RE.fullmatch(ident):
                unsupported("subgraph id %r" % ident)
            quoted = len(raw) >= 2 and raw.startswith('"') and raw.endswith('"') and '"' not in raw[1:-1]
            if '"' in raw and not quoted:
                unsupported("subgraph title quoting")
            b.explicit = ident
            b.title = norm_text(raw[1:-1] if quoted else raw, quoted, "subgraph title")
        elif rest.startswith('"'):
            if not (rest.endswith('"') and len(rest) >= 2 and '"' not in rest[1:-1]):
                unsupported("subgraph title quoting")
            raw = rest[1:-1]
            if re.search(r"\s", raw):
                b.explicit, b.title = None, norm_text(raw, True, "subgraph title")
            else:
                if not ID_RE.fullmatch(raw):
                    unsupported("quoted subgraph id %r" % raw)
                b.explicit, b.title = raw, raw
        elif ID_RE.fullmatch(rest):
            b.explicit, b.title = rest, rest
        else:
            if not re.search(r"\s", rest):
                unsupported("subgraph header %r" % rest)
            b.explicit, b.title = None, norm_text(rest, False, "subgraph title")
        if b.explicit is not None:
            check_id(b.explicit)
            if re.fullmatch(r"subGraph\d+", b.explicit):
                unsupported("explicit subgraph id of the form subGraphN")
        self.stack.append(b)

    def subgraph_close(self):
        if not self.stack:
            noparse("end without subgraph")
        b = self.stack.pop()
        db = self.db
        sg = Subgraph()
        sg.rid = b.explicit if b.explicit is not None else "subGraph%d" % db.sub_count
        db.sub_count += 1
        sg.explicit = b.explicit is not None
        sg.key = b.explicit if sg.explicit else "title:" + b.title
        sg.title = b.title
        sg.nodes = list(dict.fromkeys(b.mentions))
        sg.dir = b.dir
        sg.seq = b.seq
        db.subgraphs.append(sg)
        if self.stack:
            self.stack[-1].mentions.append(sg.rid)

    def link_style(self, rest):
        m = re.match(r"(default|\d+(?:,\d+)*)\s+(.*)$", rest)
        if not m:
            unsupported("linkStyle form")
        if re.match(r"interpolate\b", m.group(2)):
            unsupported("linkStyle interpolate")
        styles = parse_styles(m.group(2), "linkStyle")
        if m.group(1) == "default":
            self.db.link_default = list(styles)
            return
        for pos in (int(p) for p in m.group(1).split(",")):
            if pos >= len(self.db.edges):
                noparse("linkStyle index %d out of range" % pos)
            st = list(styles)
            if not any(x.startswith("fill") for x in st):
                st.append("fill:none")
            self.db.edges[pos].style = st

    def click(self, rest):
        m = re.match(r"(\S+)\s+(.*)$", rest)
        if not m or not ID_RE.fullmatch(m.group(1)):
            unsupported("click form")
        ident, rest = m.group(1), m.group(2).strip()
        target_re = r"(?:\s+(_self|_blank|_parent|_top))?"
        tip_re = r'(?:\s+"[^"]*")?'
        m = re.fullmatch(r'(?:href\s+)?"([^"]*)"' + tip_re + target_re, rest)
        if m:
            url = m.group(1).strip()
            if (not url or re.search(r"[\s%&\\<>\"\x00-\x1f\x7f]", url)
                    or re.match(r"(?i)\W*(javascript|data|vbscript):", url)):
                unsupported("click URL outside the subset")
            v = self.db.vertices.get(ident)
            if v is not None:
                v.link = url
                v.target = m.group(2) if m.group(2) else ABSENT
            return
        if re.fullmatch(r"(?:call\s+)?[A-Za-z_$][\w$]*(?:\([^()\"]*\))?" + tip_re, rest):
            return  # a callback: strict security level ignores it
        unsupported("click form")

    # -- vertex statements --------------------------------------------------
    def vertex_statement(self, s):
        self.s, self.pos = s, 0
        groups = [self.group()]
        links = []
        while True:
            had_ws = self.ws()
            if self.pos >= len(self.s):
                break
            links.append(self.link(had_ws))
            self.ws()
            if self.pos >= len(self.s):
                unsupported("link without a target in the statement")
            groups.append(self.group())
        db = self.db
        block = self.stack[-1] if self.stack else None
        prev = None
        for gi, group in enumerate(groups):
            ids = []
            for node in group:
                ident = node["id"]
                ids.append(ident)
                if node["stmt"]:
                    db.has_stmt.add(ident)
                    db.node_stmts[ident].append((node["label"], node["shape"]))
                db.add_vertex(ident, node["text"], node["vtype"], None, node["doc"])
                if node["cls"]:
                    db.set_class([ident], node["cls"])
                db.mentions.append((ident, block.seq if block else None))
                if block is not None:
                    block.mentions.append(ident)
            if gi > 0:
                kind, text, uid = links[gi - 1]
                if uid is not None:
                    db.written_uids.append(uid)
                db.add_link(prev, ids, kind, text, uid)
            prev = ids

    def ws(self):
        start = self.pos
        while self.pos < len(self.s) and self.s[self.pos] in " \t":
            self.pos += 1
        return self.pos > start

    def group(self):
        nodes = [self.node()]
        while True:
            save = self.pos
            self.ws()
            if self.s.startswith("&", self.pos):
                self.pos += 1
                self.ws()
                nodes.append(self.node())
            else:
                self.pos = save
                return nodes

    def node(self):
        m = ID_RE.match(self.s, self.pos)
        if not m:
            unsupported("expected a node id at %r" % self.s[self.pos:self.pos + 20])
        ident = check_id(m.group(0))
        self.pos = m.end()
        node = {"id": ident, "stmt": False, "text": None, "vtype": None,
                "doc": None, "cls": None, "label": None, "shape": None}
        s = self.s
        if s.startswith("@{", self.pos):
            end = self.find_close_brace(self.pos + 2)
            doc = parse_shape_data(s[self.pos + 2:end])
            self.pos = end + 1
            node.update(stmt=True, doc=doc, label=doc.get("label"), shape=doc.get("shape"))
        elif self.pos < len(s) and s[self.pos] in "[({>":
            text, vtype = self.shape()
            node.update(stmt=True, text=text, vtype=vtype, label=text, shape=vtype)
        if s.startswith(":::", self.pos):
            m = CLASSNAME_RE.match(s, self.pos + 3)
            if not m:
                unsupported("::: without a class name")
            node["cls"] = m.group(0)
            self.pos = m.end()
        if self.pos < len(s) and s[self.pos] not in " \t&" and not s.startswith(("-", "=", "~", "<"), self.pos):
            unsupported("unexpected text after node %r" % ident)
        return node

    def find_close_brace(self, i):
        inq = False
        while i < len(self.s):
            ch = self.s[i]
            if ch == '"':
                inq = not inq
            elif ch == "}" and not inq:
                return i
            i += 1
        unsupported("@{...} not closed on its line")

    def shape(self):
        s = self.s
        for opener, closers in SHAPES:
            if not s.startswith(opener, self.pos):
                continue
            start = self.pos + len(opener)
            if s.startswith('"', start):
                q = s.find('"', start + 1)
                if q < 0:
                    unsupported("unterminated quoted label")
                raw = s[start + 1:q]
                for closer, vtype in closers:
                    if s.startswith(closer, q + 1):
                        self.pos = q + 1 + len(closer)
                        return norm_text(raw, True, "label"), vtype
                unsupported("quoted label not followed by its closing bracket")
            # unquoted: the first closer of this shape ends the label
            best = None
            for closer, vtype in closers:
                j = s.find(closer, start)
                if j >= 0 and (best is None or j < best[0]):
                    best = (j, closer, vtype)
            if best is None:
                unsupported("shape bracket not closed on its line")
            j, closer, vtype = best
            raw = s[start:j]
            if opener in ("[/", "[\\") and re.search(r"[/\\]", raw):
                unsupported("slash in a slanted-shape label")
            self.pos = j + len(closer)
            return norm_text(raw, False, "label"), vtype
        unsupported("unknown shape bracket")

    def link(self, had_ws):
        """One link, with an optional edge id and label: (kind, text, uid)."""
        s = self.s
        uid = None
        m = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_-]*)@").match(s, self.pos)
        if m and had_ws and not s.startswith("{", m.end()):
            uid = m.group(1)
            self.pos = m.end()
            had_ws = False
        if not had_ws and self.pos < len(s) and s[self.pos] in "ox":
            if uid is None and self.pos > 0 and s[self.pos - 1] not in " \t":
                unsupported("o/x link head directly after an id")
        for line, rx in FULL_LINKS:
            m = rx.match(s, self.pos)
            if m:
                pre, body, post = m.group(1), m.group(2), m.group(3)
                self.pos = m.end()
                kind = self.kind(line, pre, post)
                text = None
                save = self.pos
                self.ws()
                if s.startswith("|", self.pos):
                    j = s.find("|", self.pos + 1)
                    if j < 0:
                        unsupported("unterminated |label|")
                    text = self.edge_text(s[self.pos + 1:j])
                    self.pos = j + 1
                else:
                    self.pos = save
                return kind, text, uid
        for line, rx, close in START_LINKS:
            m = rx.match(s, self.pos)
            if not m:
                continue
            pre = m.group(1)
            k = m.end()
            # the label runs to the first closing link
            j = k
            while j < len(s):
                c = close.match(s, j)
                if c and (c.end() >= len(s) or s[c.end()] in " \t" or ID_RE.match(s, c.end())):
                    break
                j += 1
            else:
                unsupported("labelled link not closed")
            raw = s[k:j]
            text = self.edge_text(raw)
            self.pos = c.end()
            end_char = c.group(2)
            kind = self.kind(line, pre, end_char if end_char in ">ox" else "")
            return kind, text, uid
        unsupported("expected a link at %r" % s[self.pos:self.pos + 20])

    def edge_text(self, raw):
        t = raw.strip()
        if len(t) >= 2 and t.startswith('"') and t.endswith('"') and '"' not in t[1:-1]:
            return norm_text(t[1:-1], True, "edge label")
        return norm_text(raw, False, "edge label")

    @staticmethod
    def kind(line, pre, post):
        end = HEADS.get(post, "none") if post else "none"
        start = HEADS.get(pre, "none") if pre else "none"
        if pre and HEADS.get(pre) != HEADS.get(post):
            unsupported("arrow with unmatched ends")
        k = (line, start, end)
        if k not in ALLOWED_KINDS:
            unsupported("arrow kind %s outside the subset" % (k,))
        return k

    # -- after the text ---------------------------------------------------
    def finish(self):
        db = self.db
        users = {e.id for e in db.edges if e.user}
        for e in db.edges:
            if e.start in users or e.end in users:
                unsupported("an edge end names a user-defined edge id")
        explicit = Counter(sg.rid for sg in db.subgraphs if sg.explicit)
        if any(n > 1 for n in explicit.values()):
            unsupported("two subgraphs share an explicit id")
        titles = Counter(sg.key for sg in db.subgraphs if not sg.explicit)
        dups = sorted(k for k, n in titles.items() if n > 1)
        if dups:
            unsupported("two subgraphs without an explicit id share a title", dup_titles=dups)


# --------------------------------------------------------------------------
# The model (section 4.1, Appendix A) as units (section 4.2)
# --------------------------------------------------------------------------
#
# Unit ids:
#   ("kind", key)                       identity: the key's kinds
#   ("prop", key, property)             a scalar
#   ("count", edgekey)                  an edge key's count (no user id)
#   ("member", kind, key)               membership: holder key or None
#   ("class", key, class)               a class assignment
#   ("classDef", name)                  a class definition
#   ("diagram", property)               header direction, linkStyle default
#   ("linkstyle", edgekey)              linkStyle styles of an edge key
# where edgekey = (from key, to key, (line, start head, end head), label).

EDGE_PROPS = {"from", "to", "type", "edgeLabel", "linkstyle"}
TEXT_PROPS = {"label", "title", "edgeLabel", "link", "linkTarget"}


def unit_class(u):
    t = u[0]
    if t == "kind":
        return "identity"
    if t == "count":
        return "relation"
    if t == "member":
        return "membership"
    if t == "prop":
        p = u[2]
        if p in ("from", "to", "type"):
            return "relation"
        if p in TEXT_PROPS:
            return "text"
        if p == "shape":
            return "shape"
        return "style"
    return "style"


def keyed_by(u):
    t = u[0]
    if t in ("kind", "prop", "class"):
        return u[1]
    if t == "member":
        return u[2]
    return None


def refs(u, value):
    """Keys a unit refers to (section 4.2); a membership's holder is not one."""
    out = []
    k = keyed_by(u)
    if k is not None:
        out.append(k)
    if u[0] in ("count", "linkstyle"):
        out.extend([u[1][0], u[1][1]])
    elif u[0] == "prop" and u[2] in ("from", "to") and isinstance(value, str):
        out.append(value)
    return out


class Model:
    def __init__(self, db):
        self.db = db
        self.units = {}
        self.node_order = []
        self.edge_order = []
        self.build()

    def build(self):
        db, U = self.db, self.units
        kinds = defaultdict(set)
        sub_by_rid = {sg.rid: sg for sg in db.subgraphs}

        def endkey(rid):
            if rid in sub_by_rid and rid not in db.has_stmt:
                return sub_by_rid[rid].key
            return rid
        self.endkey_fn = endkey

        holder = {}
        for sg in db.subgraphs:  # closing order
            for n in sg.nodes:
                if n != sg.rid and n not in holder:
                    holder[n] = sg.key

        for vid, v in db.vertices.items():
            if vid in sub_by_rid and vid not in db.has_stmt:
                continue  # an edge end referring to the subgraph
            kinds[vid].add("node")
            self.node_order.append(vid)
            U[("prop", vid, "label")] = (v.text if v.text is not None else vid).strip()
            U[("prop", vid, "shape")] = v.type if v.type is not None else "none"
            if v.link is not ABSENT:
                U[("prop", vid, "link")] = v.link
            if v.target is not ABSENT:
                U[("prop", vid, "linkTarget")] = v.target
            if v.styles:
                U[("prop", vid, "styles")] = tuple(v.styles)
            for c in v.classes:
                if c != "clickable":
                    U[("class", vid, c)] = True
            U[("member", "node", vid)] = holder.get(vid)

        for sg in db.subgraphs:
            kinds[sg.key].add("subgraph")
            U[("prop", sg.key, "title")] = sg.title
            if sg.dir:
                U[("prop", sg.key, "dir")] = sg.dir
            U[("member", "subgraph", sg.key)] = holder.get(sg.rid)

        styled = defaultdict(list)
        seen = Counter()
        for e in db.edges:
            fk, tk = endkey(e.start), endkey(e.end)
            if e.user:
                k = e.id
                kinds[k].add("edge")
                U[("prop", k, "from")] = fk
                U[("prop", k, "to")] = tk
                U[("prop", k, "type")] = e.kind
                U[("prop", k, "edgeLabel")] = e.text
                if e.style is not None:
                    U[("prop", k, "linkstyle")] = tuple(e.style)
                self.edge_order.append(("id", k))
            else:
                ek = (fk, tk, e.kind, e.text)
                U[("count", ek)] = U.get(("count", ek), 0) + 1
                if e.style is not None:
                    styled[ek].append(tuple(e.style))
                self.edge_order.append(("ek", ek, seen[ek]))
                seen[ek] += 1
        for ek, lst in styled.items():
            U[("linkstyle", ek)] = tuple(sorted(lst))

        for k, ks in kinds.items():
            U[("kind", k)] = tuple(sorted(ks))
        for name, styles in db.classdefs.items():
            U[("classDef", name)] = tuple(styles)
        U[("diagram", "direction")] = db.direction
        if db.link_default is not None:
            U[("diagram", "linkStyleDefault")] = tuple(db.link_default)

    # -- Appendix C lints, on this file alone ------------------------------
    def lints(self):
        db, out = self.db, set()
        endkey = self.endkey_fn
        node_keys = set(self.node_order)
        for k in self.node_order:
            if k not in db.has_stmt:
                out.add(("L1", k))
        for ident, stmts in db.node_stmts.items():
            labels = {lab for lab, _ in stmts if lab is not None}
            shapes = {sh for _, sh in stmts if sh is not None}
            if len(labels) > 1 or len(shapes) > 1:
                out.add(("L2", ident))
        blocks = defaultdict(set)
        for ident, seq in db.mentions:
            if seq is not None and ident in node_keys:
                blocks[ident].add(seq)
        for ident, seqs in blocks.items():
            if len(seqs) > 1:
                out.add(("L3", ident))
        txt = defaultdict(set)
        sub_rids = {sg.rid for sg in db.subgraphs}
        uids = set(db.written_uids)
        for ident in db.has_stmt:
            txt[ident].add("node")
        for sg in db.subgraphs:
            if sg.explicit:
                txt[sg.rid].add("subgraph")
        for uid in uids:
            txt[uid].add("edge")
        for ident in [m[0] for m in db.mentions] + db.style_targets:
            if ident in db.has_stmt or (ident not in sub_rids and ident not in uids):
                txt[ident].add("node")
        for u, v in self.units.items():
            if u[0] == "kind" and len(v) > 1:
                out.add(("L4", u[1]))
        for ident, ks in txt.items():
            if len(ks) > 1:
                out.add(("L4", ident))
        stmts = Counter()
        ends = {}
        for uid, s, e, kind, text in db.edge_stmts:
            fk, tk = endkey(s), endkey(e)
            key = ("id", uid) if uid else ("t", fk, tk, kind, text or "")
            stmts[key] += 1
            ends[key] = (fk, tk, uid)
        for key, n in stmts.items():
            if n > 1:
                fk, tk, uid = ends[key]
                for obj in (fk, tk, uid):
                    if obj:
                        out.add(("L5", obj))
        return out


# --------------------------------------------------------------------------
# Files: fences, conflict markers, H's verdict on each state
# --------------------------------------------------------------------------

def read_text(path):
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8", errors="replace")
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def mermaid_fences(text):
    lines = text.split("\n")
    fences = []
    i = 0
    while i < len(lines):
        m = FENCE_OPEN_RE.match(lines[i])
        if not m:
            # skip over other fenced blocks so their content is not read
            o = re.match(r"^( {0,3})(`{3,}|~{3,})", lines[i])
            if o:
                ch, n = o.group(2)[0], len(o.group(2))
                i += 1
                while i < len(lines) and not re.match(r"^ {0,3}%s{%d,}\s*$" % (re.escape(ch), n), lines[i]):
                    i += 1
            i += 1
            continue
        ch, n = m.group(2)[0], len(m.group(2))
        j = i + 1
        while j < len(lines) and not re.match(r"^ {0,3}%s{%d,}\s*$" % (re.escape(ch), n), lines[j]):
            j += 1
        fences.append("\n".join(lines[i + 1:j]))
        i = j + 1
    return fences


def choose_mode(stratum, paths, texts):
    p = paths[0].lower()
    if p.endswith((".md", ".markdown", ".mdx")):
        return "markdown"
    if p.endswith((".mmd", ".mermaid")):
        return "raw"
    if stratum == "D":
        return "markdown"
    return "markdown" if mermaid_fences(texts[0]) else "raw"


def state_of(text, mode):
    """(status, reason, model): status in ok/unsupported/noparse/notflowchart/fence."""
    if mode == "markdown":
        fences = mermaid_fences(text)
        if len(fences) != 1:
            return "fence", "%d Mermaid fences" % len(fences), None, {}
        diagram = fences[0]
    else:
        diagram = text
    try:
        db = Parser(diagram).parse()
    except HFail as f:
        return f.kind, f.reason, None, f.extra
    return "ok", None, Model(db), {}


# --------------------------------------------------------------------------
# The oracle (section 5)
# --------------------------------------------------------------------------

def decide(b, o, t):
    if o == t:
        return o
    if o == b:
        return t
    if t == b:
        return o
    return CONFLICT


def present(v):
    return v is not ABSENT and v is not CONFLICT


class Oracle:
    def __init__(self, B, O, T):
        self.B, self.O, self.T = B, O, T
        self.units = set(B.units) | set(O.units) | set(T.units)
        self.decided = {}
        self.conflicts = {}
        self.by_key = defaultdict(list)
        for u in self.units:
            b, o, t = (m.units.get(u, ABSENT) for m in (B, O, T))
            d = decide(b, o, t)
            if d is CONFLICT:
                self.conflicts[u] = (b, o, t)
            self.decided[u] = d
            k = keyed_by(u)
            if k is not None:
                self.by_key[k].append(u)
        self.keys = sorted({u[1] for u in self.units if u[0] == "kind"})
        self.undecided = {u for u in self.units if u[0] == "member" and self.membership_undecided(u)}
        self.refusals()
        self.exposure()

    def dkind(self, k):
        return self.decided.get(("kind", k), ABSENT)

    def holder_gone(self, h):
        if h is ABSENT or h is None or h is CONFLICT:
            return False
        d = self.dkind(h)
        return d is ABSENT or (d is not CONFLICT and "subgraph" not in d)

    def membership_undecided(self, u):
        vals = [self.decided[u]] + [m.units.get(u, ABSENT) for m in (self.B, self.O, self.T)]
        return any(self.holder_gone(h) for h in vals)

    def value(self, m, u):
        return m.units.get(u, ABSENT)

    # section 5.2
    def refusals(self):
        self.dangling = {}
        for u, d in self.decided.items():
            if not present(d) or u[0] in ("member", "kind"):
                continue
            for k in refs(u, d):
                if self.dkind(k) is ABSENT and any(self.value(m, ("kind", k)) is not ABSENT for m in (self.B, self.O, self.T)):
                    self.dangling.setdefault(k, []).append(u)
        self.collision = {}
        self.delmod = {}
        for k in self.keys:
            kb, ko, kt = (self.value(m, ("kind", k)) for m in (self.B, self.O, self.T))
            units = [u for u in self.by_key[k] if u not in self.undecided]
            if kb is ABSENT and ko is not ABSENT and kt is not ABSENT:
                diff = [u for u in units if self.value(self.O, u) != self.value(self.T, u)]
                if diff:
                    self.collision[k] = diff
            if kb is not ABSENT:
                for gone, other, remover in ((ko, self.T, "o"), (kt, self.O, "t")):
                    if gone is ABSENT and self.value(other, ("kind", k)) is not ABSENT:
                        changed = [u for u in units if self.value(other, u) != self.value(self.B, u)]
                        if changed:
                            self.delmod[k] = {"removed_by": remover, "changed": changed}
        self.refusal_keys = set(self.collision) | set(self.delmod)

    # section 5.5, from B, O and T only
    def exposure(self):
        reasons = []
        B, O, T = self.B, self.O, self.T
        for leg, other, lname, oname in ((O, T, "o", "t"), (T, O, "t", "o")):
            removed = {k for k in self.keys
                       if self.value(B, ("kind", k)) is not ABSENT and self.value(leg, ("kind", k)) is ABSENT}
            if not removed:
                continue
            for u, v in other.units.items():
                if u[0] == "member" and u in self.undecided:
                    continue
                if v == self.value(B, u):
                    continue
                hit = [k for k in refs(u, v) if k in removed]
                for k in hit:
                    reasons.append({"rule": "removed-and-referenced", "key": k,
                                    "removed_by": lname, "unit": unit_json(u), "by": oname})
        for k in self.keys:
            if (self.value(B, ("kind", k)) is ABSENT and self.value(O, ("kind", k)) is not ABSENT
                    and self.value(T, ("kind", k)) is not ABSENT):
                diff = [u for u in self.by_key[k] if self.value(O, u) != self.value(T, u)]
                if diff:
                    reasons.append({"rule": "both-add-differing", "key": k,
                                    "units": [unit_json(u) for u in sorted(diff, key=sort_key)]})
        reasons.sort(key=lambda r: json.dumps(r, sort_keys=True))
        self.exposed = bool(reasons)
        self.exposure_reasons = reasons


# --------------------------------------------------------------------------
# Records (section 5.3) and tiers (section 5.4)
# --------------------------------------------------------------------------

def sort_key(u):
    return json.dumps(unit_json(u), sort_keys=True)


def jv(v):
    if v is ABSENT or v is CONFLICT:
        return None
    if isinstance(v, tuple):
        return [jv(x) for x in v]
    return v


def ek_json(ek):
    return {"from": ek[0], "to": ek[1], "kind": list(ek[2]), "label": ek[3]}


def unit_json(u):
    t = u[0]
    if t == "kind":
        return {"unit": "kind", "key": u[1]}
    if t == "prop":
        return {"unit": "scalar", "key": u[1], "property": u[2]}
    if t == "count":
        return {"unit": "edge-count", "edge": ek_json(u[1])}
    if t == "member":
        return {"unit": "membership", "kind": u[1], "key": u[2]}
    if t == "class":
        return {"unit": "class", "key": u[1], "class": u[2]}
    if t == "classDef":
        return {"unit": "scalar", "classDef": u[1], "property": "styles"}
    if t == "diagram":
        return {"unit": "scalar", "diagram": True, "property": u[1]}
    if t == "linkstyle":
        return {"unit": "scalar", "edge": ek_json(u[1]), "property": "linkstyle"}
    raise ValueError(u)


def value_json(u, v):
    if v is ABSENT:
        return {"absent": True, "value": 0 if u[0] == "count" else None}
    return {"absent": False, "value": jv(v)}


def count_of(v):
    return 0 if v is ABSENT else v


def unit_objects(u, values):
    """A record's objects for a unit (section 5.3), from its values."""
    t = u[0]
    if t in ("count", "linkstyle"):
        return [u[1][0], u[1][1]]
    if t == "classDef":
        return ["classDef:" + u[1]]
    if t == "diagram":
        return []
    k = keyed_by(u)
    objs = [k]
    if t == "member":
        objs += [h for h in values if isinstance(h, str)]
    return objs


def build_records(orc, M, path, new_lints):
    D = orc.decided
    B, O, T = orc.B, orc.O, orc.T
    recs = []

    def add(cat, group, tier, objects, **extra):
        r = {"category": cat, "group": group, "tier": tier,
             "objects": sorted({o for o in objects if o})}
        r.update(extra)
        recs.append(r)

    def edge_ends(k, *models):
        out = []
        for m in models:
            for p in ("from", "to"):
                v = m.get(("prop", k, p), ABSENT) if isinstance(m, dict) else m.units.get(("prop", k, p), ABSENT)
                if isinstance(v, str):
                    out.append(v)
        return out

    mk = lambda k: M.units.get(("kind", k), ABSENT)

    # identity group
    i_objects = set()
    for k in sorted(orc.dangling):
        objs = {k}
        for u in orc.dangling[k]:
            objs.update(refs(u, D[u]))
            if u[0] == "prop" and u[2] in EDGE_PROPS:
                objs.update(edge_ends(u[1], D))
        add("I1", "identity", "A", objs, key=k,
            units=[unit_json(u) for u in sorted(orc.dangling[k], key=sort_key)])
        i_objects |= objs
    for k in sorted(orc.collision):
        add("I2", "identity", "A", [k], key=k,
            units=[unit_json(u) for u in sorted(orc.collision[k], key=sort_key)])
        i_objects.add(k)
    for k in sorted(orc.delmod):
        add("I3", "identity", "A", [k], key=k, removed_by=orc.delmod[k]["removed_by"],
            units=[unit_json(u) for u in sorted(orc.delmod[k]["changed"], key=sort_key)])
        i_objects.add(k)

    all_keys = sorted(set(orc.keys) | {u[1] for u in M.units if u[0] == "kind"})
    kind_diff = {}  # key -> set of kinds whose presence differs
    for k in all_keys:
        d, m = orc.dkind(k), mk(k)
        inputs = [x.units.get(("kind", k), ABSENT) for x in (B, O, T)]
        if m is not ABSENT:
            # no input gives two kinds, and the merged model has two kinds
            two = len(m) > 1 and all(x is ABSENT or len(x) == 1 for x in inputs)
            # no input gives a kind other than the decided kind, and the merged kind differs
            other = present(d) and m != d and all(x is ABSENT or (len(x) == 1 and x == d) for x in inputs)
            if two or other:
                add("I4", "identity", "A", [k], key=k, decided=jv(d), merged=jv(m))
                i_objects.add(k)
        if d is CONFLICT:
            continue
        ds = set(d) if present(d) else set()
        ms = set(m) if m is not ABSENT else set()
        if ds != ms:
            kind_diff[k] = ds ^ ms
    for k, kinds in sorted(kind_diff.items()):
        ds = set(orc.dkind(k)) if present(orc.dkind(k)) else set()
        if "node" in kinds and k not in i_objects:
            add("G1", "structure", "A", [k], key=k,
                detail="absent" if "node" in ds else "present")
        if "edge" in kinds:
            objs = [k] + edge_ends(k, D, M)
            lost = "edge" in ds
            add("G2", "structure", "A", objs, edge_id=k, detail="lost" if lost else "extra", count=1)

    # structure group and the rest, unit by unit
    style_values_d = Counter()
    style_values_m = Counter()
    for u, v in D.items():
        if (u[0] == "linkstyle" or (u[0] == "prop" and u[2] == "linkstyle")) and present(v):
            for st in (v if u[0] == "linkstyle" else (v,)):
                style_values_d[st] += 1
    for u, v in M.units.items():
        if u[0] == "linkstyle" or (u[0] == "prop" and u[2] == "linkstyle"):
            for st in (v if u[0] == "linkstyle" else (v,)):
                style_values_m[st] += 1

    units = sorted((set(D) | set(M.units)), key=sort_key)
    for u in units:
        if u[0] == "kind":
            continue
        d = D.get(u, ABSENT)
        m = M.units.get(u, ABSENT)
        if u in orc.undecided:
            continue
        cls = unit_class(u)
        if d is CONFLICT:
            if keyed_by(u) in orc.refusal_keys:
                continue
            b, o, t = orc.conflicts[u]
            eligible = m != o and m != t
            group = {"identity": "identity", "relation": "structure", "membership": "structure",
                     "text": "structure", "shape": "other", "style": "other"}[cls]
            tier = {"identity": "A", "relation": "A", "membership": "A", "text": "A",
                    "shape": "C", "style": "D"}[cls] if eligible else "-"
            add("MC", group, tier, unit_objects(u, (b, o, t, m)), **{
                "class": cls, "eligible": eligible, "unit": unit_json(u),
                "base": value_json(u, b), "o": value_json(u, o), "t": value_json(u, t),
                "merged": value_json(u, m)})
            continue
        if d == m:
            continue
        base = {"class": cls, "unit": unit_json(u), "decided": value_json(u, d), "merged": value_json(u, m)}
        if cls == "relation":
            if u[0] == "count":
                dc, mc = count_of(d), count_of(m)
                add("G2", "structure", "A", unit_objects(u, ()), detail="lost" if mc < dc else "extra",
                    count=abs(dc - mc), **base)
            else:
                add("G2", "structure", "A", [u[1]] + edge_ends(u[1], D, M), detail="changed", **base)
        elif cls == "membership":
            add("G3", "structure", "A", unit_objects(u, (d, m)), **base)
        elif cls == "text":
            objs = [u[1]]
            if u[2] == "edgeLabel":
                objs += edge_ends(u[1], D)
            add("G4", "structure", "A", objs, **base)
        elif cls == "shape":
            add("C", "other", "C", unit_objects(u, ()), **base)
        else:
            cat = "D"
            if u[0] == "linkstyle" or (u[0] == "prop" and u[2] == "linkstyle"):
                dv = set(d if u[0] == "linkstyle" else (d,)) if present(d) else set()
                mv = set(m if u[0] == "linkstyle" else (m,)) if m is not ABSENT else set()
                moved = any(style_values_m[s] for s in dv - mv) or any(style_values_d[s] for s in mv - dv)
                if moved:
                    cat = "S-LINKSTYLE"
            objs = unit_objects(u, ())
            if u[0] == "prop" and u[2] == "linkstyle":
                objs += edge_ends(u[1], D)
            add(cat, "other", "D", objs, **base)

    # S-ORDER
    for name, seqs in (("nodes", [x.node_order for x in (B, O, T, M)]),
                       ("edges", [x.edge_order for x in (B, O, T, M)])):
        if order_differs(*seqs):
            add("S-ORDER", "other", "-", [path], sequence=name)

    # tier B: an A record one of whose objects newly fails a lint (row 1)
    lint_objs = defaultdict(set)
    for lint, obj in new_lints:
        lint_objs[obj].add(lint)
    for r in recs:
        if r["tier"] != "A":
            continue
        hits = sorted({(lint, o) for o in r["objects"] for lint in lint_objs.get(o, ())})
        if hits:
            r["tier"] = "B"
            r["new_lints"] = [list(h) for h in hits]
    return recs


ORDER_PAIR_LIMIT = 1500


def order_differs(b, o, t, m):
    """S-ORDER: a pair the merged order puts the other way round from the decided order."""
    pos = [{x: i for i, x in enumerate(seq)} for seq in (b, o, t)]
    if len(m) > ORDER_PAIR_LIMIT:
        pairs = ((m[i], m[i + 1]) for i in range(len(m) - 1))
    else:
        pairs = ((m[i], m[j]) for i in range(len(m)) for j in range(i + 1, len(m)))
    for x, y in pairs:
        rel = []
        for p in pos:
            if x in p and y in p:
                rel.append(p[x] < p[y])
            else:
                rel.append(None)
        d = decide(*rel)
        if d is False:
            return True
    return False


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def tier_counts(records):
    c = Counter(r["tier"] for r in records)
    return {k: c[k] for k in sorted(c)}


def main(argv):
    if len(argv) != 6:
        sys.stderr.write("usage: extract2.py <stratum> <base> <o> <t> <merged>\n")
        return 2
    stratum = argv[1]
    paths = argv[2:6]
    texts = [read_text(p) for p in paths]
    mode = choose_mode(stratum, paths, texts)
    names = ("base", "o", "t", "merged")
    states = [state_of(tx, mode) for tx in texts]

    out = {
        "extractor": "extract2",
        "stratum": stratum,
        "mode": mode,
        "path": paths[3],
        "states": {},
        "outcome": None,
        "decided": None,
        "conflicts": None,
        "undecided_memberships": None,
        "refusal_cases": None,
        "exposure": None,
        "new_lint_failures": None,
        "records": [],
    }
    for name, (status, reason, _m, _x) in zip(names, states):
        out["states"][name] = {"in_subset": status == "ok", "status": status, "reason": reason}

    inputs_ok = all(st[0] == "ok" for st in states[:3])
    orc = None
    if inputs_ok:
        B, O, T = (st[2] for st in states[:3])
        orc = Oracle(B, O, T)
        out["decided"] = [dict(unit_json(u), **value_json(u, orc.decided[u]))
                          for u in sorted(orc.decided, key=sort_key)
                          if orc.decided[u] is not CONFLICT and u not in orc.undecided]
        out["conflicts"] = [dict(unit_json(u), base=value_json(u, b), o=value_json(u, o), t=value_json(u, t))
                            for u, (b, o, t) in sorted(orc.conflicts.items(), key=lambda kv: sort_key(kv[0]))
                            if u not in orc.undecided]
        out["undecided_memberships"] = [unit_json(u) for u in sorted(orc.undecided, key=sort_key)]
        out["refusal_cases"] = (
            [{"case": "dangling", "key": k, "units": [unit_json(u) for u in sorted(v, key=sort_key)]}
             for k, v in sorted(orc.dangling.items())]
            + [{"case": "collision", "key": k, "units": [unit_json(u) for u in sorted(v, key=sort_key)]}
               for k, v in sorted(orc.collision.items())]
            + [{"case": "delete/modify", "key": k, "removed_by": v["removed_by"],
                "units": [unit_json(u) for u in sorted(v["changed"], key=sort_key)]}
               for k, v in sorted(orc.delmod.items())])
        out["exposure"] = {"exposed": orc.exposed, "reasons": orc.exposure_reasons}

    merged_text = texts[3]
    mstatus, mreason, M, mextra = states[3]
    path = paths[3]

    if CONFLICT_RE.search(merged_text):
        out["outcome"] = "E"
        out["records"] = [{"category": "E", "group": "other", "tier": "E", "objects": [path],
                           "reason": "conflict marker in the merged file"}]
    elif mstatus == "noparse":
        out["outcome"] = "E"
        out["records"] = [{"category": "E", "group": "other", "tier": "E", "objects": [path],
                           "reason": "R does not parse the merged diagram: " + mreason}]
    elif not inputs_ok:
        out["outcome"] = "INPUT-OUT-OF-SUBSET"
    elif mstatus in ("fence", "notflowchart"):
        out["outcome"] = "G0"
        out["records"] = [{"category": "G0", "group": "structure", "tier": "B", "objects": [path],
                           "reason": mreason}]
    elif mstatus == "unsupported":
        dups = mextra.get("dup_titles") or []
        both_added = dups and all(
            orc.value(orc.B, ("kind", k)) is ABSENT and orc.value(orc.O, ("kind", k)) is not ABSENT
            and orc.value(orc.T, ("kind", k)) is not ABSENT for k in dups)
        if both_added:
            out["outcome"] = "DUP-TITLE"
            out["records"] = [{"category": "DUP-TITLE", "group": "other", "tier": "-",
                               "objects": sorted(dups), "exposed": orc.exposed}]
        else:
            out["outcome"] = "OUT-OF-SUBSET"
            out["records"] = [{"category": "OUT-OF-SUBSET", "group": "other", "tier": "-",
                               "objects": [path], "reason": mreason}]
    else:
        lint_in = set()
        for st in states[:3]:
            lint_in |= st[2].lints()
        new = sorted(M.lints() - lint_in)
        out["new_lint_failures"] = [list(x) for x in new]
        out["outcome"] = "decided"
        out["records"] = build_records(orc, M, path, new)

    out["tiers"] = tier_counts(out["records"])
    sys.stdout.write(json.dumps(out, sort_keys=True, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
