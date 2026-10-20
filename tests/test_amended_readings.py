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


# --- §9: bad-encoding and lone-cr are both reported; leading-bom is not -----------


def test_whole_file_refusals():
    assert got(b"\xef\xbb\xbfflowchart TD\r\xff") == {("lone-cr", None), ("bad-encoding", None)}
    assert got(b"\xef\xbb\xbfflowchart TD\r") == {("lone-cr", None)}


# --- bc2cf0b: non-WSP fences ---------------------------


def test_spec_example_of_nbsp_indented_fences():
    # §4.2 rule 1's own example: a U+00A0 before each fence.
    text = NBSP + "---\n" + NBSP + "---\nflowchart TD\na --> b\n"
    assert got(text) == {
        ("no-header", None),
        ("malformed-line", None),
        ("undeclared-id", "a"),
        ("undeclared-id", "b"),
    }


def test_a_closing_fence_indented_by_nbsp_does_not_close():
    # The front matter then runs to the end of the file (§4.2 rule 1).
    assert got("---\nx: 1\n" + NBSP + "---\n" + H) == {("not-admitted", None), ("no-header", None)}


@pytest.mark.parametrize("line", ["%% x %%{ direction LR", "%% x %%{y}%% direction"])
def test_a_directive_line_shaped_like_a_comment_is_not_exempt(line):
    # §4.2 rule 3 (directive) comes before rule 5 (comment), so the line is a
    # directive line, and §4.9 exempts only comment lines.
    assert got(H + line + "\n  a[A]\n") == {("not-admitted", None), ("stray-direction", None)}


def test_a_comment_holding_the_text_is_still_exempt():
    assert got(H + "%% x direction LR\n%% ends in direction\n  a[A]\n") == set()


# --- the owner's ruling (2026-10-20): `:::` and `@{` in any line ------------------
# §4.2 rule 3 refuses a line holding `%%{`, `:::` or `@{` as not-admitted before
# any production is tried; §4.3 rule 11 now covers Markdown strings only.


@pytest.mark.parametrize(
    "line",
    [
        # SPEC.md §4.10's own list
        "  a[x:::y]",
        '  a["x@{y"]',
        "  a[A]\n  b[B]\n  a -->|x:::y| b",
        "  subgraph s [a:::b]\n  end",
        '  subgraph s ["a@{b"]\n  end',
        "  a[A]\n  style a fill:#f00 :::x",
        "  linkStyle 0 :::x",
        "%% use ::: here",
        # and every other kind of line
        "  a:::c",
        "  a[A]\n  b[B]\n  a:::c --> b",
        "  a@{ shape: rect }",
        "  a[A]\n  b[B]\n  a e1@{ curve: x }--> b",
        "  classDef c fill:red:::x",
        "  classDef c fill:@{x",
        "  a[A]\n  classDef c fill:red\n  class a:::b c",
        "  a[A]\n  style a fill:red@{x",
        "  subgraph s\n  end x:::y",
        "  subgraph s\n    direction LR:::x\n  end",
        "  accTitle: a:::b",
        "  click a:::b",
        "%%@{",
        "  a[x:::y] q",
    ],
)
def test_syntax_like_text_is_not_admitted_in_any_line(line):
    assert ("not-admitted", None) in got(H + line + "\n")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("  a[x:::y]\n", {("not-admitted", None)}),
        ('  a["x@{y"]\n', {("not-admitted", None)}),
        ("%% use ::: here\n", {("not-admitted", None)}),
        # rule 3 decides before §4.3, so no first word changes it
        ("  a[A]\n  style a fill:#f00 :::x\n", {("not-admitted", None)}),
        ("  linkStyle 0 :::x\n", {("not-admitted", None)}),
        ("  classDef c fill:red:::x\n", {("not-admitted", None)}),
        ("  end x:::y\n", {("not-admitted", None)}),
    ],
)
def test_rule_3_is_the_only_refusal_of_its_line(text, expected):
    assert got(H + text) == expected


def test_a_refused_line_declares_nothing():
    # the node statement is refused, so the edge names an undeclared id
    assert got(H + "  a[x:::y]\n  b[B]\n  b --> a\n") == {
        ("not-admitted", None),
        ("undeclared-id", "a"),
    }


def test_a_subgraph_line_holding_it_opens_no_block():
    assert got(H + "  a[A]\n  subgraph s [a:::b]\n    a\n  end\n") == {
        ("not-admitted", None),
        ("malformed-line", None),
        ("unbalanced-block", None),
    }


def test_rule_3_does_not_move_the_header():
    # A rule 3 line is not a statement line, so the header comes after it.
    assert got("%% a:::b\n" + H + "  a[A]\n") == {("not-admitted", None)}


def test_a_comment_holding_it_is_not_exempt_from_stray_direction():
    assert got(H + "%% x::: direction LR\n") == {
        ("not-admitted", None),
        ("stray-direction", None),
    }


def test_a_conflict_marker_holding_it_is_a_conflict_marker():
    assert got(H + "<<<<<<< a:::b\n") == {("conflict-marker", None)}


def test_front_matter_holding_it_is_front_matter():
    assert got("---\nx: a:::b @{c\n---\n" + H) == {("not-admitted", None)}


@pytest.mark.parametrize("text", ["  a[x::y]\n", '  a["x@y"]\n', '  a["x{y"]\n', "  a[x:: :y]\n"])
def test_near_misses_are_label_text(text):
    assert got(H + text) == set()


@pytest.mark.parametrize(
    "line",
    ['  a["`x`"]', '  b[B]\n  a[A] -->|"`x`"| b', '  a["`x`"] --> b'],
)
def test_markdown_strings_are_rule_11(line):
    assert got(H + line + "\n") == {("not-admitted", None)}


@pytest.mark.parametrize(
    "line, expected",
    [
        ('  subgraph s ["`T`"]\n  end', {("malformed-line", None), ("unbalanced-block", None)}),
        ('  a[A]\n  style a font-family:"`x`"', {("malformed-line", None)}),
        ('  linkStyle 0 x"`y', {("link-style", None)}),
    ],
)
def test_markdown_strings_get_the_refusal_of_an_earlier_rule(line, expected):
    assert got(H + line + "\n") == expected
