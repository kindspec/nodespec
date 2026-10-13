#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""The verdict under the owner's ruling of 2026-10-13 (LOG §15).

The frozen aggregator cannot run on the bound results: aggregate.verdict sorts
the cases by "key", and 9,822 cases in arms.json have a null key, so the sort
raises TypeError (aggregate.py:167). The owner ruled that the bound
`aggregate` is never run. Instead, this script:

- imports the frozen harness unchanged;
- builds the summary with mermaid_spike.bound_summary(results/), the function
  cmd_aggregate uses, and refuses if any real-arm case with a tier-A record
  lacks a reproduction, as cmd_aggregate does;
- drops the cases whose key is null, and nothing else;
- calls the frozen aggregate.verdict on the result;
- writes results/verdict-by-ruling.json and its transcript.

It checks, and prints, that the summary it passes differs from bound_summary's
only by the dropped cases, and that no dropped case is exposed, decided,
recorded, or was run through X.

    python3 -I -S -B ruling/verdict_by_ruling.py
"""
import collections
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SPIKE, "harness"))
sys.dont_write_bytecode = True

import mermaid_spike as CLI  # noqa: E402
from ms import aggregate as AG  # noqa: E402

RESULTS = os.path.join(SPIKE, "results")


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, default=str)


def filtered_summary():
    """(full summary, filtered summary, dropped cases). Raises SystemExit as
    cmd_aggregate would if a reproduction is missing."""
    summary, missing = CLI.bound_summary(RESULTS)
    if missing:
        raise SystemExit("refusing: run `repro` first for every real-arm case with a tier-A record; missing: "
                         + ", ".join(missing))
    dropped = [c for c in summary["cases"] if c.get("key") is None]
    kept = [c for c in summary["cases"] if c.get("key") is not None]
    filt = dict(summary, cases=kept)
    return summary, filt, dropped


def check(summary, filt, dropped, out):
    ref, _ = CLI.bound_summary(RESULTS)
    assert canon({k: v for k, v in ref.items() if k != "cases"}) == canon(
        {k: v for k, v in filt.items() if k != "cases"}), "a non-case field differs"
    assert [canon(c) for c in ref["cases"] if c.get("key") is not None] == [canon(c) for c in filt["cases"]], \
        "the kept cases differ from bound_summary's"
    assert len(ref["cases"]) == len(filt["cases"]) + len(dropped)
    print("summary: every field but `cases` equals bound_summary's; the kept cases equal its non-null-key "
          "cases, in order", file=out)
    why = collections.Counter()
    for c in dropped:
        # A non-commuting P case is built at arms.py's arm_p without evaluate(),
        # so it has no "exposed" key; its "excluded" text may be redacted.
        nc = c["arm"] == "P" and "exposed" not in c
        why[(c["arm"], "non-commuting" if nc else "early exit through prepare()")] += 1
    print(f"dropped: {len(dropped)} null-key cases of {len(ref['cases'])}", file=out)
    for k, n in sorted(why.items()):
        print(f"  {k[0]}, {k[1]}: {n}", file=out)
    flags = {"exposed": sum(1 for c in dropped if c.get("exposed")),
             "decided": sum(1 for c in dropped if c.get("decided")),
             "with records": sum(1 for c in dropped if c.get("records")),
             "run through X": sum(1 for c in dropped if "x_agree" in c or c.get("x_records"))}
    print("dropped cases that are " + ", ".join(f"{k}: {v}" for k, v in flags.items()), file=out)
    assert not any(flags.values()), "a dropped case is exposed, decided, recorded or was run through X"


def main():
    out = io.StringIO()

    def say(*a):
        print(*a, file=out)
    head = subprocess.run(["git", "-C", SPIKE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    say("# mermaid-spike verdict by the owner's ruling of 2026-10-13 (LOG §15)")
    say("# argv: ruling/verdict_by_ruling.py")
    say(f"# start: {stamp}")
    say(f"# nodespec HEAD: {head}")
    say(f"# python: {sys.version.split()[0]}")
    say("# bound: False (the bound `aggregate` is never run, by the owner's ruling)")
    say("")
    summary, filt, dropped = filtered_summary()
    check(summary, filt, dropped, out)
    v = AG.verdict(filt)
    path = os.path.join(RESULTS, "verdict-by-ruling.json")
    CLI.jdump(v, path)
    say("identity:", v["identity"]["verdict"], v["identity"].get("reason", ""))
    say("structure:", v["structure"]["verdict"], v["structure"].get("reason", ""))
    say(f"wrote results/verdict-by-ruling.json, sha256 {hashlib.sha256(open(path, 'rb').read()).hexdigest()}")
    say("")
    say(f"# end: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    say("# exited: exit status 0")
    text = out.getvalue()
    tp = os.path.join(RESULTS, "transcripts", stamp[:10] + "T" + stamp[11:19].replace(":", "") + "Z-verdict-by-ruling.txt")
    with open(tp, "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
