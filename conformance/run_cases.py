#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Runs a conformance case tree against the reference checker.

    python conformance/run_cases.py [--exact] [ROOT]

ROOT defaults to conformance/cases, laid out as

    <group>/<case>/input.mmd    the file, as exact bytes
    <group>/<case>/expect.json  {"accept": true}
                                or {"refusal": [identifier, ...],
                                    "ids": {identifier: [id, ...]}}
    <group>/<case>/WHY.md       what the case is for

A merge case holds, in place of input.mmd, three versions of one file:

    <group>/<case>/base.mmd     the common ancestor
    <group>/<case>/ours.mmd     one branch
    <group>/<case>/theirs.mmd   the other branch
    <group>/<case>/merged.mmd   the file stock git produces, for a clean merge

and its expect.json also carries {"merge": "clean"} or {"merge": "conflict"}.
The runner commits base.mmd, then ours.mmd and theirs.mmd on two branches,
merges them in that order with unconfigured git (kindkit.gitmerge), and
checks that git reports what the case says. A clean merge's text must equal
merged.mmd byte for byte, and is then judged as an input.mmd would be:
SPEC.md §10, stock git's result is checked, not its exit status. A conflict
carries no other verdict. The three versions and merged.mmd are UTF-8,
and each version must be accepted on its own, so that a refusal of the
merged file is one the merge produced.

`expect.json` may also carry a "provisional" tag: the text of a bullet in
the list of provisional readings in SPEC.md's "Provisional" section (§12),
its line breaks folded to spaces, naming the reading the case rests on. A
tagged case is judged like any other and counted apart. A tag that is not a
non-empty string, or not one of those bullets, such as one naming a reading
since settled, makes the case malformed.

A case is judged as SPEC.md §9 judges a refusal: a report passes if its
identifier, and its id where the entry has one, are among those the case
names. The checker reports every refusal it finds, and each is a report, so
each is judged: an accepting case passes on no finding, and a refusing case on
at least one finding, every one of which is among the case's.

`--exact` judges more strictly, for the reference checker and not for §9
conformance: a refusing case passes only if the checker reports exactly the
identifiers the case names and, for each entry about an id, exactly its ids.
§9 lets a conforming checker report any one refusal that applies, so another
checker failing `--exact` is not thereby non-conforming; the reference checker
reports every refusal it finds, and `--exact` holds it to all of them.

Exit codes, so that "every case passed" and "no case ran" never look alike:

    0   every case passed
    1   at least one case failed
    2   no verdict: there is no tree at ROOT, the tree holds no case, a case
        is malformed or stands at the wrong depth, SPEC.md has not exactly
        one Provisional section, or the default tree holds fewer than
        MIN_CASES cases
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "reference"))

from nodespec import ID_ENTRIES, IDENTIFIERS, check  # noqa: E402

DEFAULT_ROOT = os.path.join(HERE, "cases")
SPEC = os.path.join(HERE, "..", "SPEC.md")
# conformance/cases may grow but never shrink unnoticed: a tree that lost
# cases, or went missing, is no verdict.
MIN_CASES = 393
INPUT, EXPECT, WHY = "input.mmd", "expect.json", "WHY.md"
BASE, OURS, THEIRS, MERGED = "base.mmd", "ours.mmd", "theirs.mmd", "merged.mmd"
MERGE_INPUTS = (BASE, OURS, THEIRS)
CLEAN, CONFLICT = "clean", "conflict"


class Malformed(Exception):
    """The case cannot be judged."""


def provisional_readings(path):
    """The non-empty bullets of SPEC.md's provisional list, each with its line
    breaks folded to spaces: those after the one `## <n>. Provisional…`
    heading and before the next bold paragraph or heading. The heading is
    found by its title, not its number, so renumbering cannot point it at
    another section. None when SPEC.md is missing, or holds no such heading
    or more than one."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    starts = [i for i, ln in enumerate(lines) if re.match(r"## [0-9]+\. Provisional\b", ln)]
    if len(starts) != 1:
        return None
    readings = []
    for ln in lines[starts[0] + 1 :]:
        if ln.startswith(("**", "#")):
            break
        if ln.startswith("- "):
            readings.append(ln[2:].strip())
        elif ln.startswith("  ") and ln.strip() and readings:
            readings[-1] += " " + ln.strip()
    return {r for r in readings if r}


def load_expect(path, readings=frozenset(), merge=False):
    """A case's expect.json, checked. For a merge case it must carry
    "merge"; a single-file case must not."""
    try:
        with open(path, "rb") as fh:
            exp = json.loads(fh.read().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise Malformed(f"{EXPECT} cannot be read: {e}") from e
    if not isinstance(exp, dict):
        raise Malformed(f"{EXPECT} is not an object")
    if merge:
        if exp.get("merge") not in (CLEAN, CONFLICT):
            raise Malformed(f'{EXPECT} of a merge case must give "merge": "clean" or "conflict"')
        if exp["merge"] == CONFLICT:
            if set(exp) != {"merge"}:
                raise Malformed(f"{EXPECT} of a conflicted merge carries no other verdict")
            return exp
    elif "merge" in exp:
        raise Malformed(f'{EXPECT} gives "merge", but the case has no {BASE}')
    extra = set(exp) - {"accept", "refusal", "ids", "provisional"} - ({"merge"} if merge else set())
    if extra:
        raise Malformed(f"{EXPECT} has unknown keys: {', '.join(sorted(extra))}")
    if "provisional" in exp and not (
        isinstance(exp["provisional"], str) and exp["provisional"].strip()
    ):
        raise Malformed(f"{EXPECT}'s provisional tag is not a non-empty string")
    if "provisional" in exp and exp["provisional"] not in readings:
        raise Malformed(
            f"{EXPECT}'s provisional tag is not a reading SPEC.md §12 lists as provisional"
        )
    if "accept" in exp:
        if exp["accept"] is not True or "refusal" in exp or "ids" in exp:
            raise Malformed(f'{EXPECT} must be {{"accept": true}} or a refusal')
        return exp
    refusal = exp.get("refusal")
    if not isinstance(refusal, list) or not refusal:
        raise Malformed(f"{EXPECT} names no refusal")
    unknown = [r for r in refusal if r not in IDENTIFIERS]
    if unknown:
        raise Malformed(
            f"{EXPECT} names identifiers §9 does not have: {', '.join(map(str, unknown))}"
        )
    ids = exp.get("ids", {})
    if not isinstance(ids, dict):
        raise Malformed(f"{EXPECT}'s ids is not an object")
    for k, v in ids.items():
        if k not in refusal:
            raise Malformed(f"{EXPECT} gives ids for `{k}`, which it does not name")
        if k not in ID_ENTRIES:
            raise Malformed(f"{EXPECT} gives ids for `{k}`, which §9 reports without one")
        if not isinstance(v, list) or not v or not all(isinstance(x, str) for x in v):
            raise Malformed(f"{EXPECT}'s ids for `{k}` is not a list of ids")
    missing = [r for r in refusal if r in ID_ENTRIES and r not in ids]
    if missing:
        raise Malformed(
            f"{EXPECT} gives no ids for {', '.join(missing)}, which §9 reports with one"
        )
    return exp


def expected_set(exp):
    """Every (identifier, id) a refusing case names; id is None for an entry
    that carries none."""
    ids = exp.get("ids", {})
    return {(r, i) for r in exp["refusal"] for i in (ids[r] if r in ID_ENTRIES else [None])}


def judge(findings, exp, exact=False):
    """The reasons a case fails; empty when it passes."""
    if "accept" in exp:
        return [f"expected accept, got {f.message} [{f.identifier}]" for f in findings]
    if not findings:
        return ["expected a refusal, got accept"]
    if exact:
        want, have = expected_set(exp), {(f.identifier, f.id) for f in findings}
        out = [
            f"missing [{r}]" + (f" for `{i}`" if i else "") for r, i in sorted(want - have, key=str)
        ]
        out += [
            f"extra [{r}]" + (f" for `{i}`" if i else "") for r, i in sorted(have - want, key=str)
        ]
        return out
    allowed, ids = set(exp["refusal"]), exp.get("ids", {})
    out = []
    for f in findings:
        if f.identifier not in allowed:
            out.append(f"reported [{f.identifier}], which the case does not name: {f.message}")
        elif f.identifier in ID_ENTRIES and f.id not in ids[f.identifier]:
            out.append(f"reported [{f.identifier}] for `{f.id}`, not among the case's ids")
    return out


def cases(root):
    """(name, directory, misplaced): every directory two levels below ROOT is
    a case; any other directory holding a case's files is misplaced."""
    out = []
    for dirpath, dirnames, files in os.walk(root):
        dirnames.sort()
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth == 2:
            out.append((rel.replace(os.sep, "/"), dirpath, False))
        elif {INPUT, EXPECT, *MERGE_INPUTS, MERGED} & set(files):
            out.append((rel.replace(os.sep, "/"), dirpath, True))
    return sorted(out)


def read_text(path, name):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError as e:
        raise Malformed(f"{name} is not UTF-8: {e}") from e
    except OSError as e:
        raise Malformed(f"{name} cannot be read: {e}") from e


def git_merge(base, ours, theirs):
    """(outcome, text): stock git merging ours, then theirs, onto base."""
    from kindkit.gitmerge import merge

    return merge(base, [ours, theirs], "flowchart.mmd")


def load_case(cdir, readings):
    """(expect, bytes to check or None): None for a conflicted merge that
    behaved as its case says. Raises Malformed for a case that cannot be
    judged, and returns the reasons it fails as a list in place of bytes when
    git did not do what the case says."""
    present = set(os.listdir(cdir))
    merge = bool(present & {*MERGE_INPUTS, MERGED})
    if merge and INPUT in present:
        raise Malformed(f"holds both {INPUT} and a merge case's files")
    if not merge:
        if INPUT not in present:
            raise Malformed(f"has no {INPUT}")
        exp = load_expect(os.path.join(cdir, EXPECT), readings)
        with open(os.path.join(cdir, INPUT), "rb") as fh:
            return exp, fh.read()
    missing = [n for n in MERGE_INPUTS if n not in present]
    if missing:
        raise Malformed(f"is a merge case with no {', '.join(missing)}")
    exp = load_expect(os.path.join(cdir, EXPECT), readings, merge=True)
    clean = exp["merge"] == CLEAN
    if clean != (MERGED in present):
        raise Malformed(
            f"a clean merge needs {MERGED}" if clean else f"a conflicted merge has no {MERGED}"
        )
    base, ours, theirs = (read_text(os.path.join(cdir, n), n) for n in MERGE_INPUTS)
    for name, text in zip(MERGE_INPUTS, (base, ours, theirs), strict=True):
        found = check(text.encode("utf-8"))
        if found:
            raise Malformed(
                f"{name} is refused on its own ({found[0].identifier}), "
                "so a refusal of the merge would not be the merge's"
            )
    merged = read_text(os.path.join(cdir, MERGED), MERGED) if clean else None
    try:
        outcome, text = git_merge(base, ours, theirs)
    except (RuntimeError, OSError) as e:
        raise Malformed(f"stock git could not run the merge: {e}") from e
    if outcome != exp["merge"]:
        return exp, [f"expected stock git to report {exp['merge']}, it reported {outcome}"]
    if not clean:
        return exp, None
    if text != merged:
        return exp, [f"stock git's merged text is not the case's {MERGED}"]
    return exp, text.encode("utf-8")


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    exact = "--exact" in args
    args = [a for a in args if a != "--exact"]
    if len(args) > 1 or (args and args[0].startswith("-")):
        print("usage: run_cases.py [--exact] [ROOT]", file=sys.stderr)
        return 2
    root = args[0] if args else DEFAULT_ROOT
    if not os.path.isdir(root):
        print(f"no case tree at {root}: no verdict")
        return 2
    readings = provisional_readings(SPEC)
    if readings is None:
        print(f"not exactly one Provisional section in {SPEC} to check tags against: no verdict")
        return 2
    passed, failed, malformed, provisional = [], [], [], []
    for name, cdir, misplaced in cases(root):
        try:
            if misplaced:
                raise Malformed("holds a case's files but is not two levels below ROOT")
            exp, data = load_case(cdir, readings)
        except Malformed as e:
            malformed.append(name)
            print(f"MALFORMED {name}: {e}")
            continue
        if not os.path.isfile(os.path.join(cdir, WHY)):
            print(f"note: {name} has no {WHY}")
        if "provisional" in exp:
            provisional.append(name)
        if isinstance(data, list):
            reasons = data
        elif data is None:
            reasons = []
        else:
            reasons = judge(check(data), exp, exact)
        if reasons:
            failed.append(name)
            tag = " (provisional)" if "provisional" in exp else ""
            for r in reasons:
                print(f"FAIL {name}{tag}: {r}")
        else:
            passed.append(name)
    total = len(passed) + len(failed) + len(malformed)
    prov_failed = sum(1 for n in failed if n in provisional)
    print(
        f"{total} case(s): {len(passed)} passed, {len(failed)} failed, {len(malformed)} malformed; "
        f"{len(provisional)} provisional, {prov_failed} of them failed"
    )
    if total == 0:
        print(f"the tree at {root} holds no case: no verdict")
        return 2
    if failed:
        return 1
    if not args and total < MIN_CASES:
        print(f"{total} case(s) in {root}, fewer than its floor of {MIN_CASES}: no verdict")
        return 2
    return 2 if malformed else 0


if __name__ == "__main__":
    sys.exit(main())
