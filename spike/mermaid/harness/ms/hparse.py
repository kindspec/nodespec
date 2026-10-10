# SPDX-License-Identifier: MIT
"""H, the harness parser (PRE-REGISTRATION.md §4.3). Pure stdlib.

H accepts the subset in Appendix A and nothing else. It emulates, for that
subset, what Mermaid 12.1.0 does with a flowchart text:

- the preprocessing Mermaid applies before its grammar runs (CRLF, a leading
  `---` front-matter block, `%%{...}%%` directives, `%%` comment lines,
  `encodeEntities`, a trailing newline);
- the jison lexer of `flow.jison` at mermaid@12.1.0, rule by rule and in file
  order, with its exclusive start states;
- the grammar, by recursive descent, calling the same database operations
  FlowDB does (`addVertex`, `addLink`, `addSubGraph`, `setClass`, ...).

Anything outside Appendix A raises Refuse with the construct's name; anything
H cannot follow raises Refuse("unparsed: ..."). Both mean "not in the subset";
the name is what Arm 0 counts. H never guesses: where it is unsure what
Mermaid's sanitizer or URL normalizer would print, it refuses.

A blob is in the subset only if H parses it AND H's model equals R's model
(ms/model.py); H's agreement with Mermaid is checked there, not assumed here.
Besides the model, H records what only the statements show, for Appendix C's
lints and Appendix A's "node statement": every node statement with its label
and shape, the ids mentioned directly in each subgraph block, and the ids used
as edge ids.
"""
import re

from . import flowlex as FL

__all__ = ["Refuse", "parse", "preprocess"]


class Refuse(Exception):
    """Not in the subset. args[0] is the refused construct's name."""


# ------------------------------------------------------------- preprocessing

_TAG_ATTR = re.compile(r"<(\w+)([^>]*)>", re.ASCII)
_DIRECTIVE = re.compile(r"%{2}{\s*(?:(\w+)\s*:|(\w+))\s*(?:(\w+)|((?:(?!}%{2}).|\r?\n)*))?\s*(?:}%{2})?",
                        re.IGNORECASE)
_COMMENT = re.compile(r"^\s*%%(?!{)[^\n]+\n?", re.MULTILINE)
_ENT_STYLE = re.compile(r"style.*:\S*#.*;")
_ENT_CLASSDEF = re.compile(r"classDef.*:\S*#.*;")
_ENT = re.compile(r"#[A-Za-z0-9_]+;")


def _encode_entities(t):
    t = _ENT_STYLE.sub(lambda m: m.group(0)[:-1], t)
    t = _ENT_CLASSDEF.sub(lambda m: m.group(0)[:-1], t)

    def enc(m):
        inner = m.group(0)[1:-1]
        if re.fullmatch(r"\+?\d+", inner):
            return "ﬂ°°" + inner + "¶ß"
        return "ﬂ°" + inner + "¶ß"
    return _ENT.sub(enc, t)


def preprocess(text):
    """The text Mermaid's grammar sees: cleanupText, front matter, directives,
    comments, encodeEntities, plus a newline."""
    if " " in text or " " in text:
        raise Refuse("unicode line separator")
    t = re.sub(r"\r\n?", "\n", text)
    t = _TAG_ATTR.sub(lambda m: "<" + m.group(1) + re.sub(r'="([^"]*)"', r"='\1'", m.group(2)) + ">", t)
    lines = t.split("\n")
    if lines and lines[0].rstrip(" \t") == "---":
        # Appendix A: leading front matter, read as configuration and ignored.
        # Only the plain form: '---' on the first line, closed by a '---' line.
        for i in range(1, len(lines)):
            if lines[i].rstrip(" \t") == "---":
                t = "\n".join(lines[i + 1:])
                break
        else:
            raise Refuse("unclosed front matter")
    elif t.lstrip(" \t\n").startswith("---"):
        raise Refuse("front matter not on the first line")
    t = _DIRECTIVE.sub("", t)
    t = _COMMENT.sub("", t).lstrip()
    if '"`' in t:
        raise Refuse("markdown string")
    return _encode_entities(t) + "\n"


# --------------------------------------------------------------------- lexer

class Tok:
    __slots__ = ("t", "v")

    def __init__(self, t, v):
        self.t, self.v = t, v

    def __repr__(self):
        return f"{self.t}({self.v!r})"


_COMPILED = None


def _compiled():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = [re.compile(r) for r in FL.RULES]
    return _COMPILED


_SD_TEXT = re.compile(r'[^}^"]+')


def _shape_data(src, i):
    r"""Lex `@{ ... }` as the shapeData and shapeDataStr states do (rules 8 to
    12): returns (text, end). A string's `\n\s*` becomes <br/>."""
    out = []
    while True:
        if i >= len(src):
            raise Refuse("unparsed: unterminated @{")
        c = src[i]
        if c == "}":
            return "".join(out), i + 1
        if c == '"':
            j = src.find('"', i + 1)
            if j < 0:
                raise Refuse("unparsed: unterminated string in @{")
            out.append('"' + re.sub(r"\n\s*", "<br/>", src[i + 1:j]) + '"')
            i = j + 1
            continue
        m = _SD_TEXT.match(src, i)
        if not m:
            raise Refuse("unparsed: @{ ... }")
        out.append(m.group(0))
        i = m.end()


def lex(src):
    """Mermaid's lexer on the preprocessed text: a list of Tok, ending EOF."""
    rules = _compiled()
    stack = ["INITIAL"]
    first_graph = True
    toks, i, n = [], 0, len(src)
    while i < n:
        for k in FL.CONDITIONS[stack[-1]]:
            m = rules[k].match(src, i)
            if m:
                break
        else:
            raise Refuse(f"unparsed: no lexer rule at {src[i:i + 12]!r} in state {stack[-1]}")
        v, end = m.group(0), m.end()
        act = FL.ACTIONS[k]
        op = act[0]
        if op == "refuse":
            raise Refuse(act[1])
        if op == "shapedata":
            v, end = _shape_data(src, end)
            toks.append(Tok("SHAPE_DATA", v))
        elif op == "tok":
            toks.append(Tok(act[1], v))
        elif op == "tokpop":
            toks.append(Tok(act[1], v))
            if len(stack) > 1:
                stack.pop()
        elif op == "tokpush":
            toks.append(Tok(act[1], v))
            stack.append(act[2])
        elif op == "push":
            stack.append(act[1])
        elif op == "pop":
            if len(stack) > 1:
                stack.pop()
        elif op == "graph":
            toks.append(Tok("GRAPH", v))
            if first_graph:
                first_graph = False
                stack.append("dir")
        elif op == "eof":
            break
        if end == i:
            # Only `<click>[^\s\n]*` and `$` can match empty, and neither
            # can before the end of the input.
            raise Refuse("unparsed: empty lexer match")
        i = end
    toks.append(Tok("EOF", ""))
    return toks


# ------------------------------------------------------------- the database

_DOMPURIFY_TAGS = {"b", "i", "em", "strong", "u", "sub", "sup", "small", "code", "s", "del", "mark"}


def _sanitize(t):
    """common.sanitizeText under §4.4's configuration (htmlLabels false, so
    sanitizeMore is a no-op): DOMPurify.sanitize(t, {FORBID_TAGS: [style]}).
    DOMPurify returns a string without '<' unchanged. With '<', H accepts only
    <br> forms and a few plain lower-case tags, balanced, and no '&', stray
    '>' or no-break space, which DOMPurify's serializer would escape."""
    if not t or "<" not in t:
        return t
    if "&" in t or "\u00a0" in t:
        raise Refuse("label with '<' and '&' or a no-break space")
    out, pos, stack = [], 0, []
    for m in re.finditer(r"<(/?)([A-Za-z]+)( ?/?)>", t):
        out.append(t[pos:m.start()])
        close, name, tail = m.group(1), m.group(2), m.group(3)
        if name.lower() == "br" and not close:
            out.append("<br>")
        elif name in _DOMPURIFY_TAGS and not tail:
            if close:
                if not stack or stack[-1] != name:
                    raise Refuse("label with an unbalanced tag")
                stack.pop()
            else:
                stack.append(name)
            out.append(m.group(0))
        else:
            raise Refuse("label with an html tag H does not model")
        pos = m.end()
    out.append(t[pos:])
    if stack:
        raise Refuse("label with an unbalanced tag")
    if any("<" in x or ">" in x for x in out[::2]):
        raise Refuse("label with a stray '<' or '>'")
    return "".join(out)


def _format_url(s):
    """utils.formatUrl under securityLevel strict: @braintree/sanitize-url
    7.1.2. H follows its plain paths only, and refuses the rest."""
    url = s.strip()
    if not url:
        return None
    if re.search(r"[%\x00-\x1f\x7f-\x9f -‍﻿]|&#|&(?:newline|tab);|\\[nrt]|\s", url, re.I):
        raise Refuse("click url H does not normalize")
    if url[0] in "./":
        return url
    m = re.match(r"^.+(:|&colon;)", url)
    if not m:
        return url
    scheme = m.group(0).lower().strip()
    if re.match(r"^([^\w]*)(javascript|data|vbscript)", scheme, re.I | re.M):
        return "about:blank"
    back = url.replace("\\", "/")
    if scheme == "mailto:" or "://" in scheme:
        return back
    if scheme in ("http:", "https:"):
        m2 = re.fullmatch(r"(https?)://([A-Za-z0-9.-]+)(/[A-Za-z0-9\-._~/]*)?(\?[A-Za-z0-9\-._~/=&+]*)?(#[A-Za-z0-9\-._~/=&+]*)?",
                          back, re.I)
        if not m2 or not m2.group(2) or ".." in m2.group(2) or m2.group(2).startswith(".") \
                or m2.group(2).endswith(".") or re.search(r"(^|/)\.{1,2}(/|$)", m2.group(3) or ""):
            raise Refuse("click url H does not normalize")
        return (m2.group(1).lower() + "://" + m2.group(2).lower() + (m2.group(3) or "/")
                + (m2.group(4) or "") + (m2.group(5) or ""))
    return back


_VALID_SHAPES = None


def _valid_shapes():
    # Mermaid 12.1.0's shape names for `@{ shape: ... }` (shapes.ts), with
    # each alias; anything else throws "No such shape" in R.
    global _VALID_SHAPES
    if _VALID_SHAPES is None:
        _VALID_SHAPES = set("""
        rect rounded stadium fr-rect subproc subprocess subroutine framed-rectangle cyl db database
        cylinder circle circ bang notch-pent prepare hexagon hex lean-r lean-right in-out lean-l
        lean-left out-in trap-b trapezoid-bottom priority trapezoid trap-t trapezoid-top
        inv-trapezoid manual dbl-circ double-circle diam diamond decision question sm-circ
        small-circle start fr-circ stop framed-circle f-circ junction filled-circle fork join
        hourglass collate brace comment brace-l brace-r braces bolt com-link lightning-bolt doc
        document delay half-rounded-rectangle h-cyl das horizontal-cylinder lin-cyl disk
        lined-cylinder curv-trap curved-trapezoid display div-rect div-proc divided-rectangle
        divided-process tri extract triangle win-pane internal-storage window-pane lin-rect
        lin-proc lined-process lined-rectangle shaded-process notch-rect card notched-rectangle
        docs documents st-doc stacked-document flip-tri flipped-triangle manual-file sl-rect
        manual-input sloped-rectangle processes procs st-rect stacked-rectangle flag paper-tape
        cross-circ summary bow-rect bow-tie-rectangle stored-data tag-doc tagged-document
        tag-rect tag-proc tagged-process tagged-rectangle text odd anchor
        """.split())
    return _VALID_SHAPES


def _shape_doc(s):
    """The `@{ ... }` body, as js-yaml would read the subset's forms: comma or
    newline separated `key: value`, values bare or double-quoted. Appendix A:
    keys other than shape and label are out of the subset."""
    body = s.strip()
    out = {}
    # R reads a one-line body as a YAML flow mapping, and a multi-line one as
    # a block mapping, where a comma is part of the value.
    sep = "\n" if "\n" in body else ","
    parts = re.findall(r'(?:[^"' + sep + r']|"[^"]*")+', body)
    if sep == "\n" and any("," in re.sub(r'"[^"]*"', "", p) for p in parts):
        raise Refuse("@{ } H does not read")
    for p in [p for p in parts if p.strip()]:
        m = re.fullmatch(r'\s*([A-Za-z]+)\s*:\s*(?:"([^"\\]*)"|([^"\s][^"]*?))\s*', p)
        if not m:
            raise Refuse("@{ } H does not read")
        k = m.group(1)
        if k not in ("shape", "label"):
            raise Refuse(f"@{{ }} key {k}")
        if k in out:
            raise Refuse("@{ } repeated key")
        v = m.group(2) if m.group(2) is not None else m.group(3)
        if m.group(3) is not None and (v[0] in "-?:,[]{}#&*!|>'%@`" or re.search(r"[\[\]{}]|: | #|:$", v)
                                       or re.fullmatch(r"-?\d+(\.\d+)?([eE][-+]?\d+)?|true|false|null", v)):
            raise Refuse("@{ } value H does not read")
        out[k] = v
    return out


class DB:
    """FlowDB's state for the subset, with H's statement-level records."""

    def __init__(self):
        self.vertices = {}      # id -> dict, in insertion order (a JS Map)
        self.edges = []
        self.subgraphs = []     # closing order
        self.sub_lookup = {}
        self.classdefs = {}
        self.sub_count = 0
        # statement-level, for Appendix A's node statement and Appendix C
        self.node_statements = {}   # id -> [(label or None, shape or None)]
        self.block_mentions = []    # [(subgraph id, set of ids mentioned directly)]
        self.edge_id_uses = set()
        self.edge_id_attempts = {}  # user edge id -> edges that asked for it
        self.swallowed = set()      # ids R dropped as nodes: an earlier edge id
        self.headers = []           # (subgraph id, explicit: bool)

    def add_vertex(self, vid, text=None, ttype=None, vtype=None, styles=None, classes=None, doc=None,
                   statement=False):
        if not vid or not vid.strip():
            return
        if doc is not None and vid in self.sub_lookup:
            raise Refuse("@{ } on a subgraph id")
        if any(e["id"] == vid for e in self.edges):
            self.swallowed.add(vid)
            return  # R drops a vertex whose id is an earlier edge id (probe edgeIdThenNode)
        v = self.vertices.get(vid)
        if v is None:
            v = {"id": vid, "text": None, "type": None, "classes": [], "styles": [], "link": None,
                 "linkTarget": None}
            self.vertices[vid] = v
        if text is not None:
            txt = _sanitize(text.strip())
            if len(txt) >= 2 and txt.startswith('"') and txt.endswith('"'):
                txt = txt[1:-1]
            v["text"] = txt
        elif v["text"] is None:
            v["text"] = vid
        if vtype is not None:
            v["type"] = vtype
        if styles:
            v["styles"].extend(styles)
        if classes:
            v["classes"].extend(classes)
        if doc is not None:
            if "shape" in doc:
                sh = doc["shape"]
                if sh != sh.lower() or "_" in sh or sh not in _valid_shapes():
                    raise Refuse("@{ shape } H does not know")
                v["type"] = sh
            if doc.get("label"):
                v["text"] = doc["label"]
        if statement:
            self.node_statements.setdefault(vid, []).append(
                (v["text"] if (text is not None or (doc or {}).get("label")) else None,
                 vtype if vtype is not None else (doc or {}).get("shape")))

    def add_single_link(self, start, end, link, eid):
        e = {"start": start, "end": end, "type": link["type"], "stroke": link["stroke"],
             "text": "", "style": None, "id": None, "user": False, "want_id": eid}
        if eid:
            self.edge_id_attempts[eid] = self.edge_id_attempts.get(eid, 0) + 1
        if link.get("text") is not None:
            t = _sanitize(link["text"].strip())
            if len(t) >= 2 and t.startswith('"') and t.endswith('"'):
                t = t[1:-1]
            e["text"] = t
        if eid and not any(x["id"] == eid for x in self.edges):
            e["id"], e["user"] = eid, True
        else:
            n = sum(1 for x in self.edges if x["start"] == start and x["end"] == end)
            e["id"] = f"L_{start}_{end}_{0 if n == 0 else n + 1}"
        if len(self.edges) >= 100000:
            raise Refuse("over 100,000 edges")
        self.edges.append(e)

    def add_link(self, starts, ends, link):
        eid = link["id"].replace("@", "", 1) if link.get("id") else None
        if eid:
            self.edge_id_uses.add(eid)
        for s in starts:
            for t in ends:
                if s == starts[-1] and t == ends[0]:
                    self.add_single_link(s, t, link, eid)
                else:
                    self.add_single_link(s, t, link, None)

    def set_class(self, ids, cls):
        for i in ids.split(","):
            if i in self.vertices:
                self.vertices[i]["classes"].append(cls)

    def add_class(self, ids, styles):
        joined = ",".join(styles).replace("\\,", "§§§").replace(",", ";").replace(
            "§§§", ",").split(";")
        for i in ids.split(","):
            self.classdefs.setdefault(i, []).extend(joined)

    def update_link(self, positions, styles):
        for p in positions:
            if p == "default":
                continue  # edges.defaultStyle: not in Appendix A's model
            if p >= len(self.edges):
                raise Refuse("linkStyle index out of range")
            st = list(styles)
            if st and not any(s.startswith("fill") for s in st):
                st.append("fill:none")
            self.edges[p]["style"] = st

    def set_link(self, ids, url, target):
        for i in ids.split(","):
            v = self.vertices.get(i)
            if v is not None:
                v["link"] = _format_url(url)
                v["linkTarget"] = target
        self.set_class(ids, "clickable")

    def add_subgraph(self, id_obj, items, title_obj, explicit_form):
        sid = id_obj["text"].strip() if id_obj is not None else None
        title = title_obj["text"] if title_obj is not None else None
        if id_obj is not None and id_obj is title_obj and re.search(r"\s", title_obj["text"]):
            sid = None
        seen, nodes = set(), []
        for it in items:
            if not isinstance(it, str) or it.strip() == "" or it in seen:
                continue
            seen.add(it)
            nodes.append(it)
        if sid is None:
            sid = f"subGraph{self.sub_count}"
            explicit = False
        else:
            explicit = True
            if re.fullmatch(r"subGraph\d+", sid):
                raise Refuse("explicit subgraph id subGraphN")
        title = _sanitize(title or "").strip()
        self.sub_count += 1
        nodes = [x for x in nodes if not any(x in sg["nodes"] for sg in self.subgraphs)]
        nodes = [x for x in nodes if x != sid]
        existing = next((sg for sg in self.subgraphs if sg["id"] == sid), None)
        if existing is not None:
            existing["nodes"].extend(nodes)
            self.sub_lookup[sid] = existing
        else:
            sg = {"id": sid, "title": title, "nodes": nodes}
            self.subgraphs.append(sg)
            self.sub_lookup[sid] = sg
        self.headers.append((sid, explicit))
        return sid


# -------------------------------------------------------------------- parser

_ID_TOKENS = {"NUM", "NODE_STRING", "DOWN", "MINUS", "DEFAULT", "COMMA", "COLON", "AMP", "BRKT",
              "MULT", "UNICODE_TEXT"}
_KEYWORDS = {"STYLE", "LINKSTYLE", "CLASSDEF", "CLASS", "CLICK", "GRAPH", "DIR", "subgraph", "end",
             "DOWN", "UP"}
_TEXT_NOTAGS = {"NUM", "NODE_STRING", "SPACE", "MINUS", "AMP", "UNICODE_TEXT", "COLON", "MULT",
                "BRKT", "START_LINK"} | _KEYWORDS
_STYLE_COMPONENTS = {"NUM", "NODE_STRING", "COLON", "SPACE", "BRKT", "STYLE"}
_ALPHANUM = {"NUM", "UNICODE_TEXT", "NODE_STRING", "DIR", "DOWN", "MINUS", "COMMA", "COLON", "AMP",
             "BRKT", "MULT"}
# (start token, [middle start tokens], end token, shape)
_SHAPES = {
    "SQS": "square", "DOUBLECIRCLESTART": "doublecircle", "STADIUMSTART": "stadium",
    "SUBROUTINESTART": "subroutine", "CYLINDERSTART": "cylinder", "TAGEND": "odd",
}
_SHAPE_END = {"SQS": "SQE", "DOUBLECIRCLESTART": "DOUBLECIRCLEEND", "STADIUMSTART": "STADIUMEND",
              "SUBROUTINESTART": "SUBROUTINEEND", "CYLINDERSTART": "CYLINDEREND", "TAGEND": "SQE"}


def _end_link(s):
    s = s.strip()
    line = s[:-1]
    typ = "arrow_open"
    last = s[-1:]
    if last == "x":
        typ = "arrow_cross"
        if s.startswith("x"):
            typ, line = "double_" + typ, line[1:]
    elif last == ">":
        typ = "arrow_point"
        if s.startswith("<"):
            typ, line = "double_" + typ, line[1:]
    elif last == "o":
        typ = "arrow_circle"
        if s.startswith("o"):
            typ, line = "double_" + typ, line[1:]
    stroke = "normal"
    if line.startswith("="):
        stroke = "thick"
    if line.startswith("~"):
        stroke = "invisible"
    if line.count("."):
        stroke = "dotted"
    return {"type": typ, "stroke": stroke}


def _destruct_link(link, start=None):
    info = _end_link(link)
    if start is None:
        return info
    s = start.strip()
    st = "arrow_open"
    if s[:1] == "<":
        st, s = "arrow_point", s[1:]
    elif s[:1] == "x":
        st, s = "arrow_cross", s[1:]
    elif s[:1] == "o":
        st, s = "arrow_circle", s[1:]
    stroke = "normal"
    if "=" in s:
        stroke = "thick"
    if "." in s:
        stroke = "dotted"
    if stroke != info["stroke"]:
        raise Refuse("unparsed: INVALID link")
    if st == "arrow_open":
        st = info["type"]
    else:
        if st != info["type"]:
            raise Refuse("unparsed: INVALID link")
        st = "double_" + st
    if st == "double_arrow":
        st = "double_arrow_point"
    return {"type": st, "stroke": stroke}


class Parser:
    def __init__(self, toks):
        self.toks, self.i, self.db = toks, 0, DB()
        self.block_stack = []

    # -- helpers
    def peek(self, k=0):
        return self.toks[min(self.i + k, len(self.toks) - 1)]

    def at(self, *types):
        return self.peek().t in types

    def take(self, *types):
        t = self.peek()
        if types and t.t not in types:
            raise Refuse(f"unparsed: expected {'/'.join(types)}, found {t.t}")
        self.i += 1
        return t

    def spaces(self):
        n = 0
        while self.at("SPACE"):
            self.i += 1
            n += 1
        return n

    # -- start: graphConfig document
    def parse(self):
        while self.at("SPACE", "NEWLINE"):
            self.i += 1
        self.take("GRAPH")
        if self.at("NODIR"):
            self.i += 1
        else:
            self.take("DIR")
            if self.at("SEMI", "NEWLINE"):
                self.i += 1
            elif self.at("SPACE"):
                self.spaces()
                self.take("NEWLINE")
            else:
                raise Refuse("unparsed: header")
        items = self.document(top=True)
        self.take("EOF")
        return self.db, items

    def document(self, top=False):
        items = []
        while True:
            t = self.peek().t
            if t == "EOF":
                if not top:
                    raise Refuse("unparsed: subgraph without end")
                return items
            if t == "end":
                if top:
                    raise Refuse("unparsed: end outside a subgraph")
                return items
            if t in ("SEMI", "NEWLINE", "SPACE"):
                self.i += 1
                continue
            r = self.statement()
            if isinstance(r, list):
                items.extend(r)
            elif r is not None:
                items.append(r)

    def separator(self):
        if self.at("NEWLINE", "SEMI"):
            self.i += 1
        elif self.at("EOF"):
            pass
        else:
            raise Refuse(f"unparsed: expected a separator, found {self.peek().t}")

    def statement(self):
        t = self.peek().t
        if t == "STYLE":
            return self.style_statement()
        if t == "LINKSTYLE":
            return self.linkstyle_statement()
        if t == "CLASSDEF":
            return self.classdef_statement()
        if t == "CLASS":
            return self.class_statement()
        if t == "CLICK":
            return self.click_statement()
        if t == "subgraph":
            return self.subgraph_statement()
        if t == "direction":
            self.i += 1
            return {"stmt": "dir"}
        if t in _ID_TOKENS:
            nodes = self.vertex_statement()
            self.separator()
            self.mention(nodes)
            return nodes
        raise Refuse(f"unparsed: statement starting {t}")

    def mention(self, ids):
        if self.block_stack:
            self.block_stack[-1].update(ids)

    # -- vertices
    def id_string(self):
        if not self.at(*_ID_TOKENS):
            raise Refuse(f"unparsed: expected an id, found {self.peek().t}")
        s = []
        while self.at(*_ID_TOKENS):
            s.append(self.take().v)
        return "".join(s)

    def text(self, *ends):
        """text: TEXT/UNICODE_TEXT... | STR then text tokens. Returns
        {"text", "type"} and leaves the end token for the caller."""
        parts, typ = [], None
        if self.at("STR"):
            parts.append(self.take().v)
            typ = "string"
        while self.at("TEXT", "UNICODE_TEXT", "TAGSTART", "TAGEND"):
            parts.append(self.take().v)
            typ = typ or "text"
        if typ is None:
            raise Refuse("unparsed: empty label")
        if typ == "string" and len(parts) > 1:
            raise Refuse("unparsed: string label followed by text")
        return {"text": "".join(parts), "type": typ}

    def vertex(self):
        vid = self.id_string()
        t = self.peek().t
        shape = None
        if t in _SHAPES:
            self.i += 1
            txt = self.text()
            self.take(_SHAPE_END[t])
            shape = _SHAPES[t]
        elif t == "PS":
            self.i += 1
            if self.at("PS"):
                self.i += 1
                txt = self.text()
                self.take("PE")
                self.take("PE")
                shape = "circle"
            else:
                txt = self.text()
                self.take("PE")
                shape = "round"
        elif t == "DIAMOND_START":
            self.i += 1
            if self.at("DIAMOND_START"):
                self.i += 1
                txt = self.text()
                self.take("DIAMOND_STOP")
                self.take("DIAMOND_STOP")
                shape = "hexagon"
            else:
                txt = self.text()
                self.take("DIAMOND_STOP")
                shape = "diamond"
        elif t in ("TRAPSTART", "INVTRAPSTART"):
            self.i += 1
            txt = self.text()
            e = self.take("TRAPEND", "INVTRAPEND").t
            shape = {("TRAPSTART", "TRAPEND"): "trapezoid", ("INVTRAPSTART", "INVTRAPEND"): "inv_trapezoid",
                     ("TRAPSTART", "INVTRAPEND"): "lean_right", ("INVTRAPSTART", "TRAPEND"): "lean_left"}[(t, e)]
        if shape is None:
            self.db.add_vertex(vid)
        else:
            self.db.add_vertex(vid, txt["text"], txt["type"], shape, statement=True)
        return vid

    def styled_vertex(self):
        vid = self.vertex()
        if self.at("STYLE_SEPARATOR"):
            self.i += 1
            cls = self.id_string()
            self.db.set_class(vid, cls)
        return vid

    def shape_data(self, node):
        doc = _shape_doc(self.take("SHAPE_DATA").v)
        self.db.add_vertex(node[-1], doc=doc, statement=True)

    def node(self):
        """node: styledVertex ((shapeData)? spaceList AMP spaceList styledVertex)*.
        A trailing shapeData or spaceList is left to the caller."""
        ids = [self.styled_vertex()]
        while True:
            save = self.i
            sd = self.i if self.at("SHAPE_DATA") else None
            if sd is not None:
                self.i += 1
            if self.at("SPACE"):
                self.spaces()
                if self.at("AMP") and self.peek(1).t == "SPACE":
                    self.i += 1
                    self.spaces()
                    nxt = self.styled_vertex()
                    if sd is not None:
                        # The grammar applies the shape data when it reduces
                        # `node shapeData spaceList AMP spaceList
                        # styledVertex`: after the next vertex.
                        resume, self.i = self.i, sd
                        self.shape_data(ids)
                        self.i = resume
                    ids.append(nxt)
                    continue
            self.i = save
            return ids

    def link(self):
        lid = None
        if self.at("LINK_ID"):
            lid = self.take().v
        if self.at("START_LINK"):
            start = self.take().v
            parts, typ = [], None
            if self.at("STR"):
                parts.append(self.take().v)
                typ = "string"
            while self.at("EDGE_TEXT", "UNICODE_TEXT"):
                parts.append(self.take().v)
                typ = typ or "text"
            if typ is None:
                raise Refuse("unparsed: empty edge text")
            if typ == "string" and len(parts) > 1:
                raise Refuse("unparsed: string edge text followed by text")
            end = self.take("LINK").v
            d = _destruct_link(end, start)
            d["text"] = "".join(parts)
        else:
            d = _destruct_link(self.take("LINK").v)
            if self.at("PIPE"):
                self.i += 1
                d["text"] = self.text()["text"]
                self.take("PIPE")
                if self.at("SPACE"):
                    self.i += 1
        d["id"] = lid
        return d

    def vertex_statement(self):
        node = self.node()
        allnodes = list(node)
        stmt = node
        if self.at("SHAPE_DATA"):
            self.shape_data(node)
        self.spaces()
        while self.at("LINK", "START_LINK", "LINK_ID"):
            link = self.link()
            nxt = self.node()
            if self.at("SHAPE_DATA"):
                self.shape_data(nxt)
            self.db.add_link(stmt, nxt, link)
            allnodes = nxt + allnodes
            stmt = nxt
            self.spaces()
        return allnodes

    # -- other statements
    def styles_opt(self):
        styles, cur = [], []
        while True:
            if self.at(*_STYLE_COMPONENTS):
                cur.append(self.take().v)
            elif self.at("COMMA"):
                if not cur:
                    raise Refuse("unparsed: empty style")
                styles.append("".join(cur))
                cur = []
                self.i += 1
            else:
                break
        if not cur:
            raise Refuse("unparsed: empty style")
        styles.append("".join(cur))
        return styles

    def style_statement(self):
        self.take("STYLE")
        self.take("SPACE")
        vid = self.id_string()
        self.take("SPACE")
        styles = self.styles_opt()
        self.separator()
        self.db.add_vertex(vid, styles=styles)
        return []

    def linkstyle_statement(self):
        self.take("LINKSTYLE")
        self.take("SPACE")
        if self.at("DEFAULT"):
            self.i += 1
            pos = ["default"]
        else:
            pos = [int(self.take("NUM").v)]
            while self.at("COMMA"):
                self.i += 1
                pos.append(int(self.take("NUM").v))
        self.take("SPACE")
        if self.at("INTERPOLATE"):
            raise Refuse("linkStyle interpolate")
        styles = self.styles_opt()
        self.separator()
        self.db.update_link(pos, styles)
        return []

    def classdef_statement(self):
        self.take("CLASSDEF")
        self.take("SPACE")
        ids = self.id_string()
        self.take("SPACE")
        styles = self.styles_opt()
        self.separator()
        self.db.add_class(ids, styles)
        return []

    def class_statement(self):
        self.take("CLASS")
        self.take("SPACE")
        ids = self.id_string()
        self.take("SPACE")
        cls = self.id_string()
        self.separator()
        self.db.set_class(ids, cls)
        return []

    def click_statement(self):
        ids = self.take("CLICK").v
        href = False
        if self.at("HREF"):
            self.i += 1
            href = True
        if self.at("STR"):
            url = self.take().v
            target = None
            if self.at("SPACE") and self.peek(1).t == "STR":
                self.i += 2  # a tooltip: not in Appendix A's model
            if self.at("SPACE") and self.peek(1).t == "LINK_TARGET":
                self.i += 1
                target = self.take("LINK_TARGET").v
            self.separator()
            self.db.set_link(ids, url, target)
            return []
        if href:
            raise Refuse("unparsed: click href without a string")
        # click <id> <callback> ["tooltip"]: under securityLevel strict this
        # only adds the class `clickable`, which Appendix A leaves out.
        if not self.at(*_ALPHANUM):
            raise Refuse("unparsed: click")
        while self.at(*_ALPHANUM):
            self.i += 1
        if self.at("SPACE") and self.peek(1).t == "STR":
            self.i += 2
        self.separator()
        self.db.set_class(ids, "clickable")
        return []

    def subgraph_statement(self):
        self.take("subgraph")
        id_obj = title_obj = None
        if self.at("SPACE"):
            self.i += 1
            if self.at("STR"):
                id_obj = {"text": self.take().v, "type": "text"}
            else:
                parts = []
                while self.at(*_TEXT_NOTAGS):
                    parts.append(self.take().v)
                if not parts:
                    raise Refuse("unparsed: subgraph header")
                id_obj = {"text": "".join(parts), "type": "text"}
            if self.at("SQS"):
                self.i += 1
                title_obj = self.text()
                self.take("SQE")
            else:
                title_obj = id_obj
        self.separator()
        self.block_stack.append(set())
        items = self.document()
        self.take("end")
        mentioned = self.block_stack.pop()
        sid = self.db.add_subgraph(id_obj, items, title_obj, explicit_form=id_obj is not None)
        self.db.block_mentions.append((sid, mentioned))
        self.mention([sid])
        return sid


def parse(text):
    """H's parse of one diagram text: the DB, or Refuse."""
    src = preprocess(text)
    toks = lex(src)
    db, _ = Parser(toks).parse()
    return db
