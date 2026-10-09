"""Census check: for D-stratum evaluable both-sides cases (M-merge and M-PR),
report fence-level facts only. Reads the three input blobs (base, leg1, leg2)
of each case; never merges, never reads a merge result.

usage: python3 -I fence_cases.py <bare-repo> <owner/name> <worktree-at-pin> [prs]

Prints per case: kind id path gen_marker_at_pin mermaid_fences(B,O,T)
flow_fences(B,O,T) one_fence_all flow_fence_changed(O,T)  -- no content.
"""
import hashlib
import os
import re
import subprocess
import sys

repo, name, wt = sys.argv[1], sys.argv[2], sys.argv[3]
do_prs = len(sys.argv) > 4
KW = re.compile(r"^\s*(flowchart|graph)\b", re.I)
FENCE = re.compile(r"^\s*(```|~~~)\s*mermaid\s*$", re.I)
CLOSE = re.compile(r"^\s*(```|~~~)\s*$")
GENMARK = re.compile(r"auto-?generated|do not edit", re.I)


def git(*a, check=True):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"git {a[0]} failed: {r.stderr.decode(errors='replace')}")
    return r


def fences(blob):
    t = git("cat-file", "blob", blob).stdout.decode("utf-8", "replace").splitlines()
    out = []
    k = 0
    while k < len(t):
        if FENCE.match(t[k]):
            j = k + 1
            while j < len(t) and not CLOSE.match(t[j]):
                j += 1
            body = t[k + 1:j]
            first = next((s.strip() for s in body if s.strip() and not s.strip().startswith("%%")), "")
            out.append((bool(KW.match(first)), hashlib.sha256("\n".join(body).encode()).hexdigest()))
            k = j + 1
        else:
            k += 1
    return out


ls = subprocess.run(["git", "-C", wt, "-c", "core.quotepath=off", "ls-files", "-z"], capture_output=True).stdout.decode("utf-8", "surrogateescape").split("\0")
flow = set()
for p in ls:
    if not p.lower().endswith(".md"):
        continue
    L = open(os.path.join(wt, p), encoding="utf-8", errors="replace").read().splitlines()
    if any(FENCE.match(l) and next((s.strip() for s in L[k + 1:] if s.strip() and not s.strip().startswith("%%")), "") and KW.match(next(s.strip() for s in L[k + 1:] if s.strip() and not s.strip().startswith("%%"))) for k, l in enumerate(L)):
        flow.add(p)


def genmark(p):
    try:
        with open(os.path.join(wt, p), encoding="utf-8", errors="replace") as f:
            return any(GENMARK.search(next(f, "")) for _ in range(10))
    except OSError:
        return None


def changed(b, x):
    d = {}
    t = git("diff-tree", "--no-renames", "-r", "-z", b, x, "--", "*.md").stdout.decode("utf-8", "surrogateescape").split("\0")
    k = 0
    while k + 1 < len(t):
        mm = t[k].split()
        if len(mm) >= 5 and t[k + 1] in flow:
            d[t[k + 1]] = (mm[4], mm[3], mm[2])
        k += 2
    return d


def report(kind, ident, b, l1, l2):
    c1, c2 = changed(b, l1), changed(b, l2)
    for p in sorted(set(c1) & set(c2)):
        (s1, b1, _), (s2, b2, _) = c1[p], c2[p]
        if s1 == "A" and s2 == "A" or "D" in (s1, s2) or b1 == b2:
            continue
        base_blob = git("rev-parse", f"{b}:{p}").stdout.decode().strip()
        F = [fences(x) for x in (base_blob, b1, b2)]
        nm = [len(f) for f in F]
        nf = [sum(1 for fl, _ in f if fl) for f in F]
        one = all(n == 1 for n in nm) and all(n == 1 for n in nf)
        chg = "-"
        if one:
            chg = f"{F[1][0][1] != F[0][0][1]},{F[2][0][1] != F[0][0][1]}"
        print("\t".join(map(str, [name, kind, ident[:12], p, genmark(p), nm, nf, one, chg])), flush=True)


if not do_prs:
    for line in git("rev-list", "--merges", "--parents", "HEAD").stdout.decode().split("\n"):
        f = line.split()
        if len(f) != 3:
            continue
        bases = git("merge-base", "--all", f[1], f[2], check=False).stdout.decode().split()
        if len(bases) != 1:
            continue
        report("merge", f[0], bases[0], f[1], f[2])
else:
    toks = git("log", "--no-merges", "--no-renames", "--format=@%H", "--raw", "--no-abbrev", "-z", "HEAD", "--", "*.md").stdout.decode("utf-8", "surrogateescape").split("\0")
    commits, cur, i = [], None, 0
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
        if st[0] in "AM" and p in flow:
            commits.append(cur)
    for c in dict.fromkeys(commits):
        r = subprocess.run(["gh", "api", f"repos/{name}/commits/{c}/pulls", "--jq",
                            '.[] | select(.merged_at != null) | [.number, .head.sha, .merge_commit_sha] | @tsv'],
                           capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            n, h, m = ln.split("\t")
            if m != c or git("cat-file", "-e", h, check=False).returncode != 0:
                continue
            par = git("rev-parse", f"{c}^").stdout.decode().strip()
            bases = git("merge-base", "--all", h, par, check=False).stdout.decode().split()
            if len(bases) != 1:
                continue
            # record the pull request commit count with the case
            pr_commits = subprocess.run(["gh", "api", f"repos/{name}/pulls/{n}", "--jq", ".commits"], capture_output=True, text=True).stdout.strip()
            report(f"pr#{n}(commits={pr_commits})", c, bases[0], par, h)
