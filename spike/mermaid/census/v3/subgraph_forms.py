"""Count subgraph header forms in flowchart blobs at the pin. Counts only.

usage: python3 -I subgraph_forms.py mmd <bare-repo> <owner/name> <paths-file>
       python3 -I subgraph_forms.py md  <checkout>  <owner/name> <paths-file>

A header `subgraph X` gets an explicit id when X is `id [title]` / `id["title"]`
(an id token followed by a bracket) or a single token with no whitespace and no
quote. Otherwise (several words, or a quoted title alone) Mermaid assigns a
positional id `subGraphN`. Content is read only to classify header lines; only
counts are printed.
Prints: corpus blobs blobs_with_subgraph blobs_with_auto_id blobs_with_duplicate_auto_title
        headers headers_auto
"""
import os
import re
import subprocess
import sys

mode, d, name, pf = sys.argv[1:5]
paths = [p for p in open(pf, "rb").read().decode("utf-8", "surrogateescape").split("\0") if p]
HDR = re.compile(r"^\s*subgraph\b(.*)$")
EXPL = re.compile(r'^\s*[^\s\[\]"(){}]+\s*(\[.*|\(.*|\{.*)?$')
OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b", re.I)


def text(p):
    if mode == "mmd":
        r = subprocess.run(["git", "-C", d, "-c", "core.quotepath=off", "cat-file", "blob", f"HEAD:{p}"], capture_output=True)
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
    try:
        return open(os.path.join(d, p), encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def diagram_lines(t):
    L = t.splitlines()
    if mode == "mmd":
        return L
    out, k = [], 0
    while k < len(L):
        m = OPEN.match(L[k])
        if m:
            ch, n = m.group(1)[0], len(m.group(1))
            j = k + 1
            while j < len(L) and not re.match(r"^ {0,3}" + re.escape(ch) + "{" + str(n) + r",}\s*$", L[j]):
                j += 1
            out += L[k + 1:j]
            k = j + 1
        else:
            k += 1
    return out


b = bs = ba = bd = h = ha = 0
for p in paths:
    t = text(p)
    if t is None:
        continue
    b += 1
    titles = []
    has = auto = False
    for ln in diagram_lines(t):
        m = HDR.match(ln)
        if not m:
            continue
        rest = m.group(1).strip()
        if not rest:
            continue
        has = True
        h += 1
        if not EXPL.match(rest) or rest.startswith('"'):
            auto = True
            ha += 1
            titles.append(rest.strip('"'))
    bs += has
    ba += auto
    bd += len(titles) != len(set(titles))
print("\t".join(map(str, [name, b, bs, ba, bd, h, ha])))
