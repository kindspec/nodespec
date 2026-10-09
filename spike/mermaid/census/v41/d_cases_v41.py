"""Stratum-D (and F) pull-request cases under the v3 rules, with the one-fence filter.

usage: python3 -I d_cases_v3.py mpr      <bare> <owner/name> <paths-file> <stratum>
       python3 -I d_cases_v3.py unmerged <bare> <owner/name> <paths-file> <stratum> [fast]

mpr: every merged pull request whose merge commit c is on HEAD's history with one
  parent and touches a selected path. Target leg (draft v3 §8.2):
    - rebase if k = API commit count, c~0..c~(k-1) are non-merge commits, and
      their patch-ids, oldest first, equal the pull request's commits' patch-ids
      in order; target = c~k;
    - else squash if patch-id(diff c^ c) == patch-id(diff merge-base(head, c^) head);
      target = c^;
    - else excluded and counted.
unmerged: closed-unmerged pull requests against the default branch (as
  v2/unmerged_counts.py); base leg = last first-parent commit of HEAD before closed_at.

For every evaluable both-sides path, the three input blobs are read and only fence
facts are printed: Mermaid fence counts and flowchart-fence counts per input,
whether every input holds exactly one fence that is a flowchart, and whether each
leg's fence body differs from the base's. Diffs are read to compute patch-ids;
only match booleans are kept. Nothing is merged; no merge result is read.
Read-only corpora: pass --redact to print a hash in place of the path.
"""
import hashlib
import json
import re
import subprocess
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
redact = "--redact" in sys.argv
mode, repo, name, pf, stratum = args[:5]
fast = len(args) > 5 and args[5] == "fast"
paths = set(p for p in open(pf, "rb").read().decode("utf-8", "surrogateescape").split("\0") if p)
OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b", re.I)
KW = re.compile(r"^(flowchart|flowchart-elk|graph)(\s|$)", re.I)


def git(*a, inp=None):
    return subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True, input=inp)


def out(*a):
    return git(*a).stdout.decode().strip()


def api(path, jq, paginate=False):
    for _ in range(5):
        r = subprocess.run(["gh", "api", *(["--paginate"] if paginate else []), path, "--jq", jq], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
        import time
        time.sleep(30)
    return None


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


def fences(spec):
    r = git("cat-file", "blob", spec)
    if r.returncode != 0:
        return None
    t = r.stdout.decode("utf-8", "replace").splitlines()
    res, k = [], 0
    while k < len(t):
        m = OPEN.match(t[k])
        if m:
            ch, n = m.group(1)[0], len(m.group(1))
            j = k + 1
            while j < len(t) and not re.match(r"^ {0,3}" + re.escape(ch) + "{" + str(n) + r",}\s*$", t[j]):
                j += 1
            body = t[k + 1:j]
            res.append((first_kw(body), hashlib.sha256("\n".join(body).encode()).hexdigest()))
            k = j + 1
        else:
            k += 1
    return res


def fence_facts(b, l1, l2, p):
    F = [fences(f"{x}:{p}") for x in (b, l1, l2)]
    if any(f is None for f in F):
        return "unreadable"
    if stratum == "mmd":
        return "file"
    nm = [len(f) for f in F]
    nf = [sum(1 for fl, _ in f if fl) for f in F]
    one = all(n == 1 for n in nm) and all(n == 1 for n in nf)
    chg = f"{F[1][0][1] != F[0][0][1]},{F[2][0][1] != F[0][0][1]}" if one else "-"
    return f"fences={nm} flow={nf} one={one} changed={chg}"


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


def cases(kind, ident, b, l1, l2, tally):
    c1, c2 = changed(b, l1), changed(b, l2)
    for p in sorted(set(c1) & set(c2)):
        (s1, b1), (s2, b2) = c1[p], c2[p]
        if s1 == "A" and s2 == "A":
            tally["addadd"] += 1
        elif "D" in (s1, s2):
            tally["delmod"] += 1
        elif b1 == b2:
            tally["conv"] += 1
        else:
            tally["evaluable"] += 1
            facts = fence_facts(b, l1, l2, p)
            if "one=True" in facts:
                tally["one_fence"] += 1
                if "changed=True,True" in facts:
                    tally["one_fence_both_changed"] += 1
            if stratum == "mmd":
                tally["one_fence_both_changed"] += 1  # F: both legs change the file by construction
            label = "h:" + hashlib.sha256(p.encode()).hexdigest()[:16] if redact else p
            print("\t".join(["CASE", name, kind, ident, label, facts]), flush=True)


def patch_id(*rev):
    d = git(*rev).stdout
    r = git("patch-id", "--stable", inp=d).stdout.decode().split()
    return r[0] if r else None


tally = {k: 0 for k in ("prs", "rebase", "squash", "excluded", "nohead", "multibase", "addadd", "delmod",
                        "conv", "evaluable", "one_fence", "one_fence_both_changed", "closed_unmerged", "apierr", "over250")}
head = out("rev-parse", "HEAD")
if mode == "mpr":
    toks = git("log", "--no-merges", "--no-renames", "--format=@%H", "--raw", "--no-abbrev", "-z", "HEAD").stdout.decode("utf-8", "surrogateescape").split("\0")
    commits, cur, i = [], None, 0
    while i < len(toks):
        t = toks[i].lstrip("\n")
        if t.startswith("@"):
            cur = t[1:]; i += 1; continue
        if not t:
            i += 1; continue
        st, p = t.split()[4], toks[i + 1]
        i += 2
        if st[0] in "CR":
            i += 1; continue
        if st[0] in "AM" and p in paths:
            commits.append(cur)
    seen = set()
    for c in dict.fromkeys(commits):
        o = api(f"repos/{name}/commits/{c}/pulls", '.[] | select(.merged_at != null) | [.number, .head.sha, .merge_commit_sha, .commits // ""] | @tsv')
        if o is None:
            tally["apierr"] += 1; continue
        for ln in o.splitlines():
            f = ln.split("\t")
            if len(f) < 3:
                continue
            n, h, m = f[0], f[1], f[2]
            if n in seen:
                continue
            # the PR's merge commit may be a later commit than c (rebase): find it
            if git("merge-base", "--is-ancestor", m, head).returncode != 0:
                continue
            if len(out("rev-list", "--parents", "-n1", m).split()) != 2:
                continue  # two-parent merges belong to M-merge
            seen.add(n)
            tally["prs"] += 1
            if git("cat-file", "-e", h).returncode != 0:
                git("fetch", "-q", "--filter=blob:none", "origin", f"pull/{n}/head")
            if git("cat-file", "-e", h).returncode != 0:
                tally["nohead"] += 1; continue
            kc = api(f"repos/{name}/pulls/{n}", ".commits")
            prc = api(f"repos/{name}/pulls/{n}/commits?per_page=100", ".[].sha", paginate=True)
            target = None
            try:
                k = int(kc.strip())
                prc = prc.split()
            except (AttributeError, ValueError):
                k, prc = None, None
            if k and k > 250:
                tally["excluded"] += 1; tally["over250"] += 1; continue  # GitHub lists at most 250 commits
            if k and prc and len(prc) == k:
                chain = [out("rev-parse", f"{m}~{j}") for j in range(k)]
                if all(len(out("rev-list", "--parents", "-n1", x).split()) == 2 for x in chain):
                    if [patch_id("show", "--format=", x) for x in reversed(chain)] == [patch_id("show", "--format=", x) for x in prc]:
                        target = out("rev-parse", f"{m}~{k}")
                        tally["rebase"] += 1
            if target is None:
                par = out("rev-parse", f"{m}^")
                mb = out("merge-base", h, par)
                if mb and patch_id("diff", par, m) == patch_id("diff", mb, h):
                    target = par
                    tally["squash"] += 1
            if target is None:
                tally["excluded"] += 1; continue
            bases = out("merge-base", "--all", h, target).split()
            if len(bases) != 1:
                tally["multibase"] += 1; continue
            cases("pr#" + n, m[:12], bases[0], target, h, tally)
else:
    git("fetch", "-q", "--filter=blob:none", "origin", "+refs/pull/*/head:refs/pr/*")
    refs = out("for-each-ref", "--format=%(refname:strip=2) %(objectname)", "refs/pr/").splitlines()
    byref = {ln.split()[0]: ln.split()[1] for ln in refs}
    near = set()
    if fast:
        src = git("--literal-pathspecs", "log", "--source", "--format=%H %S", "--glob=refs/pr/*", "--not", head, "--", *sorted(paths)).stdout.decode().split("\n")
        for ln in src:
            if ln.strip():
                n = ln.split()[1].split("/")[-1]
                if n in byref:
                    near.add((n, byref[n]))
    else:
        touch = git("--literal-pathspecs", "rev-list", "--glob=refs/pr/*", "--not", head, "--", *sorted(paths)).stdout.decode().split()
        for c in touch:
            for ln in out("for-each-ref", "--contains", c, "--format=%(refname:strip=2) %(objectname)", "refs/pr/").splitlines():
                near.add(tuple(ln.split()))
    for n, h in sorted(near):
        mb = out("merge-base", h, head)
        if not (mb and mb != h and changed(mb, h)):
            continue
        o = api(f"repos/{name}/pulls/{n}", "{state, merged_at, closed_at, base: .base.ref, default: .base.repo.default_branch}")
        try:
            j = json.loads(o)
        except (TypeError, ValueError):
            tally["apierr"] += 1; continue
        if j["merged_at"] or j["state"] == "open" or j["base"] != j["default"]:
            continue
        tally["closed_unmerged"] += 1
        bl = out("rev-list", "-1", "--first-parent", f"--before={j['closed_at']}", "HEAD")
        mb2 = out("merge-base", "--all", h, bl).split()
        if len(mb2) == 1:
            cases("unmerged#" + n, h[:12], mb2[0], bl, h, tally)
print("TALLY\t" + name + "\t" + json.dumps(tally), flush=True)
