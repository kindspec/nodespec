"""Count never-merged concurrent legs that changed a flowchart path on both sides.

usage: python3 -I unmerged_counts.py prs   <bare-repo> <owner/name> <paths-file>
       python3 -I unmerged_counts.py forks <bare-repo> <owner/name> <paths-file> [max_forks]

Tree metadata only: no blob is read, nothing is merged. <paths-file> holds the
selected flowchart paths, NUL-separated (from flow_paths.py).

prs: fetch every refs/pull/*/head (commits and trees; the clone is blobless).
  A pull request is a candidate if its head changed a selected path since
  merge-base(head, HEAD). For each candidate, the API gives state, merged_at,
  closed_at and base ref. Closed-unmerged ones against the default branch are
  kept. Base leg = the last first-parent commit of HEAD before closed_at.
  Both-sides = the path changed from merge-base(head, base leg) on both legs.
  Prints: repo pr_refs candidates closed_unmerged open other_base
          both_sides addadd delmod convergent evaluable evaluable_prs
forks: the first max_forks (default 100) forks by stargazers. Each fork's
  default branch is fetched. Fork point = merge-base(fork, HEAD). A fork counts
  if it has commits of its own, and is evaluable if a selected path changed
  since the fork point on both the fork and upstream HEAD.
  Prints: repo forks_listed fetched with_own_commits own_touch_flow
          both_sides addadd delmod convergent evaluable evaluable_forks
"""
import json
import subprocess
import sys

mode, repo, name, pf = sys.argv[1:5]
maxf = int(sys.argv[5]) if len(sys.argv) > 5 else 100
paths = set(p for p in open(pf, "rb").read().decode("utf-8", "surrogateescape").split("\0") if p)


def git(*a, check=False):
    return subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True)


def out(*a):
    return git(*a).stdout.decode().strip()


def changed(b, x):
    d = {}
    t = git("diff-tree", "--no-renames", "-r", "-z", b, x).stdout.decode("utf-8", "surrogateescape").split("\0")
    k = 0
    while k + 1 < len(t):
        mm = t[k].split()
        if len(mm) >= 5 and t[k + 1] in paths:
            d[t[k + 1]] = (mm[4], mm[3])
        k += 2
    return d


def classify(b, l1, l2, acc):
    c1, c2 = changed(b, l1), changed(b, l2)
    hit = False
    for p in set(c1) & set(c2):
        acc["bs"] += 1
        (s1, b1), (s2, b2) = c1[p], c2[p]
        if s1 == "A" and s2 == "A":
            acc["aa"] += 1
        elif "D" in (s1, s2):
            acc["dm"] += 1
        elif b1 == b2:
            acc["cv"] += 1
        else:
            acc["ev"] += 1
            hit = True
    acc["evn"] += hit


acc = dict(bs=0, aa=0, dm=0, cv=0, ev=0, evn=0)
head = out("rev-parse", "HEAD")
if not paths:
    print("\t".join(map(str, [name, "no-paths"])))
    sys.exit(0)
if mode == "prs":
    git("fetch", "-q", "--filter=blob:none", "origin", "+refs/pull/*/head:refs/pr/*")
    refs = out("for-each-ref", "--format=%(refname:strip=2) %(objectname)", "refs/pr/").splitlines()
    # commits on pull-request heads, not on HEAD, that touch a selected path
    touch = []  # unused in fast variant
    _unused = git("--literal-pathspecs", "rev-list", "--glob=refs/pr/*", "--not", head, "--", *sorted(paths)).stdout.decode().split()
    # fast variant: map each touching commit to the one pull-request ref git log --source reports.
    # A commit shared by several pull requests is attributed to one of them only.
    tip = dict(ln.split()[::-1] for ln in refs)  # sha -> number (unused) ; refs are "number sha"
    near = set()
    src = git("--literal-pathspecs", "log", "--source", "--format=%H %S", "--glob=refs/pr/*", "--not", head, "--", *sorted(paths)).stdout.decode().split("\n")
    byref = {ln.split()[0]: ln.split()[1] for ln in refs}
    for ln in src:
        if not ln.strip():
            continue
        c, r = ln.split()
        n = r.split("/")[-1]
        if n in byref:
            near.add((n, byref[n]))
    cands = []
    for n, h in sorted(near):
        mb = out("merge-base", h, head)
        if mb and mb != h and changed(mb, h):
            cands.append((n, h))
    cu = op = ob = 0
    apierr = 0
    for n, h in cands:
        j = None
        for attempt in range(5):
            r = subprocess.run(["gh", "api", f"repos/{name}/pulls/{n}", "--jq",
                                "{state, merged_at, closed_at, base: .base.ref, default: .base.repo.default_branch}"],
                               capture_output=True, text=True)
            try:
                j = json.loads(r.stdout)
            except ValueError:
                j = None
            if j and "state" in j:
                break
            j = None
            import time
            time.sleep(60)
        if j is None:
            apierr += 1  # counted, never silently dropped
            continue
        if j["merged_at"]:
            continue
        if j["state"] == "open":
            op += 1
            continue
        if j["base"] != j["default"]:
            ob += 1
            continue
        cu += 1
        bl = out("rev-list", "-1", "--first-parent", f"--before={j['closed_at']}", "HEAD")
        mb = out("merge-base", "--all", h, bl).split()
        if len(mb) == 1:
            classify(mb[0], bl, h, acc)
    print("\t".join(map(str, [name, len(refs), len(cands), cu, op, ob,
                              acc["bs"], acc["aa"], acc["dm"], acc["cv"], acc["ev"], acc["evn"], f"apierr={apierr}"])))
else:
    r = subprocess.run(["gh", "api", f"repos/{name}/forks?sort=stargazers&per_page={min(maxf, 100)}",
                        "--jq", ".[].full_name"], capture_output=True, text=True)
    forks = r.stdout.split()[:maxf]
    fetched = own = touch = 0
    for i, f in enumerate(forks):
        if git("fetch", "-q", "--filter=blob:none", f"https://github.com/{f}.git", f"+HEAD:refs/forks/{i}").returncode != 0:
            continue
        fetched += 1
        fh = out("rev-parse", f"refs/forks/{i}")
        fp = out("merge-base", fh, head)
        if not fp or fp == fh:
            continue
        own += 1
        if changed(fp, fh):
            touch += 1
            classify(fp, head, fh, acc)
    print("\t".join(map(str, [name, len(forks), fetched, own, touch,
                              acc["bs"], acc["aa"], acc["dm"], acc["cv"], acc["ev"], acc["evn"]])))
