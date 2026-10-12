#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""Builds the prompt for X's invocation 4 (LOG §11).

    python3 -I -S -B harness/x4_prompt.py --extractor X1/extract2.py \\
        --prompt OUT/x4-prompt.txt --index OUT/x4-index.tsv

The set of inputs is not chosen by hand: it is every V-fixture on which
V5's comparison (xrun.compare, as `vfix.py v5` runs it) finds X1's output
and H's apart. For each, the prompt holds the input files verbatim, then
X1's output, then H's output, under neutral labels. The fixture names are
left out of the prompt, since they name F's expected category; the index
file maps each label to its fixture.

X1 is run here on the same four files under their plain names (base.<ext>,
o.<ext>, t.<ext>, merged.<ext>) in a scratch directory, so its output holds
no host path; its comparison with H must come out as V5's did, or this
script stops.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SPIKE = os.path.dirname(HERE)

from ms import rbridge as RB  # noqa: E402
from ms import xrun as XR  # noqa: E402
import mermaid_spike as CLI  # noqa: E402

OPENING = ("This is a new invocation of the second-extractor role. Your working directory holds your "
           "extractor and CHOICES.md as of your first invocation. On each input below, your extractor's "
           "output differs from another reader's. Both outputs are shown, yours first, without saying "
           "which is right. Decide each from SPEC.md alone. You may keep or change your extractor. "
           "Record each decision and its reason in CHOICES.md under the heading 'Invocation 4'.")


def fence(text):
    run = max([len(m) for m in re.findall(r"`+", text)] + [2])
    return "`" * (run + 1)


def block(title, text, info=""):
    f = fence(text)
    body = text if text.endswith("\n") else text + "\n"
    return f"### {title}\n\n{f}{info}\n{body}{f}\n"


def run_plain(extractor, stratum, texts):
    d = tempfile.mkdtemp(prefix="x4p.")
    try:
        ext = "md" if stratum == "D" else "mmd"
        names = [f"{n}.{ext}" for n in ("base", "o", "t", "merged")]
        for n, t in zip(names, texts):
            with open(os.path.join(d, n), "wb") as f:
                f.write(t.encode("utf-8"))
        r = subprocess.run(["python3", "-I", extractor, stratum] + names, capture_output=True, text=True,
                           timeout=XR.TIMEOUT, cwd=d,
                           env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C.UTF-8"})
        return names, r.returncode, r.stdout, r.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--dir", default=os.path.join(SPIKE, "v-fixtures"))
    ap.add_argument("--extractor", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--index", required=True)
    a = ap.parse_args()
    fx = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(a.dir, "*", "expect.json")))
    if not fx:
        raise SystemExit(f"no V-fixture under {a.dir}")
    R = RB.RCache()
    parts, index, n = [OPENING + "\n"], [], 0
    for f in fx:
        name = os.path.basename(f)
        r = CLI.run_fixture_dir(f, R, a.extractor)
        if r.get("x_agree"):
            continue
        st = r["stratum"]
        ext = "md" if st == "D" else "mmd"
        texts = [open(os.path.join(f, f"{x}.{ext}"), encoding="utf-8").read() for x in ("base", "o", "t")]
        texts.append(r.get("merged") or "")
        names, rc, out, err = run_plain(a.extractor, st, texts)
        try:
            xo = XR.x_view(json.loads(out)) if rc == 0 and out.strip() else None
        except ValueError:
            xo = None
        agree, _ = XR.compare(r["records"], r["exposed"], xo, None if xo else f"exit {rc}")
        if agree:
            raise SystemExit(f"{name}: X1 run on plain names agrees with H, unlike V5's run")
        n += 1
        index.append(f"input {n}\t{name}\t{r.get('x_detail')}")
        h_out = {"outcome": r.get("outcome"), "exposed": r["exposed"], "records": r["records"]}
        parts.append(f"## Input {n}\n\nCommand: `python3 -I extract2.py {st} {' '.join(names)}`\n")
        for nm, t in zip(names, texts):
            parts.append(block(nm, t))
        mine = out if rc == 0 else f"exit status {rc}\n{err}"
        parts.append(block("Your extractor's output", mine, "json" if rc == 0 else ""))
        parts.append(block("The other reader's output", json.dumps(h_out, indent=1, ensure_ascii=False), "json"))
    if not n:
        raise SystemExit("X1 agrees with H on every V-fixture: there is nothing to put to X")
    with open(a.prompt, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    with open(a.index, "w", encoding="utf-8") as fh:
        fh.write(f"# x4_prompt.py: V-fixtures where X1 and H differ ({n} of {len(fx)})\n")
        fh.write("\n".join(index) + "\n")
    print(f"{n} of {len(fx)} V-fixtures differ; prompt {os.path.basename(a.prompt)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
