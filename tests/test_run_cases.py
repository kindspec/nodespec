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


def test_provisional_is_judged_and_counted(tmp_path, capsys):
    case(tmp_path, "g/p", H + "  a[A]\n", {"accept": True, "provisional": "§4.4"})
    case(tmp_path, "g/q", H + "  a[A]\n", {"refusal": ["leading-bom"], "provisional": "§3"})
    rc, out = run(tmp_path, capsys)
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
def test_provisional_must_be_a_non_empty_string(tmp_path, capsys, tag):
    case(tmp_path, "g/c", H + "  a[A]\n", {"accept": True, "provisional": tag})
    rc, out = run(tmp_path, capsys)
    assert rc == 2
    assert "MALFORMED g/c" in out


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
