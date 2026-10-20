#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Runs a conformance case tree against the reference checker.

    python conformance/run_cases.py [ROOT]

ROOT defaults to conformance/cases, laid out as

    <group>/<case>/input.mmd    the file, as exact bytes
    <group>/<case>/expect.json  {"accept": true}
                                or {"refusal": [identifier, ...],
                                    "ids": {identifier: [id, ...]}}
    <group>/<case>/WHY.md       what the case is for

`expect.json` may also carry a "provisional" tag: the case rests on a reading
SPEC.md marks provisional. Such a case is judged like any other and counted
apart.

A case is judged as SPEC.md §9 judges a refusal: a report passes if its
identifier, and its id where the entry has one, are among those the case
names. The checker reports every refusal it finds, and each is a report, so
each is judged: an accepting case passes on no finding, and a refusing case on
at least one finding, every one of which is among the case's.

Exit codes, so that "every case passed" and "no case ran" never look alike:

    0   every case passed, or there is no tree at a ROOT given (it says so)
    1   at least one case failed
    2   no verdict: the tree holds no case, a case is malformed, or the
        default tree is missing or holds fewer than MIN_CASES cases
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "reference"))

from nodespec import ID_ENTRIES, IDENTIFIERS, check  # noqa: E402

DEFAULT_ROOT = os.path.join(HERE, "cases")
# conformance/cases may grow but never shrink unnoticed: a tree that lost
# cases, or went missing, is no verdict.
MIN_CASES = 270
INPUT, EXPECT, WHY = "input.mmd", "expect.json", "WHY.md"


class Malformed(Exception):
    """The case cannot be judged."""


def load_expect(path):
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


def judge(findings, exp):
    """The reasons a case fails; empty when it passes."""
    if "accept" in exp:
        return [f"expected accept, got {f.message} [{f.identifier}]" for f in findings]
    if not findings:
        return ["expected a refusal, got accept"]
    allowed, ids = set(exp["refusal"]), exp.get("ids", {})
    out = []
    for f in findings:
        if f.identifier not in allowed:
            out.append(f"reported [{f.identifier}], which the case does not name: {f.message}")
        elif f.identifier in ID_ENTRIES and f.id not in ids[f.identifier]:
            out.append(f"reported [{f.identifier}] for `{f.id}`, not among the case's ids")
    return out


def cases(root):
    for group in sorted(os.listdir(root)):
        gdir = os.path.join(root, group)
        if not os.path.isdir(gdir):
            continue
        for case in sorted(os.listdir(gdir)):
            cdir = os.path.join(gdir, case)
            if os.path.isdir(cdir):
                yield f"{group}/{case}", cdir


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) > 1 or (args and args[0].startswith("-")):
        print("usage: run_cases.py [ROOT]", file=sys.stderr)
        return 2
    root = args[0] if args else DEFAULT_ROOT
    if not os.path.isdir(root):
        if not args:
            print(f"no case tree at {root}: no verdict")
            return 2
        print(f"no case tree at {root}: nothing to run")
        return 0
    passed, failed, malformed, provisional = [], [], [], []
    for name, cdir in cases(root):
        try:
            if not os.path.isfile(os.path.join(cdir, INPUT)):
                raise Malformed(f"has no {INPUT}")
            exp = load_expect(os.path.join(cdir, EXPECT))
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
        reasons = judge(check(data), exp)
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
