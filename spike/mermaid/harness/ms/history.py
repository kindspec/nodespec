# SPDX-License-Identifier: MIT
"""A corpus's history, read for §7.4 (selection), §7.5 (authors), §8.2 (arm M)
and §8.3 (arm P). Reads trees, commits and blobs; never runs a merge.

Paths are read NUL-separated with core.quotepath=off (§7.4).
"""
import hashlib
import re
import subprocess

from . import fence as FN
from . import gitops as G

BOT = re.compile(r"bot", re.IGNORECASE)
NOREPLY = re.compile(r"^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$", re.IGNORECASE)


class Repo:
    def __init__(self, path):
        self.path = path
        self.e = G.env("/nonexistent")
        self.e["GIT_CONFIG_PARAMETERS"] = "'core.quotepath=off'"
        self._blob = {}

    def run(self, *a, check=True, inp=None):
        r = subprocess.run(["git", "-C", self.path, "-c", "core.quotepath=off", *a], capture_output=True,
                           env=self.e, input=inp)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {' '.join(a[:3])}: {r.stderr.decode('utf-8', 'replace').strip()[:300]}")
        return r

    def out(self, *a, check=True):
        return self.run(*a, check=check).stdout.decode("utf-8", "surrogateescape")

    def has_commit(self, sha):
        return self.run("cat-file", "-e", sha + "^{commit}", check=False).returncode == 0

    def blob(self, sha):
        if sha not in self._blob:
            self._blob[sha] = self.run("cat-file", "blob", sha).stdout
        return self._blob[sha]

    def blob_at(self, commit, path):
        """The blob sha of path at commit, or None."""
        r = self.run("ls-tree", "-z", "--full-tree", commit, "--", path, check=False)
        for ent in r.stdout.decode("utf-8", "surrogateescape").split("\0"):
            if not ent:
                continue
            meta, p = ent.split("\t", 1)
            if p == path and meta.split()[1] == "blob":
                return meta.split()[2]
        return None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b, check=False).returncode == 0

    def merge_bases(self, a, b):
        return self.out("merge-base", "--all", a, b, check=False).split()

    def parents(self, c):
        return self.out("rev-list", "--parents", "-n", "1", c).split()[1:]

    def patch_id(self, a, b):
        d = self.run("diff", "--no-renames", "--no-ext-diff", a, b).stdout
        p = subprocess.run(["git", "patch-id", "--stable"], input=d, capture_output=True, env=self.e)
        return p.stdout.decode().split()[0] if p.stdout.strip() else ""


def text_of(repo, sha):
    """A blob as UTF-8 text, or None (R-undecodable: such a case is excluded
    and counted)."""
    try:
        return repo.blob(sha).decode("utf-8")
    except UnicodeDecodeError:
        return None


# --------------------------------------------------------------- the log walk

def walk(repo, pin):
    """Every non-merge commit reachable from pin, topo-order reversed, with
    its add/modify/delete entries for .mmd/.mermaid/.md paths and its author.
    Returns (commits, by_path) where by_path[path] is [(commit, status, blob)]
    in that order."""
    raw = repo.out("log", pin, "--topo-order", "--reverse", "--no-renames", "--no-merges", "--raw", "-z",
                   "--no-abbrev", "--format=@%H%x09%an%x09%ae")
    toks = raw.split("\0")
    commits, by_path, touched = [], {}, {}
    cur, i = None, 0
    while i < len(toks):
        t = toks[i].lstrip("\n")
        if t.startswith("@"):
            h, an, ae = t[1:].split("\t")
            cur = {"sha": h, "name": an, "email": ae}
            commits.append(cur)
            i += 1
            continue
        if not t:
            i += 1
            continue
        meta = t.split()
        st, p = meta[4], toks[i + 1]
        i += 2
        if st[0] in "AM":
            touched.setdefault(p, set()).add(cur["sha"])
        if FN.stratum_of(p) is None:
            continue
        by_path.setdefault(p, []).append((cur["sha"], st[0], meta[3]))
    return commits, by_path, touched


def segments(entries):
    """Versions per segment: a delete ends a list, a re-add starts a new one.
    Consecutive identical blobs are merged (§8.3)."""
    segs, cur = [], []
    for c, st, blob in entries:
        if st == "D":
            if cur:
                segs.append(cur)
            cur = []
            continue
        if cur and cur[-1][1] == blob:
            continue
        cur.append((c, blob))
    if cur:
        segs.append(cur)
    return segs


# ------------------------------------------------------------------ selection

def select(repo, pin, walked=None):
    """§7.4 over every .mmd/.mermaid/.md path in history. Returns
    {"selected": {path: stratum}, "excluded": {path: reason}}.
    R-select: a path's stratum test (a flowchart for F; exactly one Mermaid
    fence, a flowchart, for D) and the declaration rule read its last
    version's blob, as the census did for F."""
    commits, by_path, touched = walked or walk(repo, pin)
    sel, exc = {}, {}
    for p, ents in sorted(by_path.items()):
        st = FN.stratum_of(p)
        am = [e for e in ents if e[1] in "AM"]
        if not am:
            continue
        last_c, _, last_b = am[-1]
        if FN.generated_by_path(p):
            exc[p] = "generated: path segment"
            continue
        txt = text_of(repo, last_b)
        if txt is None:
            exc[p] = "last version is not UTF-8"
            continue
        if FN.generated_by_declaration(txt):
            exc[p] = "generated: declaration"
            continue
        d, why = FN.diagram_of(st, txt)
        if d is None:
            exc[p] = f"stratum test: {why}"
            continue
        if st == "F" and sibling_derived(repo, p, last_c, {c for c, s, _ in ents if s in "AM"}, touched):
            exc[p] = "generated: co-changing .dot/.json sibling"
            continue
        sel[p] = st
    return {"selected": sel, "excluded": exc}


def sibling_derived(repo, path, last_commit, mine, touched):
    """§7.4: a same-stem .dot or .json beside it, in the tree of its last
    version, added or modified in at least half of the commits that added or
    modified it."""
    d, _, f = path.rpartition("/")
    stem = f.rsplit(".", 1)[0]
    names = repo.out("ls-tree", "-z", "--name-only", f"{last_commit}:{d}" if d else last_commit,
                     check=False).split("\0")
    sibs = [(d + "/" + n) if d else n for n in names if n in (stem + ".dot", stem + ".json")]
    if not sibs:
        return False
    co = {c for c in mine if any(c in touched.get(s, ()) for s in sibs)}
    return 2 * len(co) >= len(mine)


# -------------------------------------------------------------------- authors

def identity_keys(name, email):
    """§7.5: a case-folded email (a noreply address read as its login) and a
    case-folded name."""
    e = (email or "").casefold()
    m = NOREPLY.match(e)
    if m:
        e = m.group(1)
    return {"e:" + e, "n:" + (name or "").casefold()}


class Authors:
    """Union-find over commit identities sharing a key."""

    def __init__(self):
        self.parent = {}

    def _find(self, x):
        while self.parent.setdefault(x, x) != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def add(self, name, email):
        ks = sorted(identity_keys(name, email))
        for k in ks[1:]:
            a, b = self._find(ks[0]), self._find(k)
            if a != b:
                self.parent[max(a, b)] = min(a, b)

    def of(self, name, email):
        self.add(name, email)
        return self._find(sorted(identity_keys(name, email))[0])


def is_bot(name, email):
    return bool(BOT.search((name or "").casefold()) or BOT.search((email or "").casefold()))


# ---------------------------------------------------------------- arm M-merge

def classify_pair(base_b, x_b, y_b):
    """For one path: (status) of a both-sides candidate."""
    if base_b is None and x_b is not None and y_b is not None:
        return "add/add"
    if x_b is None or y_b is None:
        return "delete/modify" if base_b is not None else "absent"
    if x_b == base_b or y_b == base_b:
        return "one side"
    if x_b == y_b:
        return "convergent"
    return "evaluable"


def merge_cases(repo, pin, selected):
    """§8.2 M-merge: every two-parent merge reachable from the pin. Returns
    (cases, counts). A case: {"merge", "o", "t", "base", "path"}."""
    counts = {"merges_2p": 0, "multi-base": 0, "add/add": 0, "delete/modify": 0, "convergent": 0,
              "evaluable": 0}
    cases = []
    lines = repo.out("rev-list", "--merges", "--parents", "--topo-order", "--reverse", pin).splitlines()
    for ln in lines:
        parts = ln.split()
        if len(parts) != 3:
            continue
        c, p1, p2 = parts
        counts["merges_2p"] += 1
        changed = _changed_paths(repo, p1, p2, selected)
        if not changed:
            continue
        bases = repo.merge_bases(p1, p2)
        for path in changed:
            if len(bases) != 1:
                counts["multi-base"] += 1
                continue
            st = classify_pair(*(repo.blob_at(x, path) for x in (bases[0], p1, p2)))
            if st in counts:
                counts[st] += 1
            if st == "evaluable":
                cases.append({"arm": "M-merge", "merge": c, "o": p1, "t": p2, "base": bases[0], "path": path})
    return cases, counts


def _changed_paths(repo, a, b, selected):
    """Selected paths changed on both sides from the one merge base; with
    several bases, the selected paths that differ between a and b (each is
    counted multi-base and dropped)."""
    bases = repo.merge_bases(a, b)

    def diff(x, y):
        return set(repo.out("diff-tree", "-r", "-z", "--no-renames", "--name-only", x, y,
                            check=False).split("\0"))
    if len(bases) == 1:
        return sorted(p for p in diff(bases[0], a) & diff(bases[0], b) if p in selected)
    return sorted(p for p in diff(a, b) if p in selected)


# ------------------------------------------------------------------ arm M-PR

def pr_cases(repo, pin, selected, prs):
    """§8.2 M-PR. prs: the archived list, each {"number", "head", "merge",
    "commits": [sha, oldest first]}. Returns (cases, counts)."""
    counts = {"prs": 0, "not reachable or not one parent": 0, "over 250 commits": 0, "rebase": 0,
              "squash": 0, "neither rule": 0, "head missing": 0, "multi-base": 0, "add/add": 0,
              "delete/modify": 0, "convergent": 0, "evaluable": 0}
    cases = []
    for pr in sorted(prs, key=lambda x: x["number"]):
        counts["prs"] += 1
        c, head, k = pr.get("merge"), pr.get("head"), len(pr.get("commits") or [])
        if not c or not repo.has_commit(c) or not repo.is_ancestor(c, pin) or len(repo.parents(c)) != 1:
            counts["not reachable or not one parent"] += 1
            continue
        if not head or not repo.has_commit(head):
            counts["head missing"] += 1
            continue
        if pr.get("commit_count", k) > 250 or k > 250:
            counts["over 250 commits"] += 1
            continue
        target = None
        chain, cur = [], c
        for _ in range(k):
            ps = repo.parents(cur)
            if len(ps) != 1:
                chain = None
                break
            chain.append(cur)
            cur = ps[0]
        if chain is not None and k > 0:
            mine = [repo.patch_id(repo.parents(x)[0], x) for x in reversed(chain)]
            theirs = [repo.patch_id(repo.parents(x)[0], x) if repo.has_commit(x) and len(repo.parents(x)) == 1
                      else None for x in pr["commits"]]
            if mine == theirs and None not in theirs:
                target = cur
                counts["rebase"] += 1
        if target is None:
            p = repo.parents(c)[0]
            mb = repo.merge_bases(head, p)
            if len(mb) == 1 and repo.patch_id(p, c) == repo.patch_id(mb[0], head):
                target = p
                counts["squash"] += 1
        if target is None:
            counts["neither rule"] += 1
            continue
        bases = repo.merge_bases(head, target)
        for path in _changed_paths(repo, target, head, selected):
            if len(bases) != 1:
                counts["multi-base"] += 1
                continue
            st = classify_pair(*(repo.blob_at(x, path) for x in (bases[0], target, head)))
            if st in counts:
                counts[st] += 1
            if st == "evaluable":
                cases.append({"arm": "M-PR", "pr": pr["number"], "merge": c, "o": target, "t": head,
                              "base": bases[0], "path": path})
    return cases, counts


# --------------------------------------------------------------------- arm P

def p_triples(repo, selected, by_path):
    """§8.3. Returns (triples, counts). A triple: {"path", "i", "a", "b",
    "versions": [(commit, blob)] from V[i] to V[i+a+b], "seg"}."""
    counts = {"pairs": 0, "predecessor ok": 0, "dropped: predecessor rule": 0, "candidates": 0}
    out = []
    for path in sorted(selected):
        for si, seg in enumerate(segments(by_path.get(path, []))):
            ok = []
            for j in range(len(seg) - 1):
                counts["pairs"] += 1
                (c0, b0), (c1, b1) = seg[j], seg[j + 1]
                fp = repo.parents(c1)
                good = repo.is_ancestor(c0, c1) and bool(fp) and repo.blob_at(fp[0], path) == b0
                ok.append(good)
                counts["predecessor ok"] += good
            for i in range(len(seg)):
                for a, b in ((1, 1), (1, 3), (3, 1)):
                    if i + a + b >= len(seg):
                        continue
                    counts["candidates"] += 1
                    if not all(ok[i:i + a + b]):
                        counts["dropped: predecessor rule"] += 1
                        continue
                    out.append({"path": path, "seg": si, "i": i, "a": a, "b": b,
                                "versions": seg[i:i + a + b + 1]})
    return out, counts


def blob_hash(text):
    return hashlib.sha1(b"blob %d\0" % len(text.encode()) + text.encode()).hexdigest()
