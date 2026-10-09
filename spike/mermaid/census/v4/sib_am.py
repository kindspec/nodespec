"""For each bare clone (v4: add/modify commits only), list .mmd/.mermaid paths excluded by the sibling rule,
and how often the path and its sibling change in the same commit. Metadata only."""
import subprocess, sys, os, collections
def git(repo, *a):
    return subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True).stdout.decode("utf-8", "surrogateescape")
for repo in sys.argv[1:]:
    log = git(repo, "log", "--no-merges", "--no-renames", "--format=@%H", "--name-status", "-z", "HEAD")
    commits = collections.defaultdict(set); last = {}
    cur = None
    toks = log.split("\0"); i = 0
    while i < len(toks):
        t = toks[i].lstrip("\n")
        if t.startswith("@"):
            cur = t[1:]; i += 1; continue
        if not t: i += 1; continue
        st = t; p = toks[i+1]; i += 2
        if st[0] in "CR": i += 1; continue
        if st[0] in "AM": commits[p].add(cur)
        if p.lower().endswith((".mmd", ".mermaid")) and st[0] in "AM": last.setdefault(p, cur)  # newest first
    for p, c in last.items():
        d, _, f = p.rpartition("/"); stem = f.rsplit(".", 1)[0]
        names = git(repo, "ls-tree", "-z", "--name-only", f"{c}:{d}" if d else c).split("\0")
        sibs = [n for n in names if n in (stem + ".dot", stem + ".json")]
        if not sibs: continue
        sp = [(d + "/" + s) if d else s for s in sibs]
        mc = commits[p]; both = {x for x in mc if any(x in commits[s] for s in sp)}
        others = sorted(n for n in names if n.startswith(stem + "."))
        print(os.path.basename(repo), p, "siblings=" + ",".join(others), f"mmd_commits={len(mc)} co-changed={len(both)}", sep="\t")
