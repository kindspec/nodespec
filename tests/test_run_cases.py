# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The case-tree runner: that it judges as §9 does, and that it can fail."""

import json

import pytest

import run_cases

H = "flowchart TD\n"


def case(root, name, text, expect, why=True):
    d = root / name
    d.mkdir(parents=True)
    (d / "input.mmd").write_bytes(text.encode() if isinstance(text, str) else text)
    if expect is not None:
        (d / "expect.json").write_text(
            json.dumps(expect) if not isinstance(expect, str) else expect
        )
    if why:
        (d / "WHY.md").write_text("why\n")


def run(root, capsys):
    rc = run_cases.main([str(root)])
    return rc, capsys.readouterr().out


def test_a_root_given_that_does_not_exist_is_no_verdict(tmp_path, capsys):
    rc, out = run(tmp_path / "absent", capsys)
    assert rc == 2
    assert "no case tree" in out and "no verdict" in out


def test_empty_tree_is_no_verdict(tmp_path, capsys):
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "no verdict" in out


def test_passing_cases(tmp_path, capsys):
    case(tmp_path, "g/accept", H + "  a[A]\n", {"accept": True})
    case(
        tmp_path,
        "g/refuse",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id"], "ids": {"undeclared-id": ["a", "b"]}},
    )
    case(tmp_path, "g/no-id", H + "  a[A] --> b\n", {"refusal": ["declaration-in-edge"]})
    case(tmp_path, "g/bytes", b"flowchart TD\r\n  a[A]\r\n", {"accept": True})
    rc, out = run(tmp_path, capsys)
    assert rc == 0, out
    assert "4 case(s): 4 passed, 0 failed, 0 malformed" in out


def test_extra_identifiers_in_the_case_are_allowed(tmp_path, capsys):
    # A case names every identifier that applies; reporting a subset passes.
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id", "malformed-line"], "ids": {"undeclared-id": ["a", "b"]}},
    )
    assert run(tmp_path, capsys)[0] == 0


def test_accept_case_refused_fails(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a --> b\n", {"accept": True})
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "FAIL g/c: expected accept" in out


def test_refusal_case_accepted_fails(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A]\n", {"refusal": ["malformed-line"]})
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "got accept" in out


def test_wrong_identifier_fails(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A] --> b\n", {"refusal": ["malformed-line"]})
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "[declaration-in-edge], which the case does not name" in out


def test_one_finding_outside_the_case_fails(tmp_path, capsys):
    # two findings, one of them named by the case: each report is judged
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n  c[C]\n  c[C]\n",
        {"refusal": ["undeclared-id"], "ids": {"undeclared-id": ["a", "b"]}},
    )
    assert run(tmp_path, capsys)[0] == 1


def test_wrong_id_fails(tmp_path, capsys):
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id"], "ids": {"undeclared-id": ["a"]}},
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "for `b`, not among the case's ids" in out


def spec(tmp_path, monkeypatch, section_12):
    """A SPEC.md holding only a §12, for the runner to read its provisional list from."""
    path = tmp_path / "SPEC.md"
    path.write_text("# spec\n\n## 12. Provisional, settled, and not decided\n\n" + section_12)
    monkeypatch.setattr(run_cases, "SPEC", str(path))


SECTION_12 = """Each reading marked **(provisional)** above is listed here.

- A reading of §3 (§3).
- A reading of §4.4 that runs
  onto a second line (§4.4).

**Settled by the owner, 2026-10-20.** These are final.

- A settled reading (§4.6).

## 13. Next
"""


def test_provisional_is_judged_and_counted(tmp_path, capsys, monkeypatch):
    spec(tmp_path, monkeypatch, SECTION_12)
    root = tmp_path / "cases"
    tag = "A reading of §4.4 that runs onto a second line (§4.4)."
    case(root, "g/p", H + "  a[A]\n", {"accept": True, "provisional": tag})
    case(
        root,
        "g/q",
        H + "  a[A]\n",
        {"refusal": ["leading-bom"], "provisional": "A reading of §3 (§3)."},
    )
    rc, out = run(root, capsys)
    assert rc == 1
    assert "FAIL g/q (provisional)" in out
    assert "2 provisional, 1 of them failed" in out


def test_malformed_cases(tmp_path, capsys):
    case(tmp_path, "g/no-expect", H, None)
    case(tmp_path, "g/bad-json", H, "{")
    case(tmp_path, "g/unknown-id", H, {"refusal": ["no-such-refusal"]})
    case(tmp_path, "g/missing-ids", H, {"refusal": ["undeclared-id"]})
    case(
        tmp_path,
        "g/ids-for-line-entry",
        H,
        {"refusal": ["malformed-line"], "ids": {"malformed-line": ["x"]}},
    )
    case(tmp_path, "g/accept-false", H, {"accept": False})
    case(tmp_path, "g/both", H, {"accept": True, "refusal": ["no-header"]})
    case(tmp_path, "g/unknown-key", H, {"accept": True, "note": "x"})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert out.count("MALFORMED") == 8


def test_missing_input_is_malformed(tmp_path, capsys):
    d = tmp_path / "g" / "c"
    d.mkdir(parents=True)
    (d / "expect.json").write_text('{"accept": true}')
    assert run(tmp_path, capsys)[0] == 2


def test_failure_outranks_malformed(tmp_path, capsys):
    case(tmp_path, "g/bad", H, None)
    case(tmp_path, "g/fail", H + "  a --> b\n", {"accept": True})
    assert run(tmp_path, capsys)[0] == 1


def test_missing_why_is_noted(tmp_path, capsys):
    case(tmp_path, "g/c", H, {"accept": True}, why=False)
    rc, out = run(tmp_path, capsys)
    assert rc == 0
    assert "has no WHY.md" in out


def test_usage(capsys):
    assert run_cases.main(["a", "b"]) == 2


def test_missing_default_tree_is_no_verdict(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(run_cases, "DEFAULT_ROOT", str(tmp_path / "absent"))
    rc = run_cases.main([])
    assert rc == 2
    assert "no verdict" in capsys.readouterr().out


def test_the_committed_tree_meets_its_floor(capsys):
    assert run_cases.main([]) == 0
    assert "fewer than its floor" not in capsys.readouterr().out


def test_a_default_tree_below_its_floor_is_no_verdict(capsys, monkeypatch):
    monkeypatch.setattr(run_cases, "MIN_CASES", 10**6)
    assert run_cases.main([]) == 2
    assert "fewer than its floor" in capsys.readouterr().out


def run_exact(root, capsys):
    rc = run_cases.main(["--exact", str(root)])
    return rc, capsys.readouterr().out


def test_exact_passes_on_the_exact_set(tmp_path, capsys):
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n  c[C]\n  c[C]\n  x y\n",
        {
            "refusal": ["undeclared-id", "duplicate-declaration", "malformed-line"],
            "ids": {"undeclared-id": ["a", "b"], "duplicate-declaration": ["c"]},
        },
    )
    case(tmp_path, "g/ok", H + "  a[A]\n", {"accept": True})
    assert run_exact(tmp_path, capsys)[0] == 0


def test_exact_fails_on_an_identifier_the_checker_does_not_report(tmp_path, capsys):
    # passes under §9's judging, fails under --exact
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id", "malformed-line"], "ids": {"undeclared-id": ["a", "b"]}},
    )
    assert run(tmp_path, capsys)[0] == 0
    rc, out = run_exact(tmp_path, capsys)
    assert rc == 1
    assert "missing [malformed-line]" in out


def test_exact_fails_on_an_id_the_checker_does_not_report(tmp_path, capsys):
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id"], "ids": {"undeclared-id": ["a", "b", "z"]}},
    )
    assert run(tmp_path, capsys)[0] == 0
    rc, out = run_exact(tmp_path, capsys)
    assert rc == 1
    assert "missing [undeclared-id] for `z`" in out


def test_exact_fails_on_an_extra_finding(tmp_path, capsys):
    case(
        tmp_path,
        "g/c",
        H + "  a --> b\n",
        {"refusal": ["undeclared-id"], "ids": {"undeclared-id": ["a"]}},
    )
    rc, out = run_exact(tmp_path, capsys)
    assert rc == 1
    assert "extra [undeclared-id] for `b`" in out


def test_exact_still_fails_an_accepted_refusal(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A]\n", {"refusal": ["malformed-line"]})
    assert run_exact(tmp_path, capsys)[0] == 1


def test_the_committed_tree_matches_exactly(capsys):
    assert run_cases.main(["--exact"]) == 0
    assert " 0 failed" in capsys.readouterr().out


def test_exact_usage(capsys):
    assert run_cases.main(["--exact", "a", "b"]) == 2
    assert run_cases.main(["--strict"]) == 2


@pytest.mark.parametrize("tag", [True, "", "   ", 1, ["§4"], None])
def test_provisional_must_be_a_non_empty_string(tmp_path, tag):
    # Refused even where the readings would admit it, so the guarantee does
    # not rest on what SPEC.md holds.
    path = tmp_path / "expect.json"
    path.write_text(json.dumps({"accept": True, "provisional": tag}))
    with pytest.raises(run_cases.Malformed, match="non-empty string"):
        run_cases.load_expect(str(path), {"", "   "})


def test_a_tag_naming_a_settled_reading_is_malformed(tmp_path, capsys):
    # SPEC.md's own §12 lists this reading as settled, not provisional.
    tag = "Ids are ASCII letters, digits and `_` (§4.4)."
    case(tmp_path, "g/c", H + "  a[A]\n", {"accept": True, "provisional": tag})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED g/c" in out and "§12" in out


@pytest.mark.parametrize(
    "tag",
    [
        "A settled reading (§4.6).",
        "A reading of §4.4 that runs",
        "A reading of §4.4 that runs\n  onto a second line (§4.4).",
        "A reading of §3",
        "§3",
    ],
)
def test_a_tag_not_in_the_provisional_list_is_malformed(tmp_path, capsys, monkeypatch, tag):
    spec(tmp_path, monkeypatch, SECTION_12)
    root = tmp_path / "cases"
    case(root, "g/c", H + "  a[A]\n", {"accept": True, "provisional": tag})
    rc, out = run(root, capsys)
    assert rc == 2
    assert "MALFORMED g/c" in out


def test_an_empty_provisional_list_admits_no_tag(tmp_path, capsys, monkeypatch):
    spec(tmp_path, monkeypatch, "No reading is provisional now.\n\n**Settled.**\n\n- A (§3).\n")
    root = tmp_path / "cases"
    case(root, "g/c", H + "  a[A]\n", {"accept": True, "provisional": "A (§3)."})
    case(root, "g/d", H + "  a[A]\n", {"accept": True})
    rc, out = run(root, capsys)
    assert rc == 2
    assert "MALFORMED g/c" in out and "MALFORMED g/d" not in out


@pytest.mark.parametrize("text", [None, "# spec\n\n## 11. Last\n"])
def test_a_spec_without_section_12_is_no_verdict(tmp_path, capsys, monkeypatch, text):
    path = tmp_path / "SPEC.md"
    if text is not None:
        path.write_text(text)
    monkeypatch.setattr(run_cases, "SPEC", str(path))
    root = tmp_path / "cases"
    case(root, "g/c", H + "  a[A]\n", {"accept": True})
    rc, out = run(root, capsys)
    assert rc == 2
    assert "no verdict" in out


def readings_of(tmp_path, text):
    path = tmp_path / "SPEC.md"
    path.write_text(text)
    return run_cases.provisional_readings(str(path))


TITLE = "## 12. Provisional, settled, and not decided\n\n"


def test_an_empty_bullet_is_no_reading(tmp_path):
    assert readings_of(tmp_path, TITLE + "Intro.\n\n- \n- A (§3).\n\n**Settled.**\n") == {"A (§3)."}


def test_a_bullet_is_stripped(tmp_path):
    text = TITLE + "Intro.\n\n-  A (§3).  \n\n**Settled.**\n"
    assert readings_of(tmp_path, text) == {"A (§3)."}


def test_the_list_ends_at_the_next_heading(tmp_path):
    text = TITLE + "Intro.\n\n- A (§3).\n\n## 13. Next\n\n- B (§13).\n"
    assert readings_of(tmp_path, text) == {"A (§3)."}


def test_the_list_is_found_by_its_title_not_its_number(tmp_path):
    text = (
        "# spec\n\n## 12. Merge\n\n- Some merge rule (§12).\n\n"
        "## 13. Provisional, settled, and not decided\n\nIntro.\n\n- A (§3).\n\n"
        "**Settled.**\n\n- X (§3).\n"
    )
    assert readings_of(tmp_path, text) == {"A (§3)."}


@pytest.mark.parametrize(
    "text",
    [
        "# spec\n\n## 12. Merge\n\n- Some merge rule (§12).\n",
        TITLE + "- A (§3).\n\n" + TITLE + "- B (§4).\n",
    ],
)
def test_no_single_provisional_section_is_no_verdict(tmp_path, capsys, monkeypatch, text):
    path = tmp_path / "SPEC.md"
    path.write_text(text)
    monkeypatch.setattr(run_cases, "SPEC", str(path))
    root = tmp_path / "cases"
    case(root, "g/c", H + "  a[A]\n", {"accept": True, "provisional": "Some merge rule (§12)."})
    rc, out = run(root, capsys)
    assert rc == 2
    assert "no verdict" in out


def test_a_case_one_level_down_is_malformed(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A]\n", {"accept": True})
    case(tmp_path, "flat", H + "  a[A]\n", {"accept": True})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED flat" in out


def test_a_case_three_levels_down_is_malformed(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A]\n", {"accept": True})
    case(tmp_path, "g/c/deeper", H + "  a[A]\n", {"accept": True})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED g/c/deeper" in out


def test_case_files_at_the_root_are_malformed(tmp_path, capsys):
    case(tmp_path, "g/c", H + "  a[A]\n", {"accept": True})
    (tmp_path / "expect.json").write_text('{"accept": true}')
    assert run(tmp_path, capsys)[0] == 2


# Merge cases: three versions of a file merged by stock git, then the result
# checked as one file (SPEC.md §10).

BASE = H + "    a[A]\n    b[B]\n    c[C]\n    a --> c\n"
ADD_EDGE = BASE + "    b --> c\n"
DROP_B = H + "    a[A]\n    c[C]\n    a --> c\n"
DROP_B_ADD_EDGE = DROP_B + "    b --> c\n"


def merge_case(root, name, base, ours, theirs, expect, merged=None, why=True):
    d = root / name
    d.mkdir(parents=True)
    for fname, text in (("base.mmd", base), ("ours.mmd", ours), ("theirs.mmd", theirs)):
        if text is not None:
            (d / fname).write_bytes(text.encode() if isinstance(text, str) else text)
    if merged is not None:
        (d / "merged.mmd").write_bytes(merged.encode() if isinstance(merged, str) else merged)
    if expect is not None:
        (d / "expect.json").write_text(
            json.dumps(expect) if not isinstance(expect, str) else expect
        )
    if why:
        (d / "WHY.md").write_text("why\n")
    return d


def test_a_clean_merge_is_checked_as_one_file(tmp_path, capsys):
    merge_case(
        tmp_path,
        "m/refused",
        BASE,
        DROP_B,
        ADD_EDGE,
        {"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["b"]}},
        merged=DROP_B_ADD_EDGE,
    )
    merge_case(
        tmp_path,
        "m/accepted",
        BASE,
        BASE.replace("[A]", "[Alpha]"),
        ADD_EDGE,
        {"merge": "clean", "accept": True},
        merged=ADD_EDGE.replace("[A]", "[Alpha]"),
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 0, out
    assert "2 case(s): 2 passed" in out


def test_a_clean_merge_judged_wrongly_fails(tmp_path, capsys):
    merge_case(
        tmp_path,
        "m/c",
        BASE,
        DROP_B,
        ADD_EDGE,
        {"merge": "clean", "accept": True},
        merged=DROP_B_ADD_EDGE,
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "FAIL m/c: expected accept, got" in out


def test_merged_text_must_match_byte_for_byte(tmp_path, capsys):
    merge_case(
        tmp_path,
        "m/c",
        BASE,
        DROP_B,
        ADD_EDGE,
        {"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["b"]}},
        merged=DROP_B_ADD_EDGE + "\n",
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert "stock git's merged text is not the case's merged.mmd" in out


def test_a_conflict_passes_when_the_case_expects_one(tmp_path, capsys):
    merge_case(
        tmp_path,
        "m/c",
        BASE,
        BASE.replace("[A]", "[One]"),
        BASE.replace("[A]", "[Two]"),
        {"merge": "conflict"},
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 0, out
    assert "1 case(s): 1 passed" in out


@pytest.mark.parametrize(
    ("ours", "expect", "merged", "said"),
    [
        (
            BASE.replace("[A]", "[One]"),
            {"merge": "clean", "accept": True},
            BASE,
            "clean, it reported conflict",
        ),
        (DROP_B, {"merge": "conflict"}, None, "conflict, it reported clean"),
    ],
)
def test_git_reporting_otherwise_fails(tmp_path, capsys, ours, expect, merged, said):
    theirs = BASE.replace("[A]", "[Two]") if expect["merge"] == "clean" else ADD_EDGE
    merge_case(tmp_path, "m/c", BASE, ours, theirs, expect, merged=merged)
    rc, out = run(tmp_path, capsys)
    assert rc == 1
    assert f"FAIL m/c: expected stock git to report {said}" in out


def test_ours_is_merged_before_theirs(tmp_path, capsys):
    # Git writes the first branch merged as HEAD's side: the order is what
    # makes a conflicted text, and so the case, reproducible.
    seen = {}

    def fake(base, branches, filename):
        seen["branches"] = branches
        return "conflict", ""

    import kindkit.gitmerge

    ours, theirs = BASE.replace("[A]", "[One]"), BASE.replace("[A]", "[Two]")
    merge_case(tmp_path, "m/c", BASE, ours, theirs, {"merge": "conflict"})
    old = kindkit.gitmerge.merge
    kindkit.gitmerge.merge = fake
    try:
        rc, _ = run(tmp_path, capsys)
    finally:
        kindkit.gitmerge.merge = old
    assert rc == 0
    assert seen["branches"] == [ours, theirs]


@pytest.mark.parametrize(
    ("files", "expect", "said"),
    [
        ({"ours": None}, {"merge": "conflict"}, "is a merge case with no ours.mmd"),
        ({"theirs": None}, {"merge": "conflict"}, "is a merge case with no theirs.mmd"),
        ({"base": None}, {"merge": "conflict"}, "is a merge case with no base.mmd"),
        ({}, {"merge": "clean", "accept": True}, "a clean merge needs merged.mmd"),
        ({"merged": BASE}, {"merge": "conflict"}, "a conflicted merge has no merged.mmd"),
        ({}, {"accept": True}, 'must give "merge": "clean" or "conflict"'),
        ({}, {"merge": "maybe"}, 'must give "merge": "clean" or "conflict"'),
        ({}, {"merge": "conflict", "accept": True}, "carries no other verdict"),
        ({"merged": BASE}, {"merge": "clean", "note": 1}, "has unknown keys: note"),
        ({"merged": BASE}, {"merge": "clean"}, "names no refusal"),
        ({"ours": b"\xff\n"}, {"merge": "conflict"}, "ours.mmd is not UTF-8"),
        ({"merged": b"\xff\n"}, {"merge": "clean", "accept": True}, "merged.mmd is not UTF-8"),
        (
            {"base": DROP_B_ADD_EDGE},
            {"merge": "conflict"},
            "base.mmd is refused on its own (undeclared-id)",
        ),
        ({"ours": H + "  a --> b\n"}, {"merge": "conflict"}, "ours.mmd is refused on its own"),
        ({"theirs": DROP_B_ADD_EDGE}, {"merge": "conflict"}, "theirs.mmd is refused on its own"),
    ],
)
def test_malformed_merge_cases(tmp_path, capsys, files, expect, said):
    texts = {"base": BASE, "ours": BASE.replace("[A]", "[One]"), "theirs": ADD_EDGE, "merged": None}
    texts.update(files)
    merge_case(
        tmp_path,
        "m/c",
        texts["base"],
        texts["ours"],
        texts["theirs"],
        expect,
        merged=texts["merged"],
    )
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    line = next(ln for ln in out.splitlines() if ln.startswith("MALFORMED m/c: "))
    assert said in line


def test_a_merge_case_with_an_input_is_malformed(tmp_path, capsys):
    d = merge_case(tmp_path, "m/c", BASE, DROP_B, ADD_EDGE, {"merge": "conflict"})
    (d / "input.mmd").write_text(BASE)
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED m/c: holds both input.mmd and a merge case's files" in out


def test_a_single_file_case_giving_merge_is_malformed(tmp_path, capsys):
    case(tmp_path, "g/c", BASE, {"merge": "clean", "accept": True})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert 'MALFORMED g/c: expect.json gives "merge", but the case has no base.mmd' in out


@pytest.mark.parametrize("fname", ["base.mmd", "ours.mmd", "theirs.mmd", "merged.mmd"])
def test_a_merge_file_one_level_down_is_malformed(tmp_path, capsys, fname):
    d = tmp_path / "g"
    d.mkdir()
    (d / fname).write_text(BASE)
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED g: holds a case's files" in out


def test_git_failing_is_malformed_not_a_crash(tmp_path, capsys):
    # A branch identical to the base has nothing to commit, and git refuses.
    merge_case(tmp_path, "m/c", BASE, BASE, ADD_EDGE, {"merge": "clean", "accept": True}, ADD_EDGE)
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED m/c: stock git could not run the merge" in out


def test_git_missing_is_malformed_not_a_crash(tmp_path, capsys, monkeypatch):
    merge_case(
        tmp_path,
        "m/c",
        BASE,
        BASE.replace("[A]", "[One]"),
        BASE.replace("[A]", "[Two]"),
        {"merge": "conflict"},
    )
    monkeypatch.setenv("PATH", str(tmp_path / "no-bin"))
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED m/c: stock git could not run the merge" in out


def test_an_unreadable_merge_file_is_malformed_not_a_crash(tmp_path, capsys):
    d = merge_case(tmp_path, "m/c", BASE, DROP_B, ADD_EDGE, {"merge": "clean", "accept": True})
    (d / "merged.mmd").mkdir()
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED m/c: merged.mmd cannot be read" in out
