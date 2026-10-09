"""Count flowchart diagrams at the pin whose header keyword is not lower case. Counts only.

usage: python3 -I v41/mixed_case.py <mmd|md> <repo-or-checkout> <paths-file>
Reads only the diagram's first keyword line. Prints: diagrams mixed_case
"""
import os, re, subprocess, sys
mode, d, pf = sys.argv[1:4]
KWI = re.compile(r"^(flowchart|flowchart-elk|graph)(\s|$)", re.I)
KW = re.compile(r"^(flowchart|flowchart-elk|graph)(\s|$)")
OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b", re.I)
def first(lines):
    i = 0
    while i < len(lines) and not lines[i].strip(): i += 1
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---": i += 1
        i += 1
    for ln in lines[i:]:
        s = ln.strip()
        if s and not s.startswith("%%"): return s
    return ""
n = mixed = 0
for p in [p for p in open(pf, "rb").read().decode("utf-8", "surrogateescape").split("\0") if p]:
    if mode == "mmd":
        r = subprocess.run(["git", "-C", d, "cat-file", "blob", f"HEAD:{p}"], capture_output=True)
        if r.returncode: continue
        bodies = [r.stdout.decode("utf-8", "replace").splitlines()]
    else:
        L = open(os.path.join(d, p), encoding="utf-8", errors="replace").read().splitlines()
        bodies, k = [], 0
        while k < len(L):
            if OPEN.match(L[k]):
                j = k + 1
                while j < len(L) and not re.match(r"^ {0,3}(`{3,}|~{3,})\s*$", L[j]): j += 1
                bodies.append(L[k + 1:j]); k = j + 1
            else: k += 1
    for b in bodies:
        f = first(b)
        if KWI.match(f):
            n += 1
            mixed += not KW.match(f)
print(n, mixed)
