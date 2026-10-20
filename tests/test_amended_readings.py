# SPDX-License-Identifier: Apache-2.0 OR MIT
"""One test per reading SPEC.md settled after draft 0's first text (e7e643e)."""

import pytest

from nodespec import check

H = "flowchart TD\n"
NBSP = "\N{NO-BREAK SPACE}"


def got(text):
    return {(f.identifier, f.id) for f in check(text)}


# --- §3: lone-cr is a byte 0x0D not followed by 0x0A -------------------------


def test_lone_cr_is_a_byte_test():
    assert got(b"flowchart TD\r\r\n") == {("lone-cr", None)}
    assert got(b"flowchart TD\r\n\r") == {("lone-cr", None)}
    assert got("flowchart TD\r  a[A]\n") == {("lone-cr", None)}
    assert got(b"flowchart TD\r\n  a[A]\r\n") == set()


# --- §4.2 rule 1 and §4.9: front matter is exempt from stray-direction ----------


def test_front_matter_lines_are_exempt_from_stray_direction():
    assert got("---\ntitle: go direction LR\n---\n" + H) == {("not-admitted", None)}
    assert got("---\nx: ends in direction\n---\n" + H) == {("not-admitted", None)}


def test_unclosed_front_matter_is_exempt_to_the_end_of_the_file():
    assert got("---\n" + H + "  a[go direction LR]\n") == {
        ("not-admitted", None),
        ("no-header", None),
    }


def test_lines_after_the_closing_fence_are_not_exempt():
    assert got("---\nx: 1\n---\n" + H + "  a[go direction LR]\n") == {
        ("not-admitted", None),
        ("stray-direction", None),
    }


def test_fences_with_trailing_or_indenting_wsp_are_front_matter():
    assert got(" \t---\nx: direction LR\n---  \n" + H) == {("not-admitted", None)}


def test_a_fence_indented_by_nbsp_is_not_a_fence():
    # §4.2 rule 1 reads the fence with WSP around it; U+00A0 is not WSP
    # (§3), so the line is the first statement line.
    assert got(NBSP + "---\nx: 1\n---\n" + H) == {
        ("no-header", None),
        ("malformed-line", None),
    }


# --- §4.9: a directive line is not exempt ------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        '%%{init: {"theme": "direction LR"}}%%',
        "  a[go direction LR %%{x}%%]",
        "  a[A %%{x direction LR}%%]",
        "%%{x direction TB",
    ],
)
def test_directive_lines_holding_the_text_are_refused_twice(line):
    assert got(H + line + "\n") == {("not-admitted", None), ("stray-direction", None)}


# --- §4.9: the words compare exactly -------------------------------------------


@pytest.mark.parametrize(
    "label", ["go direction lr", "go direction Lr", "go Direction LR", "go DIRECTION LR"]
)
def test_direction_words_compare_exactly(label):
    assert got(H + f"  a[{label}]\n") == set()


def test_trailing_direction_compares_exactly():
    assert got(H + "  a[A]\n  subgraph s\n    a\n  end\n  style a fill:Direction\n") == set()


# --- §4.9: both clauses use §4.9's whitespace -------------------------------------


def test_both_clauses_use_mermaids_whitespace():
    assert got(H + f"  a[direction{NBSP}LR]\n") == {("stray-direction", None)}
    assert got(H + f"  a[A]\n  style a fill:direction{NBSP}\n") == {
        ("stray-direction", None),
        ("malformed-line", None),
    }


# --- §4.4: the L_ form's characters include `_` ----------------------------------


def test_L_form_with_underscores_is_reserved():
    assert got(H + "  L_a_b__0[X]\n") == {("reserved-id", "L_a_b__0")}
    assert got(H + "  L_____0[X]\n") == {("reserved-id", "L_____0")}
    assert got(H + "  a[A]\n  b_[B]\n  a L_a_b__0@--> b_\n") == {("reserved-id", "L_a_b__0")}


def test_L_form_needs_three_parts():
    assert got(H + "  L__0[X]\n  L_a__[X]\n  L_ab_0[X]\n") == set()


# --- §4.6: edge-id-on-group only on a top-level edge statement --------------------


def test_edge_id_on_group_not_on_other_classified_lines():
    assert got(H + "  b[B]\n  c[C]\n  a[A] & b e1@--> c\n") == {("declaration-in-edge", None)}
    text = H + "  a[A]\n  b[B]\n  c[C]\n  subgraph s\n    a & b e1@--> c\n  end\n"
    assert got(text) == {("statement-in-block", None)}


# --- §4.7: the whole run of WSP after `subgraph` is skipped ---------------------


@pytest.mark.parametrize("opening", ["subgraph  s", "subgraph\t s", "subgraph \t s [T]"])
def test_subgraph_after_a_run_of_wsp(opening):
    assert got(H + f"  a[A]\n  {opening}\n    a\n  end\n") == set()


def test_without_id_test_skips_the_whole_run():
    # After the run the text is `s-x`: no WSP, so not subgraph-without-id.
    assert got(H + "  subgraph  s-x\n  end\n") == {
        ("malformed-line", None),
        ("unbalanced-block", None),
    }
    assert got(H + "  subgraph \t\n") == {("subgraph-without-id", None)}
    assert got(H + '  subgraph \t "T"\n') == {("subgraph-without-id", None)}


# --- §4.9: every direction statement after the first is direction-twice ------------


def test_third_direction_statement():
    text = H + "  subgraph s\n    direction LR\n    direction TB\n    direction BT\n  end\n"
    assert [f.identifier for f in check(text)] == ["direction-twice", "direction-twice"]


# --- §4.10: :::, @{ and Markdown strings, by the rule that decides the line --------


@pytest.mark.parametrize(
    "line",
    [
        '  subgraph s ["`T`"]',
        "  subgraph s [a@{b]",
        "  classDef c fill:red:::x",
        "  classDef c fill:@{x",
        "  class a:::b c",
        '  class a c"`',
        "  style a fill:red@{x",
        '  style a font-family:"`x`"',
        "  end x:::y",
        "  direction LR:::x",
    ],
)
def test_not_admitted_text_on_earlier_rules_lines_is_malformed(line):
    assert ("malformed-line", None) in got(H + "  a[A]\n" + line + "\n")
    assert ("not-admitted", None) not in got(H + "  a[A]\n" + line + "\n")


@pytest.mark.parametrize(
    "text",
    [
        "  subgraph s [a:::b]\n  end\n",
        '  subgraph s ["a@{b"]\n  end\n',
        "  a[x:::y]\n",
        '  a["x@{y"]\n',
    ],
)
def test_not_admitted_text_inside_a_label_that_matches_is_label_text(text):
    # §4.10: rule 11 is reached only by a line no earlier rule decides. An
    # unquoted label may hold `:` and a quoted one `@` and `{` (§4.1), so these
    # lines match their productions and are accepted.
    assert got(H + text) == set()


def test_not_admitted_text_on_a_linkstyle_line_is_link_style():
    assert got(H + "  a[A]\n  linkStyle 0 stroke:red:::x\n") == {("link-style", None)}


@pytest.mark.parametrize(
    "line",
    [
        '  a["`x`"]',
        "  a:::c",
        "  a@{ shape: rect }",
        '  a[A] -->|"`x`"| b',
        "  a[A] --> b:::c",
        "  a e1@{ curve: x }--> b",
    ],
)
def test_not_admitted_text_reached_by_rule_11(line):
    assert got(H + "  b[B]\n" + line + "\n") == {("not-admitted", None)}


def test_not_admitted_text_reached_by_rule_11_in_a_block():
    assert got(H + "  a[A]\n  subgraph s\n    a:::c\n  end\n") == {("not-admitted", None)}


# --- §9: bad-encoding and lone-cr are both reported; leading-bom is not -----------


def test_whole_file_refusals():
    assert got(b"\xef\xbb\xbfflowchart TD\r\xff") == {("lone-cr", None), ("bad-encoding", None)}
    assert got(b"\xef\xbb\xbfflowchart TD\r") == {("lone-cr", None)}


# --- bc2cf0b: non-WSP fences, and syntax-like label text ---------------------------


def test_spec_example_of_nbsp_indented_fences():
    # §4.2 rule 1's own example: a U+00A0 before each fence.
    text = NBSP + "---\n" + NBSP + "---\nflowchart TD\na --> b\n"
    assert got(text) == {
        ("no-header", None),
        ("malformed-line", None),
        ("undeclared-id", "a"),
        ("undeclared-id", "b"),
    }


@pytest.mark.parametrize(
    "text",
    [
        "  b[B]\n  a[A]\n  a -->|x:::y| b\n",
        '  b[B]\n  a[A]\n  a -->|"x@{y"| b\n',
    ],
)
def test_edge_label_text_that_matches_is_text(text):
    assert got(H + text) == set()


def test_a_line_that_matches_nothing_is_not_admitted_though_its_text_is_label_text():
    assert got(H + "  a[x:::y] q\n") == {("not-admitted", None)}
    assert got(H + '  a["x@{y"] q\n') == {("not-admitted", None)}


def test_a_closing_fence_indented_by_nbsp_does_not_close():
    # The front matter then runs to the end of the file (§4.2 rule 1).
    assert got("---\nx: 1\n" + NBSP + "---\n" + H) == {("not-admitted", None), ("no-header", None)}
