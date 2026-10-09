"""Count squash- or rebase-merged pull requests that changed a flowchart path on both legs.

usage: python3 -I mpr_counts.py <bare-blobless-repo> <owner/name> <paths-file>

<paths-file> holds the selected flowchart paths, NUL-separated (written by
flow_paths.py). For each non-merge commit on HEAD that adds or modifies one of
them, the GitHub API names the merged pull request whose merge_commit_sha is
that commit. Its head is fetched (commits and trees only, the clone is
blobless). Base = merge-base(head, commit^). Legs = commit^ (the target branch
when the pull request landed) and the head. A path counts if it changed from
base on both legs. Tree metadata only: no blob is read, nothing is merged.

Prints: repo commits_examined prs_squash_or_rebase prs_head_fetched multibase
both_sides_paths addadd delmod convergent evaluable evaluable_prs
"""
import subprocess
import sys

repo, name, pf = sys.argv[1], sys.argv[2], sys.argv[3]
paths = set(p for p in open(pf, "rb").read().decode("utf-8", "surrogateescape").split("\0") if p)


def git(*a, check=True):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"git {a[0]} failed: {r.stderr.decode(errors='replace')}")
    return r


toks = git("log", "--no-merges", "--no-renames", "--format=@%H", "--raw", "--no-abbrev", "-z", "HEAD").stdout.decode("utf-8", "surrogateescape").split("\0")
commits = []
cur = None
i = 0
while i < len(toks):
    t = toks[i].lstrip("\n")
    if t.startswith("@"):
        cur = t[1:]
        i += 1
        continue
    if not t:
        i += 1
        continue
    st, p = t.split()[4], toks[i + 1]
    i += 2
    if st[0] in "CR":
        i += 1
        continue
    if st[0] in "AM" and p in paths and (not commits or commits[-1] != cur):
        commits.append(cur)
commits = list(dict.fromkeys(commits))

prs = {}
for c in commits:
    r = subprocess.run(["gh", "api", f"repos/{name}/commits/{c}/pulls",
                        "--jq", '.[] | select(.merged_at != null) | [.number, .head.sha, .merge_commit_sha] | @tsv'],
                       capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        n, h, m = ln.split("\t")
        if m == c:
            prs[n] = (h, c)

fetched = multi = bs = aa = dm = cv = ev = evp = 0
for n, (h, c) in prs.items():
    if git("cat-file", "-e", h, check=False).returncode != 0:
        git("fetch", "-q", "origin", f"pull/{n}/head", check=False)
    if git("cat-file", "-e", h, check=False).returncode != 0:
        continue
    fetched += 1
    par = git("rev-parse", f"{c}^").stdout.decode().strip()
    bases = git("merge-base", "--all", h, par, check=False).stdout.decode().split()
    if len(bases) != 1:
        multi += len(bases) > 1
        continue
    b = bases[0]

    def changed(x):
        d = {}
        t = git("diff-tree", "--no-renames", "-r", "-z", b, x).stdout.decode("utf-8", "surrogateescape").split("\0")
        k = 0
        while k + 1 < len(t):
            mm = t[k].split()
            if len(mm) >= 5 and t[k + 1] in paths:
                d[t[k + 1]] = (mm[4], mm[3])
            k += 2
        return d
    c1, c2 = changed(par), changed(h)
    hit = False
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
            hit = True
    evp += hit
print("\t".join(map(str, [name, len(commits), len(prs), fetched, multi, bs, aa, dm, cv, ev, evp])))
