#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""Red first, for the owner's ruling of 2026-10-13 (LOG §15).

- RED: the frozen aggregate.verdict, on the bound summary exactly as
  cmd_aggregate builds it (mermaid_spike.bound_summary), raises TypeError
  from sorting cases whose key is null.
- GREEN: on the same summary less the null-key cases (verdict_by_ruling's
  filter), it returns a verdict, and that verdict serialises to the same bytes
  as results/verdict-by-ruling.json.

Exit 0 only if both hold. It writes nothing under results/ but its transcript.

    python3 -I -S -B ruling/redfirst.py
"""
import datetime
import io
import json
import os
import subprocess
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SPIKE, "harness"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

import mermaid_spike as CLI  # noqa: E402
from ms import aggregate as AG  # noqa: E402
import verdict_by_ruling as VR  # noqa: E402


def main():
    out = io.StringIO()

    def say(*a):
        print(*a, file=out)
    head = subprocess.run(["git", "-C", SPIKE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    say("# mermaid-spike red-first check for the owner's ruling of 2026-10-13 (LOG §15)")
    say("# argv: ruling/redfirst.py")
    say(f"# start: {stamp}")
    say(f"# nodespec HEAD: {head}")
    say("# bound: False")
    say("")
    ok = True
    summary, _ = CLI.bound_summary(VR.RESULTS)
    try:
        AG.verdict(summary)
        say("RED   FAIL  the frozen verdict() ran on the unfiltered summary; expected a TypeError")
        ok = False
    except TypeError as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        say(f"RED   PASS  the frozen verdict() on the unfiltered summary raises TypeError: {e}")
        say(f"            at {os.path.basename(tb.filename)}:{tb.lineno}: {tb.line}")
    _, filt, dropped = VR.filtered_summary()
    try:
        v = AG.verdict(filt)
    except Exception as e:  # noqa: BLE001
        say(f"GREEN FAIL  the frozen verdict() on the filtered summary raised {type(e).__name__}: {e}")
        return finish(out, stamp, 1)
    path = os.path.join(VR.RESULTS, "verdict-by-ruling.json")
    mine = json.dumps(v, sort_keys=True, indent=1, ensure_ascii=False, default=str) + "\n"
    same = os.path.isfile(path) and open(path, encoding="utf-8").read() == mine
    say(f"GREEN {'PASS' if same else 'FAIL'}  the frozen verdict() on the summary less {len(dropped)} null-key "
        f"cases returns a verdict{', byte-identical to results/verdict-by-ruling.json' if same else ''}")
    ok = ok and same
    return finish(out, stamp, 0 if ok else 1)


def finish(out, stamp, rc):
    print("", file=out)
    print(f"# end: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}", file=out)
    print(f"# exited: exit status {rc}", file=out)
    text = out.getvalue()
    tp = os.path.join(VR.RESULTS, "transcripts", stamp[:10] + "T" + stamp[11:19].replace(":", "") + "Z-redfirst.txt")
    with open(tp, "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.write(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())
