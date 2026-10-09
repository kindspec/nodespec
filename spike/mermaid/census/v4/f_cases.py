"""Census check for stratum F evaluable both-sides merges: distinct triples,
and whether each leg changes the diagram after dropping blank lines, %% comment
lines and surrounding whitespace. Reads only the three input blobs; never merges.

usage: python3 -I f_cases.py <bare-repo> <owner/name>
"""
import hashlib
import re
import subprocess
import sys

repo, name = sys.argv[1], sys.argv[2]
SUF = (".mmd", ".mermaid")
KW = re.compile(r"^\s*(flowchart|graph)\b", re.I)


def git(*a, check=True):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"git {a[0]} failed: {r.stderr.decode(errors='replace')}")
    return r


def norm(blob):
    t = git("cat-file", "blob", blob).stdout.decode("utf-8", "replace").splitlines()
    return tuple(s.strip() for s in t if s.strip() and not s.strip().startswith("%%"))


def isflow(lines):
    i = 0
    if lines and lines[0] == "---":
        i = lines.index("---", 1) + 1 if "---" in lines[1:] else len(lines)
    return i < len(lines) and bool(KW.match(lines[i]))


def changed(b, x):
    d = {}
    t = git("diff-tree", "--no-renames", "-r", "-z", b, x).stdout.decode("utf-8", "surrogateescape").split("\0")
    k = 0
    while k + 1 < len(t):
        mm = t[k].split()
        if len(mm) >= 5 and t[k + 1].lower().endswith(SUF):
            d[t[k + 1]] = (mm[4], mm[3])
        k += 2
    return d


seen = set()
for line in git("rev-list", "--merges", "--parents", "HEAD").stdout.decode().split("\n"):
    f = line.split()
    if len(f) != 3:
        continue
    bases = git("merge-base", "--all", f[1], f[2], check=False).stdout.decode().split()
    if len(bases) != 1:
        continue
    b = bases[0]
    c1, c2 = changed(b, f[1]), changed(b, f[2])
    for p in set(c1) & set(c2):
        (s1, b1), (s2, b2) = c1[p], c2[p]
        if (s1 == "A" and s2 == "A") or "D" in (s1, s2) or b1 == b2:
            continue
        bb = git("rev-parse", f"{b}:{p}").stdout.decode().strip()
        N = [norm(x) for x in (bb, b1, b2)]
        key = (bb, b1, b2)
        dup = key in seen
        seen.add(key)
        print("\t".join(map(str, [name, f[0][:12], p, all(isflow(n) for n in N), N[1] != N[0], N[2] != N[0], "dup" if dup else "new"])))
