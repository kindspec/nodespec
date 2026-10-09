"""Write the selected flowchart paths of one corpus, NUL-separated, to stdout.

usage: python3 -I flow_paths.py mmd <bare-repo>
       python3 -I flow_paths.py md  <shallow-worktree-at-pin>

The same content reads as mmd_counts.py and md_counts.py (diagram-type keyword
only), and the same path-segment rule for generated files.
"""
import os
import re
import subprocess
import sys

mode, d = sys.argv[1], sys.argv[2]
KW = re.compile(r"^\s*(flowchart|graph)\b", re.I)
FENCE = re.compile(r"^\s*(```|~~~)\s*mermaid\s*$", re.I)
GEN = {"testdata", "test", "tests", "__tests__", "__snapshots__", "snapshots", "baseline", "baselines",
       "fixture", "fixtures", "generated", "gen", "dist", "build", "out", "node_modules", "vendor"}


def first_kw(lines):
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    for ln in lines[i:]:
        s = ln.strip()
        if s and not s.startswith("%%"):
            return bool(KW.match(s))
    return False


def gen(p):
    return bool(set(s.lower() for s in p.split("/")[:-1]) & GEN)


out = []
if mode == "mmd":
    g = ["git", "-C", d, "-c", "core.quotepath=off"]
    toks = subprocess.run(g + ["log", "--no-merges", "--no-renames", "--format=@%H", "--raw", "--no-abbrev", "-z", "HEAD"],
                          capture_output=True).stdout.decode("utf-8", "surrogateescape").split("\0")
    last = {}
    i = 0
    while i < len(toks):
        t = toks[i].lstrip("\n")
        if t.startswith("@") or not t:
            i += 1
            continue
        m = t.split()
        p = toks[i + 1]
        i += 2
        if m[4][0] in "CR":
            i += 1
            continue
        if m[4][0] in "AM" and p.lower().endswith((".mmd", ".mermaid")) and p not in last:
            last[p] = m[3]  # log is newest first: first sighting is the last version
    for p, b in last.items():
        if gen(p):
            continue
        r = subprocess.run(g + ["cat-file", "blob", b], capture_output=True)
        if r.returncode == 0 and first_kw(r.stdout.decode("utf-8", "replace").splitlines()):
            out.append(p)
else:
    ls = subprocess.run(["git", "-C", d, "-c", "core.quotepath=off", "ls-files", "-z"],
                        capture_output=True).stdout.decode("utf-8", "surrogateescape").split("\0")
    for p in ls:
        if not p.lower().endswith(".md") or gen(p):
            continue
        L = open(os.path.join(d, p), encoding="utf-8", errors="replace").read().splitlines()
        if any(FENCE.match(l) and first_kw(L[k + 1:]) for k, l in enumerate(L)):
            out.append(p)
sys.stdout.buffer.write("\0".join(out).encode("utf-8", "surrogateescape"))
