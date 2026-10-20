# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Readings of SPEC.md where the text admits more than one, each pinned.

Each test names the reading it takes. If SPEC.md is clarified the other way,
the test is what changes, with the checker.
"""

from nodespec import check

H = "flowchart TD\n"


def got(text):
    return {(f.identifier, f.id) for f in check(text)}


def test_stray_direction_applies_to_front_matter_and_directive_lines():
    # §4.9 exempts comments and direction statements only, read literally.
    assert got("---\ntitle: direction LR\n---\n" + H) == {
        ("not-admitted", None),
        ("stray-direction", None),
    }
    assert got(H + "%%{init: {'x': 'direction TB'}}%%\n") == {
        ("not-admitted", None),
        ("stray-direction", None),
    }
    assert got(H + "<<<<<<< direction LR\n") == {
        ("conflict-marker", None),
        ("stray-direction", None),
    }


def test_stray_direction_trailing_whitespace_is_mermaids():
    # "with trailing whitespace removed" uses §4.9's whitespace, not WSP.
    assert got(H + "  a[A]\n  style a fill:direction\u00a0\n") == {
        ("stray-direction", None),
        ("malformed-line", None),
    }


def test_a_comment_holding_eq_quote_is_not_exempt_from_stray_direction():
    assert got(H + '%% x="direction LR"\n') == {
        ("malformed-line", None),
        ("stray-direction", None),
    }


def test_markdown_title_on_a_subgraph_line_is_malformed():
    # §4.3 rule 1 sends a top-level subgraph line to §4.7 alone, and §4.10
    # says a line is not-admitted only as §4.2 and §4.3 say.
    assert got(H + '  subgraph s ["`T`"]\n  end\n') == {
        ("malformed-line", None),
        ("unbalanced-block", None),
    }


def test_not_admitted_forms_in_a_style_line_are_malformed():
    assert got(H + "  a[A]\n  style a fill:red:::x\n") == {("malformed-line", None)}


def test_not_admitted_forms_in_a_block_are_not_admitted():
    assert got(H + "  a[A]\n  subgraph s\n    a:::c\n  end\n") == {("not-admitted", None)}


def test_edge_id_on_group_only_on_a_top_level_edge_statement():
    assert got(H + "  b[B]\n  c[C]\n  a[A] & b e1@--> c\n") == {("declaration-in-edge", None)}
    assert got(H + "  a[A]\n  b[B]\n  c[C]\n  subgraph s\n    a & b e1@--> c\n  end\n") == {
        ("statement-in-block", None)
    }


def test_reserved_id_yields_to_stray_direction():
    # "reserved-id applies only to a line that nothing else refuses".
    assert got(H + "  end[go direction LR]\n") == {("stray-direction", None)}


def test_order_rules_read_only_lines_not_refused():
    # class-not-last: the later line was refused, so it is not a statement
    # line for the rule.
    assert got(H + "  a[A]\n  classDef c fill:red\n  class a c\n  linkStyle 0 x\n") == {
        ("link-style", None)
    }
    # styled-twice: the second style line was refused.
    assert got(H + "  a[A]\n  style a fill:red\n  style a fill:red;\n") == {
        ("malformed-line", None)
    }


def test_styled_twice_counts_lines_not_mentions():
    assert got(H + "  a[A]\n  classDef c fill:red\n  class a,a c\n") == set()


def test_member_twice_whatever_the_id_names():
    text = H + "  a[A]\n  b[B]\n  a e1@--> b\n  subgraph s\n    e1\n    e1\n  end\n"
    assert got(text) == {("wrong-kind", "e1"), ("member-twice", "e1")}


def test_every_subgraph_on_a_cycle_is_reported():
    text = (
        H + "  subgraph s\n    t\n  end\n  subgraph t\n    u\n  end\n  subgraph u\n    s\n  end\n"
    )
    assert got(text) == {("membership-cycle", x) for x in "stu"}


def test_a_subgraph_held_by_a_cycle_is_not_on_it():
    text = (
        H + "  subgraph s\n    t\n  end\n  subgraph t\n    s\n  end\n  subgraph u\n    s\n  end\n"
    )
    assert got(text) == {
        ("membership-cycle", "s"),
        ("membership-cycle", "t"),
        ("member-twice", "s"),
    }


def test_third_direction_statement_is_refused_too():
    text = H + "  subgraph s\n    direction LR\n    direction TB\n    direction BT\n  end\n"
    assert [f.identifier for f in check(text)] == ["direction-twice", "direction-twice"]


def test_bom_is_not_reported_when_checking_stops():
    assert got(b"\xef\xbb\xbfflowchart TD\r") == {("lone-cr", None)}
    assert got(b"\xef\xbb\xbfflowchart TD\n\xff") == {("bad-encoding", None)}


def test_class_target_declared_as_class_is_wrong_kind():
    assert got(H + "  classDef c fill:red\n  class c c\n") == {("wrong-kind", "c")}


def test_one_duplicate_edge_finding_per_edge_written_twice_or_more():
    text = H + "  a[A]\n  b[B]\n  a --> b\n  a --> b\n  a --> b\n  b --> a\n  b --> a\n"
    assert [f.identifier for f in check(text)] == ["duplicate-edge", "duplicate-edge"]


def test_findings_about_ids_carry_the_id_and_others_carry_none():
    text = (
        H
        + "  a --> b\n  c[C]\n  c[C]\n  x y z\n  subgraph s\n    s\n  end\n"
        + "  style c fill:red\n  style c fill:red\n  direction LR\n"
    )
    for f in check(text):
        assert (f.id is not None) == (
            f.identifier
            in {
                "undeclared-id",
                "duplicate-declaration",
                "membership-cycle",
                "styled-twice",
            }
        ), f


def test_a_directive_line_is_not_a_comment_for_stray_direction():
    assert got(H + "%%{direction LR}%%\n") == {("not-admitted", None), ("stray-direction", None)}
