"""Path-level history counts for Markdown files holding a Mermaid flowchart fence.

usage: python3 -I md_counts.py <shallow-worktree-at-pin> <bare-blobless-repo> <owner/name>

Content read, bounded: at the pin only, each .md file in the shallow checkout is
scanned for a line "```mermaid" whose first following line that is not blank and
not a %% comment starts with "flowchart" or "graph". Only the path, the number of
such fences, and whether the file has exactly one Mermaid fence are kept. Nothing
else from the content is kept or printed. Earlier versions are not read, so these
are path-level counts: a version pair of such a path need not change its fence.
Nothing is merged and no merge result is read.

Prints one tab-separated line:
repo pin md_with_flow_fence md_single_fence authors_mod top_author_share bot_share
version_pairs not_ancestor triples triples_on_ancestry merges_2p multibase
both_sides_paths addadd delmod convergent evaluable evaluable_single_fence
"""
import collections
import os
import re
import subprocess
import sys

wt, repo, name = sys.argv[1], sys.argv[2], sys.argv[3]
KW = re.compile(r"^\s*(flowchart|graph)\b", re.I)
FENCE = re.compile(r"^\s*(```|~~~)\s*mermaid\s*$", re.I)


def git(*a, check=True):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"git {a[0]} failed in {repo}: {r.stderr.decode(errors='replace')}")
    return r


pin = git("rev-parse", "HEAD").stdout.decode().strip()
wpin = subprocess.run(["git", "-C", wt, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
if wpin != pin:
    sys.exit(f"pin mismatch {wpin} {pin}")
ls = subprocess.run(["git", "-C", wt, "-c", "core.quotepath=off", "ls-files", "-z"], capture_output=True).stdout.decode("utf-8", "surrogateescape").split("\0")
flow, single = set(), set()
for p in ls:
    if not p.lower().endswith(".md"):
        continue
    try:
        lines = open(os.path.join(wt, p), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        continue
    nm = nf = 0
    for k, ln in enumerate(lines):
        if FENCE.match(ln):
            nm += 1
            for ln2 in lines[k + 1:]:
                s = ln2.strip()
                if not s or s.startswith("%%"):
                    continue
                nf += bool(KW.match(s))
                break
    if nf:
        flow.add(p)
        if nm == 1:
            single.add(p)

out = git("log", "--no-merges", "--no-renames", "--topo-order", "--reverse",
          "--format=@%H%x09%an%x09%ae", "--raw", "--no-abbrev", "-z", "HEAD", "--", "*.md").stdout.decode("utf-8", "surrogateescape")
toks = out.split("\0")
vers = collections.defaultdict(list)
seg = collections.Counter()
fa = collections.Counter()
i = 0
while i < len(toks):
    t = toks[i].lstrip("\n")
    if t.startswith("@"):
        cur, an, ae = t[1:].split("\t")
        au = f"{an} <{ae}>"
        i += 1
        continue
    if not t:
        i += 1
        continue
    meta = t.split()
    st, p = meta[4], toks[i + 1]
    i += 2
    if st[0] in "CR":
        i += 1
        continue
    if p not in flow:
        continue
    if st == "D":
        seg[p] += 1
    elif st[0] in "AM":
        vers[(p, seg[p])].append(cur)
        if st[0] == "M":
            fa[au] += 1


def anc(x, y):
    return git("merge-base", "--is-ancestor", x, y, check=False).returncode == 0


pairs = nonanc = tri = trc = 0
for (p, s), cs in vers.items():
    ok = [anc(x, y) for x, y in zip(cs, cs[1:])]
    pairs += len(ok)
    nonanc += ok.count(False)
    if len(cs) >= 3:
        tri += len(cs) - 2
        trc += sum(1 for k in range(len(ok) - 1) if ok[k] and ok[k + 1])
n = sum(fa.values())
top = fa.most_common(1)[0] if fa else ("-", 0)
bots = sum(v for k, v in fa.items() if "bot" in k.lower())

m2 = multi = bs = aa = dm = cv = ev = evs = 0
for line in git("rev-list", "--merges", "--parents", "HEAD").stdout.decode().split("\n"):
    f = line.split()
    if len(f) != 3:
        continue
    m2 += 1
    _, p1, p2 = f
    bases = git("merge-base", "--all", p1, p2, check=False).stdout.decode().split()
    if len(bases) != 1:
        multi += len(bases) > 1
        continue
    b = bases[0]

    def changed(x):
        d = {}
        t = git("diff-tree", "--no-renames", "-r", "-z", b, x, "--", "*.md").stdout.decode("utf-8", "surrogateescape").split("\0")
        k = 0
        while k + 1 < len(t):
            mm = t[k].split()
            if len(mm) >= 5 and t[k + 1] in flow:
                d[t[k + 1]] = (mm[4], mm[3])
            k += 2
        return d
    c1, c2 = changed(p1), changed(p2)
    for p in set(c1) & set(c2):
        bs += 1
        (s1, b1), (s2, b2) = c1[p], c2[p]
        if s1 == "A" and s2 == "A":
            aa += 1
        elif "D" in (s1, s2):
            dm += 1
        elif b1 == b2:
            cv += 1
        else:
            ev += 1
            evs += p in single

print("\t".join(map(str, [name, pin, len(flow), len(single), len(fa), f"{top[1]}/{n}", f"{bots}/{n}",
                          pairs, nonanc, tri, trc, m2, multi, bs, aa, dm, cv, ev, evs])))
