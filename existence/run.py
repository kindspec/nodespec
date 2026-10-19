# SPDX-License-Identifier: MIT
"""Run each candidate in cases/ once, in name order, against CRITERION.md §1.

    python3 -I -S -B existence/run.py RESULTS.jsonl

Calls the spike's harness at spike/mermaid/harness, unchanged: case.prepare
reads the three inputs (stratum F, a .mmd file) and R parses them; gitops
merges them as commits with stock git and no config; case.outcome parses the
merged file under R and judges it with the spike's oracle.

RESULTS holds one JSON line per candidate that has run, and only grows: a
candidate already in it is never run again, and only candidates not yet in it
run. The summary is printed, not stored.

Conditions 2 to 5 are judged here. Condition 1, that each leg is one
Appendix B.2 operation, is a property of the case files, judged by review and
recorded as such. Every failing condition is listed, not only the first.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "spike", "mermaid", "harness"))

from ms import case as C  # noqa: E402
from ms import gitops as G  # noqa: E402
from ms import rbridge as RB  # noqa: E402

IDENTITY = {"I1", "I2", "I3", "I4"}
PATH = "diagram/diagram.mmd"
NOT_PARSED = "R does not parse the merged diagram"


def run_one(name, R):
    d = os.path.join(HERE, "cases", name)
    texts = [open(os.path.join(d, f), encoding="utf-8").read() for f in ("base.mmd", "ours.mmd", "theirs.mmd")]
    row = {"case": name, "condition 1": "by review", "failed": [], "met": False}
    prep = C.prepare("F", *texts, R)
    if prep["excluded"]:
        # The harness cannot judge these inputs: none of 2 to 5 is reached.
        row.update(outcome="not judgeable", why=prep["excluded"], failed=["2", "3", "4", "5"])
        return row
    m = G.merge_texts(PATH, *(t.encode("utf-8") for t in texts))
    res = C.outcome(prep, texts, m, R, path=PATH)
    why = res.get("why") or ""
    row.update(outcome=res["outcome"], why=res.get("why"), records=res["records"],
               lint_new=res.get("lint_new", []),
               merged=m.merged.decode("utf-8", "replace") if m.merged is not None else None)
    if res["outcome"] == "E":
        # A conflict fails 2; a merged file R refuses fails 3. Neither is judged.
        row["failed"] = ["3", "4", "5"] if why.startswith(NOT_PARSED) else ["2", "4", "5"]
        return row
    if res["outcome"] == "G0":
        row["failed"] = ["3", "4", "5"]
        return row
    if res["outcome"] != "JUDGED":
        # OUT-OF-SUBSET or DUP-TITLE: R parsed it, the oracle cannot decide it.
        row["failed"] = ["4", "5"]
        return row
    ident = [r for r in res["records"] if r["category"] in IDENTITY]
    if not ident:
        row["failed"] = ["4", "5"]
    elif not any(r["tier"] == "A" for r in ident):
        row["failed"] = ["5"]
    else:
        row["met"] = True
    return row


def main(results):
    done = []
    if os.path.exists(results):
        done = [json.loads(line) for line in open(results, encoding="utf-8") if line.strip()]
    seen = {r["case"] for r in done}
    names = sorted(os.listdir(os.path.join(HERE, "cases")))
    todo = [n for n in names if n not in seen]
    if not todo:
        sys.exit(f"every candidate in cases/ is already in {results}; each runs once")
    RB.check_install()
    R = RB.RCache()
    with open(results, "a", encoding="utf-8") as f:
        for n in todo:
            row = run_one(n, R)
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            done.append(row)
    met = [r["case"] for r in done if r["met"]]
    print(json.dumps({"ran now": todo, "candidates": len(done), "met": met,
                      "verdict (conditions 2 to 5)": "met" if met else "not met",
                      "r": R.config, "git": G.version()}, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
