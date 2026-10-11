#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION.md §11.2 V2: Appendix B.1's replay reproduces V[i+a+b]
when applied to V[i+a].

    python3 -I -S -B harness/v2.py [--histories N]

R-v2 (LOG §2): F's prompt is frozen verbatim and asks for no history, and
Appendix D defines no layout for one, so V2 runs over histories H builds
itself: seed flowcharts edited one Appendix B.2 operation at a time
(ms/sgen.py), with random.Random seeded from the history's index. Every
version keeps its lines distinct, so each anchor in V[i+a] is unique there.
For every i and every (a, b) in {(1,1), (1,3), (3,1)}, replay(V[i+a], V[i+a],
V[i+a+b]) must equal V[i+a+b] byte for byte. Exit 1 on any mismatch, any
non-commuting replay, or zero histories.
"""
import argparse
import random
import sys
import os

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ms import replay as RP  # noqa: E402
from ms import sgen as SG  # noqa: E402

SEEDS = [
    "flowchart TD\n  a[Alpha] --> b[Beta]\n  b --> c[Gamma]\n  c --> d[(Store)]\n",
    "graph LR\n  api[API] --> db[(DB)]\n  ui[UI] --> api\n  subgraph back [Back end]\n    db\n    cache[Cache]\n  end\n",
    "flowchart TD\n  s1([Start]) --> q{Ready?}\n  q -->|yes| go[Go]\n  q -->|no| wait[Wait]\n"
    "  classDef hot fill:#f96\n  class go hot\n",
]


def history(seed_text, n, rng):
    vs = [seed_text]
    while len(vs) < n:
        for _ in range(30):
            op = SG.draw(SG.FALLBACK_MIX, rng)
            try:
                new = SG.apply_op(op, vs[-1], rng)
            except Exception:  # noqa: BLE001 -- an op that does not apply is redrawn
                new = None
            if new and new != vs[-1] and len(set(new.splitlines())) == len(new.splitlines()):
                vs.append(new)
                break
        else:
            return None
    return vs


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--histories", type=int, default=60)
    a = ap.parse_args()
    checked = fails = hs = 0
    for k in range(a.histories):
        rng = random.Random(f"nodespec-mermaid:V2:{k}")
        vs = history(SEEDS[k % len(SEEDS)], 6, rng)
        if vs is None:
            continue
        hs += 1
        for i in range(len(vs)):
            for x, y in ((1, 1), (1, 3), (3, 1)):
                if i + x + y >= len(vs):
                    continue
                checked += 1
                try:
                    ok = RP.replay(vs[i + x], vs[i + x], vs[i + x + y]) == vs[i + x + y]
                    why = "differs"
                except RP.NonCommuting as e:
                    ok, why = False, f"non-commuting: {e}"
                if not ok:
                    fails += 1
                    print(f"  FAIL  history {k} i={i} ({x},{y}): {why}")
    print(f"\nV2: {hs} histories, {checked} replays, {fails} failed")
    ok = hs > 0 and checked > 0 and fails == 0
    print("V2:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
