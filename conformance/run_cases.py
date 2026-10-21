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

`expect.json` may also carry a "provisional" tag: the text of a bullet in
SPEC.md §12's list of provisional readings, its line breaks folded to spaces,
naming the reading the case rests on. A tag that is not one of those bullets,
such as one naming a reading since settled, makes the case malformed. Such a
case is judged like any other and counted apart.

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
        is malformed or stands at the wrong depth, SPEC.md has no §12, or the
        default tree holds fewer than MIN_CASES cases
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "reference"))

from nodespec import ID_ENTRIES, IDENTIFIERS, check  # noqa: E402

DEFAULT_ROOT = os.path.join(HERE, "cases")
SPEC = os.path.join(HERE, "..", "SPEC.md")
# conformance/cases may grow but never shrink unnoticed: a tree that lost
# cases, or went missing, is no verdict.
MIN_CASES = 322
INPUT, EXPECT, WHY = "input.mmd", "expect.json", "WHY.md"


class Malformed(Exception):
    """The case cannot be judged."""


def provisional_readings(path):
    """The bullets of SPEC.md §12's provisional list, each with its line
    breaks folded to spaces: those after the §12 heading and before the next
    bold paragraph or heading. None when SPEC.md or its §12 is missing."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## 12.")]
    if not starts:
        return None
    readings = []
    for ln in lines[starts[0] + 1 :]:
        if ln.startswith(("**", "#")):
            break
        if ln.startswith("- "):
            readings.append(ln[2:].strip())
        elif ln.startswith("  ") and ln.strip() and readings:
            readings[-1] += " " + ln.strip()
    return set(readings)


def load_expect(path, readings=frozenset()):
    try:
        with open(path, "rb") as fh:
            exp = json.loads(fh.read().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise Malformed(f"{EXPECT} cannot be read: {e}") from e
    if not isinstance(exp, dict):
        raise Malformed(f"{EXPECT} is not an object")
    extra = set(exp) - {"accept", "refusal", "ids", "provisional"}
    if extra:
        raise Malformed(f"{EXPECT} has unknown keys: {', '.join(sorted(extra))}")
    if "provisional" in exp and not isinstance(exp["provisional"], str):
        raise Malformed(f"{EXPECT}'s provisional tag is not a string")
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
        elif {INPUT, EXPECT} & set(files):
            out.append((rel.replace(os.sep, "/"), dirpath, True))
    return sorted(out)


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
        print(f"no §12 in {SPEC} to check provisional tags against: no verdict")
        return 2
    passed, failed, malformed, provisional = [], [], [], []
    for name, cdir, misplaced in cases(root):
        try:
            if misplaced:
                raise Malformed("holds a case's files but is not two levels below ROOT")
            if not os.path.isfile(os.path.join(cdir, INPUT)):
                raise Malformed(f"has no {INPUT}")
            exp = load_expect(os.path.join(cdir, EXPECT), readings)
            with open(os.path.join(cdir, INPUT), "rb") as fh:
                data = fh.read()
        except Malformed as e:
            malformed.append(name)
            print(f"MALFORMED {name}: {e}")
            continue
        if not os.path.isfile(os.path.join(cdir, WHY)):
            print(f"note: {name} has no {WHY}")
        if "provisional" in exp:
            provisional.append(name)
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
