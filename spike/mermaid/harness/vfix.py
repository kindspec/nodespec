#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""§11.2's V steps that need F's V-fixtures (and, for V5, X):

    python3 -I -S -B harness/vfix.py v1 [--dir v-fixtures]
    python3 -I -S -B harness/vfix.py v3 [--dir v-fixtures]
    python3 -I -S -B harness/vfix.py v5 [--dir v-fixtures] [--extractor x/extract2.py]

- V1: H's model equals R's on every V-fixture state, the merged one included,
  under Appendix A's mapping. A state R does not parse is reported, not
  compared.
- V3 (its V-fixture half, R-v3fix): each category fires on its V-fixtures
  and stays silent on clean ones. The fixture's category, read from its
  directory name, must fire in H; a clean fixture must give no record F's
  tiers would line, and no E. Its expect.json must use R-tiers' encoding,
  and H must fall on the same side of the A and B lines as "tiers" says:
  the line computation the sealed run uses (mermaid_spike.sealed_lines).
  Every other difference from expect.json is listed, not failed (LOG §10,
  §11).
- V5: X agrees with H on every V-fixture (§10.5's rule).

V2 does not read fixtures: it runs over histories H builds (v2.py, R-v2).

Exit 1 if any fixture fails, or if there is none: a step over zero fixtures
does not pass.
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SPIKE = os.path.dirname(HERE)

from ms import fence as FN  # noqa: E402
from ms import model as MD  # noqa: E402
from ms import rbridge as RB  # noqa: E402
from ms import xrun as XR  # noqa: E402
import mermaid_spike as CLI  # noqa: E402


PREFIX = {"i1": "I1", "i2": "I2", "i3": "I3", "i4": "I4", "g0": "G0", "g1": "G1", "g2": "G2", "g3": "G3",
          "g4": "G4", "mc": "MC", "c": "C", "d": "D", "sl": "S-LINKSTYLE", "so": "S-ORDER", "e": "E",
          "x": "exposed-E", "clean": "clean"}


def fixtures(d):
    return sorted(os.path.dirname(p) for p in glob.glob(os.path.join(d, "*", "expect.json")))


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("step", choices=("v1", "v3", "v5"))
    ap.add_argument("--dir", default=os.path.join(SPIKE, "v-fixtures"))
    ap.add_argument("--extractor", default=os.path.join(SPIKE, "x", "extract2.py"))
    a = ap.parse_args()
    fx = fixtures(a.dir)
    if not fx:
        print(f"no V-fixture under {a.dir}: {a.step.upper()} cannot pass over zero fixtures")
        return 1
    R = RB.RCache()
    fails, notes, n = [], [], 0
    for f in fx:
        name = os.path.basename(f)
        exp = json.load(open(os.path.join(f, "expect.json")))
        st = exp["stratum"]
        ext = "md" if st == "D" else "mmd"
        r = CLI.run_fixture_dir(f, R, a.extractor if a.step == "v5" else None)
        n += 1
        if a.step == "v1":
            texts = [open(os.path.join(f, f"{x}.{ext}"), encoding="utf-8").read() for x in ("base", "o", "t")]
            texts.append(r.get("merged") or "")
            for label, t in zip(("base", "o", "t", "merged"), texts):
                d, _ = FN.diagram_of(st, t)
                if d is None:
                    continue
                rr = R.get(d)
                if not rr.get("parse"):
                    print(f"  {name} {label}: R does not parse it; not compared")
                    continue
                from ms import subset as SS
                s = SS.classify(d, rr)
                if s.status == "out" and "differs" in (s.reason or ""):
                    fails.append(f"{name} {label}: {s.reason}")
                elif s.status != "in":
                    print(f"  {name} {label}: out of the subset ({s.status}: {s.reason})")
        elif a.step == "v3":
            # §11.2 V3: "Each category fires on its V-fixtures and stays silent
            # on clean ones" (R-v3fix). A fixture's category is the one F
            # wrote it for, read from its directory name as F's coverage table
            # lists it; that category must fire (an E outcome is E; an
            # exposed-and-refused fixture must be exposed and E); a clean
            # fixture must give no record F's tiers would line, and no E.
            # The A and B lines of F's tiers must match H's. Every other
            # difference with F's expectation is listed for the log.
            cat = PREFIX.get(name.split("-")[0])
            hcats = {x["category"] for x in r["records"] if x["category"] in XR.CATS}
            if r.get("outcome") == "E":
                hcats.add("E")
            fcats = {x["category"] for x in exp.get("records", [])}
            if cat is None:
                fails.append(f"{name}: no category for its name")
            elif cat == "clean":
                if hcats - {"S-ORDER"} or r["exposed"] != bool(exp.get("exposed")):
                    fails.append(f"{name}: clean, but H gives {sorted(hcats)} exposed {r['exposed']}")
            elif cat == "exposed-E":
                if not (r["exposed"] and "E" in hcats):
                    fails.append(f"{name}: should be exposed and E; H exposed {r['exposed']}, {sorted(hcats)}")
            elif cat not in hcats:
                fails.append(f"{name}: {cat} does not fire; H gives {sorted(hcats)}")
            try:
                for ln in CLI.sealed_lines([r]):
                    if ln["h"] != ln["f"]:
                        fails.append(f"{name}: {ln['group']} line {ln['line']}: H "
                                     f"{'qualifies' if ln['h'] else 'does not'}, F's tiers {exp.get('tiers')}")
            except CLI.Malformed as e:
                fails.append(f"{name}: expect.json: {e}")
            want, got = XR.norm_records(exp.get("records", [])), XR.norm_records(r["records"])
            if r.get("outcome") == "E":
                got.add(("E", ()))
            want = {(c, o if c in XR.OBJECTS_DEFINED else ()) for c, o in want} | {
                ("E", ()) for x in exp.get("records", []) if x["category"] == "E"}
            if want != got or bool(exp.get("exposed")) != r["exposed"]:
                notes.append(f"{name}: H only {sorted(got - want)[:4]}; F only {sorted(want - got)[:4]}")
        elif a.step == "v5":
            if not r.get("x_agree"):
                fails.append(f"{name}: {r.get('x_detail')}")
    for x in notes:
        print("  differs from F's expectation:", x)
    for x in fails:
        print("  FAIL ", x)
    print(f"\n{a.step.upper()}: {n} checked, {len(fails)} failed")
    ok = n > 0 and not fails
    print(f"{a.step.upper()}:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
