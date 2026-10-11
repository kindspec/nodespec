#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""A syntax census over the archived corpora, taken before Arm 0 (LOG §11).

    python3 -I -S -B harness/syntax_census.py --archive DIR \\
        --private-map MAP --private-table TABLE

It asks whether two readings on which X (choices 5 and 6) and H differ can
touch the population at all:

(a) Mermaid fence openers that §3's pattern accepts and X's does not:
    `mermaid-example`, a case variant of `mermaid` other than lower case,
    and (counted apart) any other text after `mermaid` on the opener line.
(b) Lines that are exactly `=======`, in blobs that hold a §3 Mermaid
    fence: inside or outside a fence, and whether the blob also holds a
    `<<<<<<<` line.

It reads trees and blobs only (ms/history.py's walk and §7.4 selection). It
runs no arm, no merge, and not R, and it reads no outcome. It prints totals
only: no corpus, path or content.

Scopes:
- pin: every .md blob in the tree at each stratum-D corpus's pin;
- population: every version (added or modified, reachable from the pin) of
  every path §7.4 selects for the row's stratum.
"""
import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ms import corpus as K  # noqa: E402
from ms import fence as FN  # noqa: E402
from ms import history as HI  # noqa: E402

# X's opener, as its extract2.py (invocations 1 and 4) has it: case-sensitive,
# and nothing but blanks after "mermaid". Its group 1 is the fence run, as in
# fence.OPENER, so fence.fences can use either.
X_OPENER = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*mermaid[ \t]*$")
WORD = re.compile(r"mermaid", re.IGNORECASE)
MARK_EQ = re.compile(r"^={7}\r?$")
MARK_LT = re.compile(r"^<{7}")


def kind(line):
    """Why §3 accepts an opener line X does not, or None if both accept it."""
    if X_OPENER.match(line):
        return None
    m = FN.OPENER.match(line)
    tail = line[m.end(1):].lstrip(" \t")
    if m.group(2):
        return "mermaid-example"
    if not tail.startswith("mermaid"):
        return "case variant"
    return "other text after mermaid"


def scan(text):
    """§3's fences, with their line spans: [(opener index, end index, opener)]."""
    ls = [b for _, b, _ in FN._lines(text)]
    out, i = [], 0
    while i < len(ls):
        m = FN.OPENER.match(ls[i])
        if not m:
            i += 1
            continue
        ch, n = m.group(1)[0], len(m.group(1))
        j = i + 1
        while j < len(ls) and not (len(ls[j]) >= n and set(ls[j]) == {ch}):
            j += 1
        out.append((i, j, ls[i]))
        i = j + 1
    return ls, out


def x_diagram(stratum, text):
    """diagram_of under X's opener."""
    saved = FN.OPENER
    FN.OPENER = X_OPENER
    try:
        return FN.diagram_of(stratum, text)
    finally:
        FN.OPENER = saved


def tally(text, c, scope):
    ls, fs = scan(text)
    if not fs:
        return set()
    hits = set()
    for _, _, op in fs:
        k = kind(op)
        if k:
            c[(scope, "a: fences", k)] += 1
            hits.add("a:" + k)
    inside = set()
    for i, j, _ in fs:
        inside.update(range(i, j + 1))
    lt = any(MARK_LT.match(x) for x in ls)
    for n, x in enumerate(ls):
        if MARK_EQ.match(x):
            where = "inside a fence" if n in inside else "outside a fence"
            c[(scope, "b: lines", f"{where}, blob {'with' if lt else 'without'} a <<<<<<< line")] += 1
            hits.add(f"b:{where}")
            hits.add(f"b:{'with' if lt else 'without'} <<<<<<<")
    for h in hits:
        c[(scope, "blobs holding", h)] += 1
    c[(scope, "blobs", "holding a §3 Mermaid fence")] += 1
    return hits


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--private-map", required=True)
    ap.add_argument("--private-table", required=True)
    a = ap.parse_args()
    head = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"# syntax census, {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}")
    print(f"# nodespec HEAD: {head}")
    print("# archive, private map and private table: held by the owner (paths not recorded)")
    print("# reads trees and blobs only: no arm, no merge, no R, no outcome\n")
    public = K.load_public()
    _, ident = K.load_private(a.private_map, a.private_table, public)
    bundles = json.load(open(os.path.join(a.archive, "bundles.json"), encoding="utf-8"))
    c = collections.Counter()
    paths_a, paths_b = set(), set()
    corp_a, corp_b = set(), set()
    seen_pin, rows = set(), 0
    for r in public:
        st = {"md": "D", "mmd": "F"}.get(r["stratum"])
        lab = r["corpus"]
        ent = bundles.get(lab)
        if st is None or ent is None:
            c[("rows", "skipped", "no stratum or no bundle")] += 1
            continue
        pin = ident[(r["stratum"], lab)]["pin"]
        repo = HI.Repo(os.path.join(a.archive, ent["file"][:-len(".bundle")] + ".mirror.git"))
        if not repo.has_commit(pin):
            raise SystemExit("refusing: a pin is missing from its mirror")
        rows += 1
        walked = HI.walk(repo, pin)
        sel = HI.select(repo, pin, walked)
        _, by_path, _ = walked
        # (a) selection: would X's opener change which .md paths §7.4 selects?
        if st == "D":
            for p, ents in by_path.items():
                if FN.stratum_of(p) != "D" or FN.generated_by_path(p):
                    continue
                am = [e for e in ents if e[1] in "AM"]
                if not am:
                    continue
                txt = HI.text_of(repo, am[-1][2])
                if txt is None or FN.generated_by_declaration(txt):
                    continue
                h_in = FN.diagram_of("D", txt)[0] is not None
                x_in = x_diagram("D", txt)[0] is not None
                if h_in != x_in:
                    c[("population", "a: selection", "paths selected by §3 only" if h_in else "paths selected by X only")] += 1
                    paths_a.add((lab, p))
                    corp_a.add(lab)
        # population versions of selected paths of this row's stratum
        for p, pst in sel["selected"].items():
            if pst != st:
                continue
            c[("population", "paths", f"selected, stratum {st}")] += 1
            for blob in sorted({b for _, s, b in by_path[p] if s in "AM"}):
                txt = HI.text_of(repo, blob)
                if txt is None:
                    continue
                c[("population", "versions", f"stratum {st}")] += 1
                if st == "F":
                    if any(MARK_EQ.match(x) for x in txt.split("\n")):
                        c[("population", "b: F versions", "holding a ======= line")] += 1
                        paths_b.add((lab, p))
                        corp_b.add(lab)
                    continue
                hits = tally(txt, c, "population")
                if any(h.startswith("a:") for h in hits):
                    paths_a.add((lab, p))
                    corp_a.add(lab)
                    hd, xd = FN.diagram_of("D", txt)[0], x_diagram("D", txt)[0]
                    if hd != xd:
                        c[("population", "a: versions", "whose diagram differs under X's opener")] += 1
                if any(h.startswith("b:inside") or h.startswith("b:outside") for h in hits):
                    paths_b.add((lab, p))
                    corp_b.add(lab)
        # the tree at the pin
        if st == "D" and (lab, pin) not in seen_pin:
            seen_pin.add((lab, pin))
            raw = repo.out("ls-tree", "-r", "-z", "--full-tree", pin)
            for e in raw.split("\0"):
                if not e:
                    continue
                meta, p = e.split("\t", 1)
                if meta.split()[1] != "blob" or FN.stratum_of(p) != "D":
                    continue
                txt = HI.text_of(repo, meta.split()[2])
                if txt is not None:
                    tally(txt, c, "pin")
    print(f"corpus rows read: {rows}")
    for k in sorted(c):
        print(f"{' / '.join(k)}: {c[k]}")
    print(f"\npopulation paths touched by (a): {len(paths_a)}, in {len(corp_a)} corpora")
    print(f"population paths touched by (b): {len(paths_b)}, in {len(corp_b)} corpora")
    return 0


if __name__ == "__main__":
    sys.exit(main())
