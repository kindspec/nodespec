"""NUL-safe history counts for Mermaid flowchart files in one bare (blobless) repo.

usage: python3 -I mmd_counts.py <bare-repo> <owner/name>

Metadata only, except one bounded content read per path: the blob of the path's
last added-or-modified version is fetched and only its diagram-type keyword is
kept (the first line that is not blank, not a %% comment, and not inside a
leading --- front-matter block). Nothing is merged. No merge result is read.

Prints one tab-separated line:
repo pin files_at_pin flow_files_at_pin(selected) flow_paths_ever(selected) gen_rule_excluded commits_touching authors
version_pairs not_ancestor_pairs triples triples_on_ancestry
top_author_share bot_share merges_2p merges_multibase both_sides_paths
both_addadd both_delmod both_convergent both_evaluable both_merges_evaluable
"""
import collections
import re
import subprocess
import sys

repo = sys.argv[1]
SUF = (".mmd", ".mermaid")
KW = re.compile(r"^\s*(flowchart|graph)\b", re.I)


def git(*a, check=True, inp=None):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a],
                       capture_output=True, input=inp)
    if check and r.returncode != 0:
        sys.exit(f"git {a[0]} failed in {repo}: {r.stderr.decode(errors='replace')}")
    return r


def is_flow(blob):
    r = git("cat-file", "blob", blob, check=False)
    if r.returncode != 0:  # v2: a failed lazy fetch is fatal, never "not a flowchart"
        sys.exit(f"blob fetch failed in {repo}: {blob}")
    lines = r.stdout.decode("utf-8", "replace").splitlines()
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
        if not s or s.startswith("%%"):
            continue
        return bool(KW.match(s))
    return False


pin = git("rev-parse", "HEAD").stdout.decode().strip()
out = git("log", "--no-merges", "--no-renames", "--topo-order", "--reverse",
          "--format=@%H%x09%an%x09%ae", "--raw", "--no-abbrev", "-z", "HEAD").stdout.decode("utf-8", "surrogateescape")
toks = out.split("\0")
vers = collections.defaultdict(list)   # (path, segment) -> [(commit, blob)]
seg = collections.Counter()
last_blob = {}
touch_commits = set()
authors_all = set()
mod_authors = collections.Counter()
mod_commit_author = {}
cur = None
i = 0
while i < len(toks):
    t = toks[i].lstrip("\n")
    if t.startswith("@"):
        cur, an, ae = t[1:].split("\t")
        cur_author = f"{an} <{ae}>"
        i += 1
        continue
    if not t:
        i += 1
        continue
    # --raw -z: ":<mode> <mode> <sha> <sha> <status>" NUL path NUL
    meta = t.split()
    st = meta[4]
    p = toks[i + 1]
    i += 2
    if st[0] in "CR":
        i += 1
        continue
    if not p.lower().endswith(SUF):
        continue
    touch_commits.add(cur)
    authors_all.add(cur_author)
    if st == "D":
        seg[p] += 1
    elif st[0] in "AM":
        vers[(p, seg[p])].append((cur, meta[3]))
        last_blob[p] = meta[3]
        if st[0] == "M":
            mod_authors[cur_author] += 1

flow = {p: is_flow(b) for p, b in last_blob.items()}
GEN = {"testdata", "test", "tests", "__tests__", "__snapshots__", "snapshots", "baseline", "baselines",
       "fixture", "fixtures", "generated", "gen", "dist", "build", "out", "node_modules", "vendor"}
flow_all = {p for p, f in flow.items() if f}
flowpaths = {p for p in flow_all if not (set(s.lower() for s in p.split("/")[:-1]) & GEN)}
# v2 sibling rule: a same-stem sibling in .dot or .json, in the tree of the path's last version
# (or at the pin if the path exists there), marks the flowchart as derived output.
last_commit = {}
for (pp, sg), cs in vers.items():
    last_commit[pp] = cs[-1][0]
def sibling(pp):
    d, _, f = pp.rpartition("/")
    stem = f.rsplit(".", 1)[0]
    c = last_commit.get(pp, "HEAD")
    names = git("ls-tree", "-z", "--name-only", f"{c}:{d}" if d else c, check=False).stdout.decode("utf-8", "surrogateescape").split("\0")
    return any(n in (stem + ".dot", stem + ".json") for n in names)
sib = {pp for pp in flowpaths if sibling(pp)}
flowpaths -= sib
gen_excl = len(flow_all) - len(flowpaths)
gen_excl = len(flow_all) - len(flowpaths)

at_pin = git("ls-tree", "-r", "-z", "--name-only", "HEAD").stdout.decode("utf-8", "surrogateescape").split("\0")
files_pin = [p for p in at_pin if p.lower().endswith(SUF)]
flow_pin = [p for p in files_pin if p in flowpaths]


def anc(x, y):
    return git("merge-base", "--is-ancestor", x, y, check=False).returncode == 0


pairs = nonanc = tri = tri_chain = 0
fa = collections.Counter()
touch_flow = set()
for (p, s), cs in vers.items():
    if p not in flowpaths:
        continue
    for c, _ in cs:
        touch_flow.add(c)
    ok = [anc(x[0], y[0]) for x, y in zip(cs, cs[1:])]
    pairs += len(ok)
    nonanc += ok.count(False)
    if len(cs) >= 3:
        tri += len(cs) - 2
        tri_chain += sum(1 for k in range(len(ok) - 1) if ok[k] and ok[k + 1])

# authors of modifying commits to flowchart paths
log2 = git("log", "--no-merges", "--no-renames", "--format=@%H%x09%an%x09%ae", "--raw", "--no-abbrev", "-z", "HEAD").stdout.decode("utf-8", "surrogateescape").split("\0")
cur = None
j = 0
while j < len(log2):
    t = log2[j].lstrip("\n")
    if t.startswith("@"):
        h, an, ae = t[1:].split("\t")
        cur = f"{an} <{ae}>"
        seen = False
        j += 1
        continue
    if not t:
        j += 1
        continue
    meta = t.split()
    st = meta[4]
    p = log2[j + 1]
    j += 2
    if st[0] in "CR":
        j += 1
        continue
    if st == "M" and p in flowpaths:
        fa[cur] += 1
n = sum(fa.values())
top = fa.most_common(1)[0] if fa else ("-", 0)
bots = sum(v for k, v in fa.items() if "bot" in k.lower())
flow_authors = len(fa)

# two-parent merges with a both-sides change to a flowchart path (tree metadata only)
m2 = multi = bs = addadd = delmod = conv = ev = 0
ev_merges = 0
for line in git("rev-list", "--merges", "--parents", "HEAD").stdout.decode().split("\n"):
    f = line.split()
    if len(f) != 3:
        continue
    m2 += 1
    _, p1, p2 = f
    bases = git("merge-base", "--all", p1, p2, check=False).stdout.decode().split()
    if len(bases) != 1:
        if len(bases) > 1:
            multi += 1
        continue
    b = bases[0]

    def changed(x):
        d = {}
        t = git("diff-tree", "--no-renames", "-r", "-z", b, x).stdout.decode("utf-8", "surrogateescape").split("\0")
        k = 0
        while k + 1 < len(t):
            mm = t[k].split()
            if len(mm) >= 5 and t[k + 1] in flowpaths:
                d[t[k + 1]] = (mm[4], mm[3])
            k += 2
        return d
    c1, c2 = changed(p1), changed(p2)
    hit = False
    for p in set(c1) & set(c2):
        bs += 1
        s1, b1 = c1[p]
        s2, b2 = c2[p]
        if s1 == "A" and s2 == "A":
            addadd += 1
        elif "D" in (s1, s2):
            delmod += 1
        elif b1 == b2:
            conv += 1
        else:
            ev += 1
            hit = True
    ev_merges += hit

name = sys.argv[2]
print("\t".join(map(str, [name, pin, len(files_pin), len(flow_pin), len(flowpaths), gen_excl, len(touch_flow),
                          flow_authors, pairs, nonanc, tri, tri_chain, f"{top[1]}/{n}", f"{bots}/{n}",
                          m2, multi, bs, addadd, delmod, conv, ev, ev_merges])))
