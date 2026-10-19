# SPDX-License-Identifier: MIT
"""Run each candidate in cases/ once, in name order, against CRITERION.md §1.

    python3 -I -S -B existence/run.py OUT.jsonl

Calls the spike's harness at spike/mermaid/harness, unchanged: case.prepare
reads the three inputs (stratum F, a .mmd file) and R parses them; gitops
merges them as commits with stock git and no config; case.outcome parses the
merged file under R and judges it with the spike's oracle. One JSON line per
candidate, then a summary line. Refuses to write over an existing OUT, so a
candidate is not run twice.
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


def run_one(name, R):
    d = os.path.join(HERE, "cases", name)
    texts = [open(os.path.join(d, f), encoding="utf-8").read() for f in ("base.mmd", "ours.mmd", "theirs.mmd")]
    row = {"case": name, "met": False}
    prep = C.prepare("F", *texts, R)
    if prep["excluded"]:
        row.update(failed="1", why=prep["excluded"])
        return row
    m = G.merge_texts(PATH, *(t.encode("utf-8") for t in texts))
    res = C.outcome(prep, texts, m, R, path=PATH)
    row["outcome"] = res["outcome"]
    row["why"] = res.get("why")
    row["merged"] = m.merged.decode("utf-8") if m.merged is not None else None
    row["records"] = res["records"]
    row["lint_new"] = res.get("lint_new", [])
    if res["outcome"] == "E":
        row["failed"] = "3" if "parse" in (res.get("why") or "") else "2"
        return row
    if res["outcome"] != "JUDGED":
        row["failed"] = "3"
        return row
    ident = [r for r in res["records"] if r["category"] in IDENTITY]
    if not ident:
        row["failed"] = "4"
        return row
    if not any(r["tier"] == "A" for r in ident):
        row["failed"] = "5"
        return row
    row["met"] = True
    return row


def main(out):
    if os.path.exists(out):
        sys.exit(f"{out} exists; each candidate runs once")
    RB.check_install()
    R = RB.RCache()
    names = sorted(os.listdir(os.path.join(HERE, "cases")))
    rows = [run_one(n, R) for n in names]
    with open(out, "x", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        met = [r["case"] for r in rows if r["met"]]
        summary = {"summary": True, "candidates": len(rows), "met": met,
                   "verdict": "met" if met else "not met", "r": R.config, "git": G.version()}
        f.write(json.dumps(summary, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
