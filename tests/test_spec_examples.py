# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The examples SPEC.md gives, section by section, each with what it says of them.

Each expectation is the exact set of (identifier, id) the checker reports, so a
test here fails on a refusal reported that does not apply as well as on one
missed.
"""

import pytest

from nodespec import check

H = "flowchart TD\n"
OK = set()


def got(text):
    return {(f.identifier, f.id) for f in check(text)}


def one(identifier, id=None):
    return {(identifier, id)}


# (name, text, expected)
CASES = [
    # --- §3 ------------------------------------------------------------------
    ("utf8-ok", H + "  a[Ünïcode ✓]\n", OK),
    ("bad-encoding", b"flowchart TD\n  a[\xff]\n", one("bad-encoding")),
    ("bad-encoding-overlong", b"flowchart TD\n  a[\xc0\xaf]\n", one("bad-encoding")),
    ("bad-encoding-surrogate", b"flowchart TD\n  a[\xed\xa0\x80]\n", one("bad-encoding")),
    ("bad-encoding-stops", b"flowchart TD\n  a --> b\n  a[\xff]\n", one("bad-encoding")),
    ("bad-encoding-str-surrogate", "flowchart TD\n  a[\ud800]\n", one("bad-encoding")),
    ("leading-bom", "\ufeffflowchart TD\n  a[A]\n", one("leading-bom")),
    ("leading-bom-bytes", b"\xef\xbb\xbfflowchart TD\n", one("leading-bom")),
    (
        "leading-bom-then-more",
        "\ufeffflowchart TD\n  a --> b\n",
        one("leading-bom") | {("undeclared-id", "a"), ("undeclared-id", "b")},
    ),
    ("bom-not-leading-is-label-text", H + "  a[x\ufeffy]\n", OK),
    ("lone-cr", "flowchart TD\r  a[A]\r", one("lone-cr")),
    ("lone-cr-stops", "flowchart TD\n  a --> b\r\n  c\rd\n", one("lone-cr")),
    (
        "lone-cr-and-bad-encoding",
        b"flowchart TD\r\xff",
        {("lone-cr", None), ("bad-encoding", None)},
    ),
    ("crlf", "flowchart TD\r\n  a[A]\r\n  b[B]\r\n  a --> b\r\n", OK),
    ("no-final-newline", "flowchart TD\n  a[A]", OK),
    ("case-sensitive-ids", H + "  End[E]\n  end_[E]\n  End --> end_\n", OK),
    ("nbsp-is-not-wsp", H + "\u00a0a[A]\n", one("malformed-line")),
    # --- §4.1 ----------------------------------------------------------------
    ("comment-holding-eq-quote-after-header", H + '%% x="y"\n', one("malformed-line")),
    (
        "comment-holding-eq-quote-before-header",
        '%% x="y"\n' + H,
        one("no-header") | one("malformed-line"),
    ),
    ("unquoted-tilde", H + "  a[x ~~~ y]\n", one("malformed-line")),
    ("quoted-tilde", H + '  a["~~~"]\n', OK),
    ("quoted-all-wsp", H + '  a[" \t "]\n', one("malformed-line")),
    ("quoted-ends-eq", H + '  a["x="]\n', one("malformed-line")),
    ("quoted-markdown", H + '  a["`x`"]\n', one("not-admitted")),
    ("style-unit-v", H + "  a[A]\n  style a width:5v\n", one("malformed-line")),
    ("style-unit-vh", H + "  a[A]\n  style a height:100vh\n", OK),
    ("style-name-v", H + "  a[A]\n  style a fill:v\n", one("malformed-line")),
    ("style-name-v-hyphen", H + "  a[A]\n  style a fill:v-x\n", one("malformed-line")),
    ("style-name-keyword", H + "  a[A]\n  style a fill:end\n", one("malformed-line")),
    ("style-name-keyword-hyphen", H + "  a[A]\n  style a fill:class-x\n", one("malformed-line")),
    (
        "style-name-flowchart-elk",
        H + "  a[A]\n  style a fill:flowchart-elk\n",
        one("malformed-line"),
    ),
    ("style-swimlane-beta", H + "  a[A]\n  style a fill:swimlane-beta\n", one("malformed-line")),
    (
        "style-swimlane-beta-x",
        H + "  a[A]\n  style a fill:swimlane-beta-x\n",
        one("malformed-line"),
    ),
    ("style-swimlane", H + "  a[A]\n  style a fill:swimlane,stroke:swimlane-x\n", OK),
    ("style-prop-acctitle", H + "  a[A]\n  style a accTitle:red\n", one("malformed-line")),
    ("style-prop-accdescr", H + "  a[A]\n  style a accDescr:red\n", one("malformed-line")),
    ("style-L-form-word", H + "  a[A]\n  style a fill:L_x_y_0\n", OK),
    (
        "style-reserved-words-that-parse",
        H + "  a[A]\n  style a fill:hasOwnProperty,stroke:direction-x\n",
        OK,
    ),
    # --- §4.2 ----------------------------------------------------------------
    ("front-matter", "---\ntitle: x\n---\n" + H, one("not-admitted")),
    ("front-matter-indented", "  ---\t\ntitle: x\n --- \n" + H, one("not-admitted")),
    ("front-matter-unclosed", "---\n" + H + "  a[A]\n", one("not-admitted") | one("no-header")),
    ("front-matter-only-first-line", H + "---\n", one("malformed-line")),
    (
        "conflict-markers",
        H + "<<<<<<< ours\n  a[A]\n=======\n  b[B]\n>>>>>>> theirs\n",
        one("conflict-marker"),
    ),
    ("conflict-marker-pipes", H + "||||||| base\n", one("conflict-marker")),
    ("six-is-not-a-marker", H + "<<<<<< x\n", one("malformed-line")),
    ("directive", "%%{init: {}}%%\n" + H, one("not-admitted")),
    ("directive-in-comment", H + "  a[A]\n  b[B]\n%% see %%{x\n  a --> b\n", one("not-admitted")),
    ("directive-in-label", H + "  a[x %%{ y]\n", one("not-admitted")),
    ("blank-lines", "\n  \n\t\n" + H + "\n  a[A]\n\n", OK),
    ("comments", "%% top\n" + H + "  %% indented\n  a[A]\n%%x\n", OK),
    ("bare-percent-is-not-a-comment", H + "%%\n", one("malformed-line")),
    ("u2028", H + "  a[x\u2028%% y]\n", one("malformed-line")),
    ("u2029", H + "  a[x\u2029y]\n", one("malformed-line")),
    ("comment-with-u2028", H + "%% x\u2028y\n", one("malformed-line")),
    # --- §4.3 ----------------------------------------------------------------
    ("header-graph", "graph\n", OK),
    ("header-dirs", "".join(f"flowchart {d}\n" for d in ["TB"]) + "%% x\n", OK),
    ("header-graph-LR", "  graph   LR  \n", OK),
    ("no-statement-line", "%% only\n\n", one("no-header")),
    ("empty-file", "", one("no-header")),
    ("header-case", "Flowchart TD\n", one("no-header")),
    ("header-td", "flowchart td\n", one("no-header")),
    ("header-lt", "flowchart <\n", one("no-header")),
    ("header-v", "flowchart v\n", one("no-header")),
    ("header-elk", "flowchart-elk TD\n", one("no-header")),
    ("header-semicolon", "flowchart TD;\n", one("no-header")),
    ("header-space-semicolon", "graph TD ;\n", one("no-header")),
    (
        "no-header-then-lines-as-usual",
        "a[A]\n  b[B]\n  b --> c\n",
        one("no-header") | one("undeclared-id", "c"),
    ),
    ("semicolon-edge", H + "  a[A]\n  b[B]\n  a --> b;\n", one("malformed-line")),
    ("semicolon-two-statements", H + "  a[A]; b[B]\n", one("malformed-line")),
    ("semicolon-member", H + "  a[A]\n  subgraph s\n    a;\n  end\n", one("malformed-line")),
    ("semicolon-in-label", H + "  a[x; y]\n", OK),
    ("semicolon-style", H + "  a[A]\n  style a fill:red;stroke:blue\n", one("malformed-line")),
    ("semicolon-classdef", H + "  classDef c fill:#f9f;stroke:#333\n", one("malformed-line")),
    ("bare-id-top-level", H + "  a[A]\n  a\n", one("malformed-line")),
    ("second-header", H + "flowchart TD\n", one("malformed-line")),
    ("click", H + "  a[A]\n  click a call cb()\n", one("not-admitted")),
    ("click-in-block", H + "  a[A]\n  subgraph s\n    click a x\n  end\n", one("not-admitted")),
    ("acctitle", H + "  accTitle: t\n", one("not-admitted")),
    ("acctitle-wsp", H + "  accTitle  : t\n", one("not-admitted")),
    ("accdescr-colon", H + "accDescr: d\n", one("not-admitted")),
    ("accdescr-brace", H + "  accDescr {\n", one("not-admitted")),
    ("acctitle-brace-is-malformed", H + "  accTitle {\n", one("malformed-line")),
    ("triple-colon", H + "  a[A]\n  b[B]\n  a:::c --> b\n", one("not-admitted")),
    ("at-brace", H + "  a@{ shape: rect }\n", one("not-admitted")),
    ("link-style", H + "  a[A]\n  b[B]\n  a --> b\n  linkStyle 0 stroke:red\n", one("link-style")),
    (
        "link-style-in-block",
        H + "  a[A]\n  subgraph s\n    linkStyle 0 x\n  end\n",
        one("link-style"),
    ),
    # --- §4.4 ----------------------------------------------------------------
    ("end-hyphen", H + "  end-x[E]\n", one("malformed-line")),
    ("class-hyphen", H + "  class-a[E]\n", one("malformed-line")),
    ("ampersand-without-spaces", H + "  c[C]\n  a&b --> c\n", one("malformed-line")),
    ("bare-graph-top-level", H + "  graph\n", one("malformed-line")),
    ("node-is-an-id", H + "  node[N]\n  subgraph s\n    node\n  end\n", OK),
    ("classdef-node", H + "  classDef node fill:red\n", one("reserved-id", "node")),
    ("class-node", H + "  a[A]\n  class a node\n", one("reserved-id", "node")),
    ("class-target-node", H + "  node[N]\n  classDef c fill:red\n  class node c\n", OK),
    ("classdef-default", H + "  classDef default fill:red\n", one("reserved-id", "default")),
    ("hasownproperty", H + "  hasOwnProperty[x]\n", one("reserved-id", "hasOwnProperty")),
    ("direction-id", H + "  direction[x]\n", one("reserved-id", "direction")),
    ("L-form", H + "  L_a_b_0[x]\n", one("reserved-id", "L_a_b_0")),
    ("L-form-edge-id", H + "  a[A]\n  b[B]\n  a L_a_b_0@--> b\n", one("reserved-id", "L_a_b_0")),
    ("L-form-needs-digits", H + "  L_a_b_x[x]\n  L_a_b[x]\n  L_a_0[x]\n  L_a_b_[x]\n", OK),
    ("constructor-is-fine", H + "  constructor[x]\n  toString[y]\n  __proto__[z]\n", OK),
    ("reserved-in-edge", H + "  a[A]\n  a --> click\n", one("reserved-id", "click")),
    ("reserved-member", H + "  subgraph s\n    graph\n  end\n", one("reserved-id", "graph")),
    (
        "reserved-subgraph-opens-no-block",
        H + "  a[A]\n  subgraph style\n    a\n  end\n",
        one("reserved-id", "style") | one("malformed-line") | one("unbalanced-block"),
    ),
    ("reserved-style-target", H + "  style _self fill:red\n", one("reserved-id", "_self")),
    (
        "reserved-class-targets",
        H + "  classDef c fill:red\n  class _top,_blank c\n",
        {("reserved-id", "_top"), ("reserved-id", "_blank")},
    ),
    (
        "reserved-not-also-on-refused-line",
        H + "  subgraph s\n    end[x]\n  end\n",
        one("declaration-in-block"),
    ),
    # --- §4.5 ----------------------------------------------------------------
    ("space-before-shape", H + "  a [A]\n", one("malformed-line")),
    (
        "fourteen-shapes",
        H
        + "".join(
            f"  n{i}{s}\n"
            for i, s in enumerate(
                [
                    "[A]",
                    "(A)",
                    "([A])",
                    "[[A]]",
                    "[(A)]",
                    "((A))",
                    ">A]",
                    "{A}",
                    "{{A}}",
                    "[/A/]",
                    "[\\A\\]",
                    "[/A\\]",
                    "[\\A/]",
                    "(((A)))",
                ]
            )
        ),
        OK,
    ),
    ("label-lead-hyphen", H + "  a[-x]\n", one("malformed-line")),
    ("label-lead-slash", H + "  a[ /x]\n", one("malformed-line")),
    ("label-inner-slash", H + "  a[x/y\\z-]\n", OK),
    ("label-whitespace-only", H + "  a[  ]\n", one("malformed-line")),
    ("label-empty", H + "  a[]\n", one("malformed-line")),
    ("tilde-at-start", H + "  a[~~~]\n", one("malformed-line")),
    ("tilde-in-trapezoid", H + "  a[/x/~~~ y/]\n", one("malformed-line")),
    ("tilde-edge-label", H + "  a[A]\n  b[B]\n  a -->|~~~ x| b\n", one("malformed-line")),
    ("at-unquoted", H + "  n[a@b]\n", one("malformed-line")),
    ("at-quoted", H + '  n["a@b"]\n', OK),
    ("html-ish-label", H + "  a[x<b]\n", OK),
    ("quote-with-space-around", H + '  a[ "x" ]\n', one("malformed-line")),
    # --- §4.6 ----------------------------------------------------------------
    ("edge-id-and-label", H + "  a[A]\n  b[B]\n  a e1@--> b\n  a -->|yes| b\n", OK),
    ("no-spaces-around-link", H + "  a[A]\n  b[B]\n  a-->b\n", one("malformed-line")),
    ("circle-no-spaces", H + "  A[A]\n  B[B]\n  A---oB\n", one("malformed-line")),
    (
        "all-links",
        H
        + "  a[A]\n  b[B]\n"
        + "".join(
            f"  a {k} b\n"
            for k in [
                "-->",
                "--->",
                "---",
                "----",
                "--o",
                "--x",
                "---o",
                "<-->",
                "o--o",
                "x--x",
                "<--->",
                "-.->",
                "-..->",
                "-.-",
                "-..-",
                "==>",
                "===>",
                "===",
                "====",
                "~~~",
                "~~~~",
            ]
        ),
        OK,
    ),
    ("link-dotted-both", H + "  a[A]\n  b[B]\n  a <-.-> b\n", one("malformed-line")),
    ("link-thick-both", H + "  a[A]\n  b[B]\n  a <==> b\n", one("malformed-line")),
    ("link-dotted-circles", H + "  a[A]\n  b[B]\n  a o-.-o b\n", one("malformed-line")),
    ("link-thick-crosses", H + "  a[A]\n  b[B]\n  a x==x b\n", one("malformed-line")),
    ("link-head-at-start-o", H + "  a[A]\n  b[B]\n  a o--> b\n", one("malformed-line")),
    ("link-head-at-start-x", H + "  a[A]\n  b[B]\n  a x--> b\n", one("malformed-line")),
    ("link-head-at-start-lt", H + "  a[A]\n  b[B]\n  a <--- b\n", one("malformed-line")),
    ("inline-label-solid", H + "  a[A]\n  b[B]\n  a -- yes --> b\n", one("malformed-line")),
    ("inline-label-dotted", H + "  a[A]\n  b[B]\n  a -. yes .-> b\n", one("malformed-line")),
    ("inline-label-thick", H + "  a[A]\n  b[B]\n  a == yes ==> b\n", one("malformed-line")),
    ("groups-make-four", H + "  a[A]\n  b[B]\n  c[C]\n  d[D]\n  a & b --> c & d\n", OK),
    ("chain", H + "  a[A]\n  b[B]\n  c[C]\n  a --> b --> c\n", OK),
    ("a-and-a", H + "  a[A]\n  b[B]\n  a & a --> b\n", one("duplicate-edge")),
    ("duplicate-edge", H + "  a[A]\n  b[B]\n  a --> b\n  a --> b\n", one("duplicate-edge")),
    (
        "duplicate-edge-labels-trimmed",
        H + "  a[A]\n  b[B]\n  a -->|x| b\n  a -->| x\t| b\n",
        one("duplicate-edge"),
    ),
    ("not-duplicate-quoted-label", H + '  a[A]\n  b[B]\n  a -->|x| b\n  a -->|"x"| b\n', OK),
    ("not-duplicate-link-length", H + "  a[A]\n  b[B]\n  a --> b\n  a ---> b\n", OK),
    ("not-duplicate-label-vs-none", H + "  a[A]\n  b[B]\n  a --> b\n  a -->|x| b\n", OK),
    ("not-duplicate-direction", H + "  a[A]\n  b[B]\n  a --> b\n  b --> a\n", OK),
    ("not-duplicate-named", H + "  a[A]\n  b[B]\n  a e1@--> b\n  a e2@--> b\n  a --> b\n", OK),
    (
        "edge-id-on-group-before",
        H + "  a[A]\n  b[B]\n  c[C]\n  a & b e1@--> c\n",
        one("edge-id-on-group", "e1"),
    ),
    (
        "edge-id-on-group-after",
        H + "  a[A]\n  b[B]\n  c[C]\n  a e1@--> b & c\n",
        one("edge-id-on-group", "e1"),
    ),
    (
        "edge-id-on-group-declares-nothing",
        H + "  a[A]\n  b[B]\n  c[C]\n  a & b e1@--> c\n  classDef k fill:red\n  class e1 k\n",
        one("edge-id-on-group", "e1") | one("undeclared-id", "e1"),
    ),
    (
        "edge-id-chain-not-grouped",
        H + "  a[A]\n  b[B]\n  c[C]\n  d[D]\n  a e1@--> b & c --> d\n",
        one("edge-id-on-group", "e1"),
    ),
    ("edge-id-chain-ok", H + "  a[A]\n  b[B]\n  c[C]\n  d[D]\n  a e1@--> b --> c & d\n", OK),
    # --- §4.7 ----------------------------------------------------------------
    (
        "subgraph-forms",
        H + "  subgraph cache\n  end\n  subgraph c2 [Cache tier]\n  end\n"
        '  subgraph c3["Cache tier"]\n  end\n',
        OK,
    ),
    (
        "subgraph-title-trailing-space",
        H + "  subgraph s [T] \n  end\n",
        one("malformed-line") | one("unbalanced-block"),
    ),
    (
        "subgraph-id-trailing-space",
        H + "  subgraph s \n  end\n",
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-alone",
        H + "  subgraph\n  end\n",
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-title-words",
        H + "  subgraph My Title\n  end\n",
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-quoted",
        H + '  subgraph "My Title"\n  end\n',
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-two-words-title",
        H + "  subgraph a1 b1 [T]\n  end\n",
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-hyphen-id",
        H + "  subgraph s-x\n  end\n",
        one("malformed-line") | one("unbalanced-block"),
    ),
    (
        "end-x",
        H + "  x[X]\n  subgraph s\n  end x\n",
        one("malformed-line") | one("unbalanced-block"),
    ),
    # --- §4.8 ----------------------------------------------------------------
    (
        "class-and-style",
        H + "  a[A]\n  b[B]\n  classDef c fill:#f9f,stroke:#333\n"
        "  style a fill:#f9f\n  class a,b c\n",
        OK,
    ),
    ("classdef-two-classes", H + "  classDef c1,c2 fill:red\n", one("malformed-line")),
    (
        "class-two-classes",
        H + "  a[A]\n  classDef c1 fill:red\n  class a c1,c2\n",
        one("malformed-line"),
    ),
    ("style-two-targets", H + "  a[A]\n  b[B]\n  style a,b fill:red\n", one("malformed-line")),
    (
        "class-trailing-wsp",
        H + "  a[A]\n  classDef c fill:red\n  class a c \n",
        one("malformed-line"),
    ),
    (
        "classdef-style-trailing-wsp",
        H + "  a[A]\n  classDef c fill:red \t\n  style a fill:red \n",
        OK,
    ),
    ("classdef-no-style", H + "  classDef c\n", one("malformed-line")),
    (
        "style-words",
        H + "  a[A]\n  style a stroke-width:4px,opacity:.5,width:50%,height:100vh,"
        "font-family:Arial sans-serif,color:red !important,margin:-1.5em\n",
        OK,
    ),
    ("style-space-after-colon", H + "  a[A]\n  style a fill:  red\n", OK),
    ("style-tab-after-colon", H + "  a[A]\n  style a fill:\tred\n", one("malformed-line")),
    (
        "style-space-after-comma",
        H + "  a[A]\n  style a fill:red, stroke:blue\n",
        one("malformed-line"),
    ),
    (
        "style-space-before-comma",
        H + "  a[A]\n  style a fill:red ,stroke:blue\n",
        one("malformed-line"),
    ),
    ("style-double-hyphen", H + "  a[A]\n  style a fill:a--b\n", one("malformed-line")),
    ("style-amp-in-word", H + "  a[A]\n  style a fill:a&b\n", one("malformed-line")),
    ("style-star-word", H + "  a[A]\n  style a fill:*x\n", one("malformed-line")),
    ("style-gt", H + "  a[A]\n  style a fill:a>b\n", one("malformed-line")),
    ("style-quote", H + '  a[A]\n  style a font-family:"x"\n', one("malformed-line")),
    ("style-empty-hex", H + "  a[A]\n  style a fill:#\n", one("malformed-line")),
    ("style-uppercase-unit", H + "  a[A]\n  style a width:5PX\n", one("malformed-line")),
    ("style-triple-colon", H + "  a[A]\n  style a fill:::x\n", one("not-admitted")),
    # --- §4.9 ----------------------------------------------------------------
    ("direction-in-block", H + "  a[A]\n  subgraph s\n    direction LR\n    a\n  end\n", OK),
    ("direction-outside-block", H + "  direction LR\n", one("direction-outside-block")),
    (
        "direction-twice",
        H + "  subgraph s\n    direction LR\n    direction TB\n  end\n",
        one("direction-twice"),
    ),
    (
        "direction-once-per-block",
        H + "  subgraph s\n    direction LR\n  end\n  subgraph t\n    direction TB\n  end\n",
        OK,
    ),
    ("direction-malformed", H + "  subgraph s\n    direction lr\n  end\n", one("malformed-line")),
    ("stray-in-label", H + "  a[go direction LR]\n", one("stray-direction")),
    (
        "stray-in-edge-label",
        H + "  a[A]\n  b[B]\n  a -->|direction RL| b\n",
        one("stray-direction"),
    ),
    (
        "stray-member-then-LR",
        H + "  subgraph s\n    xdirection\n    LR\n  end\n",
        one("stray-direction") | one("undeclared-id", "LR"),
    ),
    ("stray-inside-id", H + "  xdirection LRX\n", one("stray-direction") | one("malformed-line")),
    ("stray-nbsp", H + "  a[direction\u00a0LR]\n", one("stray-direction")),
    ("stray-u3000", H + "  a[direction\u3000TB]\n", one("stray-direction")),
    # `direction` is a style word (§4.8); the line is refused for the stray alone.
    (
        "stray-trailing-ws",
        H + "  a[A]\n  subgraph s\n    a\n  end\n  style a fill:direction \n",
        one("stray-direction"),
    ),
    (
        "stray-in-title",
        H + "  subgraph s [the direction TD]\n  end\n",
        one("stray-direction") | one("unbalanced-block"),
    ),
    ("stray-comment-exempt", H + "%% direction LR\n%% ends in direction\n", OK),
    (
        "stray-direction-stmt-semicolon",
        H + "  subgraph s\n    direction LR;\n  end\n",
        one("stray-direction") | one("malformed-line"),
    ),
    ("direction-not-stray", H + "  a[direct LR]\n  b[directions]\n", OK),
    # --- §5 ------------------------------------------------------------------
    ("declaration-in-edge", H + "  db[DB]\n  api[API] --> db\n", one("declaration-in-edge")),
    ("declaration-in-edge-declares-nothing", H + "  a[A] --> b\n", one("declaration-in-edge")),
    ("duplicate-node", H + "  a[A]\n  a[A]\n", one("duplicate-declaration", "a")),
    (
        "duplicate-subgraph",
        H + "  subgraph s\n  end\n  subgraph s\n  end\n",
        one("duplicate-declaration", "s"),
    ),
    (
        "duplicate-edge-id",
        H + "  a[A]\n  b[B]\n  a e1@--> b\n  b e1@--> a\n",
        one("duplicate-declaration", "e1"),
    ),
    (
        "duplicate-classdef",
        H + "  classDef c fill:red\n  classDef c fill:red\n",
        one("duplicate-declaration", "c"),
    ),
    (
        "spec-5-4-example",
        H + "  a[a]\n  b[b]\n  d[d]\n  e[e]\n  a --> b\n  d --> e\n  e --> c\n",
        one("undeclared-id", "c"),
    ),
    (
        "spec-5-4-base",
        H + "  a[a]\n  b[b]\n  c[c]\n  d[d]\n  e[e]\n  a --> b\n  b --> c\n  c --> d\n  d --> e\n",
        OK,
    ),
    ("undeclared-style", H + "  style a fill:red\n", one("undeclared-id", "a")),
    ("undeclared-class", H + "  a[A]\n  class a c\n", one("undeclared-id", "c")),
    (
        "undeclared-class-target",
        H + "  classDef c fill:red\n  class a c\n",
        one("undeclared-id", "a"),
    ),
    ("undeclared-member", H + "  subgraph s\n    a\n  end\n", one("undeclared-id", "a")),
    (
        "wrong-kind-style-edge",
        H + "  a[A]\n  b[B]\n  a e1@--> b\n  style e1 fill:red\n",
        one("wrong-kind", "e1"),
    ),
    ("wrong-kind-class-node", H + "  a[A]\n  b[B]\n  class a b\n", one("wrong-kind", "b")),
    (
        "wrong-kind-edge-to-edge",
        H + "  a[A]\n  b[B]\n  a e1@--> b\n  a --> e1\n",
        one("wrong-kind", "e1"),
    ),
    (
        "wrong-kind-edge-to-class",
        H + "  a[A]\n  classDef c fill:red\n  a --> c\n",
        one("wrong-kind", "c"),
    ),
    (
        "wrong-kind-member-edge",
        H + "  a[A]\n  b[B]\n  a e1@--> b\n  subgraph s\n    e1\n  end\n",
        one("wrong-kind", "e1"),
    ),
    (
        "wrong-kind-style-class",
        H + "  classDef c fill:red\n  style c fill:red\n",
        one("wrong-kind", "c"),
    ),
    (
        "class-on-edge",
        H + "  a[A]\n  b[B]\n  a e1@--> b\n  classDef c fill:red\n  class e1 c\n",
        OK,
    ),
    ("class-on-subgraph", H + "  subgraph s\n  end\n  classDef c fill:red\n  class s c\n", OK),
    ("edge-to-subgraph", H + "  a[A]\n  subgraph s\n  end\n  a --> s\n  style s fill:red\n", OK),
    (
        "kind-clash-node-subgraph",
        H + "  cache[C]\n  subgraph cache\n  end\n",
        one("kind-clash", "cache"),
    ),
    (
        "kind-clash-node-edge",
        H + "  a[A]\n  b[B]\n  e1[E]\n  a e1@--> b\n",
        one("kind-clash", "e1"),
    ),
    (
        "kind-clash-class-node",
        H + "  c[C]\n  classDef c fill:red\n  a[A]\n  a --> c\n",
        one("kind-clash", "c"),
    ),
    (
        "kind-clash-and-duplicate",
        H + "  c[C]\n  c[C]\n  classDef c fill:red\n",
        {("kind-clash", "c"), ("duplicate-declaration", "c")},
    ),
    # --- §6 ------------------------------------------------------------------
    (
        "membership",
        H + "  a[A]\n  b[B]\n  subgraph s\n    a\n    t\n  end\n  subgraph t\n    b\n  end\n",
        OK,
    ),
    ("comments-and-blanks-in-block", H + "  a[A]\n  subgraph s\n\n    %% x\n    a\n  end\n", OK),
    ("declaration-in-block", H + "  subgraph s\n    a[A]\n  end\n", one("declaration-in-block")),
    (
        "declaration-in-block-declares-nothing",
        H + "  subgraph s\n    a[A]\n  end\n  b[B]\n  b --> a\n",
        one("declaration-in-block") | one("undeclared-id", "a"),
    ),
    (
        "edge-in-block",
        H + "  a[A]\n  b[B]\n  subgraph s\n    a --> b\n  end\n",
        one("statement-in-block"),
    ),
    (
        "edge-decl-in-block",
        H + "  b[B]\n  subgraph s\n    a[A] --> b\n  end\n",
        one("statement-in-block"),
    ),
    (
        "classdef-in-block",
        H + "  subgraph s\n    classDef c fill:red\n  end\n",
        one("statement-in-block"),
    ),
    ("class-in-block", H + "  subgraph s\n    class a c\n  end\n", one("statement-in-block")),
    ("style-in-block", H + "  subgraph s\n    style a\n  end\n", one("statement-in-block")),
    (
        "nested-block",
        H + "  subgraph s\n    subgraph t\n    end\n  end\n",
        one("nested-block") | one("unbalanced-block"),
    ),
    ("nested-block-malformed", H + "  subgraph s\n    subgraph\n  end\n", one("nested-block")),
    ("end-without-block", H + "  end\n", one("unbalanced-block")),
    ("block-never-closed", H + "  a[A]\n  subgraph s\n    a\n", one("unbalanced-block")),
    (
        "group-in-block",
        H + "  a[A]\n  b[B]\n  subgraph s\n    a & b\n  end\n",
        one("malformed-line"),
    ),
    (
        "member-twice-two-blocks",
        H + "  a[A]\n  subgraph s\n    a\n  end\n  subgraph t\n    a\n  end\n",
        one("member-twice", "a"),
    ),
    (
        "member-twice-one-block",
        H + "  a[A]\n  subgraph s\n    a\n    a\n  end\n",
        one("member-twice", "a"),
    ),
    (
        "cycle-of-two",
        H + "  subgraph s\n    t\n  end\n  subgraph t\n    s\n  end\n",
        {("membership-cycle", "s"), ("membership-cycle", "t")},
    ),
    ("cycle-of-one", H + "  subgraph s\n    s\n  end\n", one("membership-cycle", "s")),
    (
        "refused-subgraph-opens-no-block",
        H + "  a[A]\n  subgraph My Title\n    a\n  end\n",
        one("subgraph-without-id") | one("malformed-line") | one("unbalanced-block"),
    ),
    # --- §7 ------------------------------------------------------------------
    ("class-last", H + "  a[A]\n  classDef c fill:red\n  class a c\n\n%% done\n", OK),
    (
        "class-not-last",
        H + "  a[A]\n  classDef c fill:red\n  class a c\n  b[B]\n",
        one("class-not-last"),
    ),
    (
        "class-before-classdef",
        H + "  a[A]\n  class a c\n  classDef c fill:red\n",
        one("class-not-last"),
    ),
    (
        "class-then-refused-line",
        H + "  a[A]\n  classDef c fill:red\n  class a c\n  nope nope\n",
        one("malformed-line"),
    ),
    (
        "style-twice",
        H + "  a[A]\n  style a fill:red\n  style a stroke:blue\n",
        one("styled-twice", "a"),
    ),
    (
        "class-twice",
        H + "  a[A]\n  classDef c fill:red\n  classDef d fill:red\n  class a c\n  class a d\n",
        one("styled-twice", "a"),
    ),
    (
        "style-and-class-once-each",
        H + "  a[A]\n  classDef c fill:red\n  style a fill:red\n  class a c\n",
        OK,
    ),
    # --- boundaries of the productions above ----------------------------------
    ("tabs-as-wsp", H + "\ta[A]\n\tsubgraph\ts\t[T]\n\t\ta\n\tend\t\n", OK),
    (
        "leading-blank-no-final-newline",
        "\n" + H + "  a --> b",
        {("undeclared-id", "a"), ("undeclared-id", "b")},
    ),
    ("comment-holding-del", H + "%% x\x7f\n", one("malformed-line")),
    ("comment-holding-c1-control", H + "%% x\x85\n", one("malformed-line")),
    ("quoted-hash", H + '  a["#1"]\n', OK),
    ("quoted-ends-backtick", H + '  a["x`"]\n', OK),
    ("comment-holding-eq", H + "%% a = b\n", OK),
    ("unquoted-double-tilde", H + "  a[x~~y]\n", OK),
    ("link-short-arrow-both", H + "  a[A]\n  b[B]\n  a <-> b\n", one("malformed-line")),
    ("link-two-tildes", H + "  a[A]\n  b[B]\n  a ~~ b\n", one("malformed-line")),
    ("link-two-equals", H + "  a[A]\n  b[B]\n  a == b\n", one("malformed-line")),
    ("link-two-dashes", H + "  a[A]\n  b[B]\n  a -- b\n", one("malformed-line")),
    (
        "ampersand-no-space-before",
        H + "  a[A]\n  b[B]\n  c[C]\n  a& b --> c\n",
        one("malformed-line"),
    ),
    ("not-duplicate-end", H + "  a[A]\n  b[B]\n  c[C]\n  a --> b\n  a --> c\n", OK),
    (
        "subgraph-quoted-one-word",
        H + '  subgraph "x"\n  end\n',
        one("subgraph-without-id") | one("unbalanced-block"),
    ),
    (
        "subgraph-title-then-text",
        H + "  subgraph s [T] x\n  end\n",
        one("malformed-line") | one("unbalanced-block"),
    ),
    (
        "style-tab-between-words",
        H + "  a[A]\n  style a font-family:Arial\tsans\n",
        one("malformed-line"),
    ),
    # --- §9's own examples ---------------------------------------------------
    ("refused-line-names-nothing", H + "  a[A] --> b\n", one("declaration-in-edge")),
]


@pytest.mark.parametrize("name,text,expected", CASES, ids=[c[0] for c in CASES])
def test_example(name, text, expected):
    assert got(text) == expected


def test_case_names_unique():
    names = [c[0] for c in CASES]
    assert len(names) == len(set(names))


def test_five_hundred_edges():
    nodes = "".join(f"  n{i}[N]\n" for i in range(501))
    edges = "".join(f"  n{i} --> n{i + 1}\n" for i in range(500))
    assert got(H + nodes + edges) == OK
    assert got(H + nodes + edges + "  n0 --> n500\n") == one("too-many-edges")


def test_too_many_edges_counts_groups_and_named_edges():
    nodes = "".join(f"  n{i}[N]\n" for i in range(20))
    # 20 x 25 = 500 edges from groups, then one named edge
    left = " & ".join(f"n{i}" for i in range(20))
    edges = "".join(f"  {left} {'-' * (2 + k)}> n{k % 20}\n" for k in range(25))
    assert got(H + nodes + edges) == OK
    assert got(H + nodes + edges + "  n0 e1@--> n1\n") == one("too-many-edges")


def test_deterministic():
    text = H + "  a --> b\n  c[C]\n  c[C]\n  subgraph s\n    s\n  end\n  style z fill:red\n"
    assert check(text) == check(text) == check(text.encode())
