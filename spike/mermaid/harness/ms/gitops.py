# SPDX-License-Identifier: MIT
"""Git, as F2 requires: `git merge` in a fresh repository with
GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null, an empty HOME and
XDG_CONFIG_HOME, and no .gitattributes. git's version goes in every
transcript (version()).

Reading R-merge-order: O is checked out and T is merged into it. For M-merge,
O is the merge's first parent and T its second; for M-PR, O is the target leg
and T the pull request's head; for P and S, O is leg O.
"""
import os
import re
import shutil
import subprocess
import tempfile

NEUTRAL_ATTRIBUTES = "* !merge !text !eol !crlf !filter !ident !working-tree-encoding !conflict-marker-size !diff\n"


def env(home):
    """F2's environment: nothing from the caller's git configuration."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "HOME": home,
              "XDG_CONFIG_HOME": home, "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C",
              "GIT_AUTHOR_NAME": "spike", "GIT_AUTHOR_EMAIL": "spike@invalid",
              "GIT_COMMITTER_NAME": "spike", "GIT_COMMITTER_EMAIL": "spike@invalid",
              "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"})
    return e


def version():
    return subprocess.run(["git", "--version"], capture_output=True, text=True, env=env(os.devnull)).stdout.strip()


def git(repo, *a, e, check=True, inp=None):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, env=e, input=inp)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return r


class Merge:
    """The result for one path: merged bytes (None if the path is absent),
    whether `git ls-files -u -- <path>` is non-empty, and git's exit."""
    __slots__ = ("merged", "unmerged", "rc", "argv")

    def __init__(self, merged, unmerged, rc, argv):
        self.merged, self.unmerged, self.rc, self.argv = merged, unmerged, rc, argv


def _fresh(tmp_root):
    d = tempfile.mkdtemp(prefix="merge.", dir=tmp_root)
    home = os.path.join(d, "home")
    os.mkdir(home)
    repo = os.path.join(d, "repo")
    os.mkdir(repo)
    return d, home, repo


def merge_texts(path, base, o, t, tmp_root=None):
    """A three-way case given as bytes (arms P and S, plants): base, then O
    and T as two commits on it, each holding only `path`."""
    d, home, repo = _fresh(tmp_root)
    e = env(home)
    try:
        git(repo, "init", "-q", "-b", "base", e=e)
        full = os.path.join(repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)

        def commit(data, msg):
            with open(full, "wb") as f:
                f.write(data)
            git(repo, "add", "--", path, e=e)
            git(repo, "commit", "-q", "--allow-empty", "-m", msg, e=e)
        commit(base, "base")
        git(repo, "checkout", "-q", "-b", "o", "base", e=e)
        commit(o, "o")
        git(repo, "checkout", "-q", "-b", "t", "base", e=e)
        commit(t, "t")
        git(repo, "checkout", "-q", "o", e=e)
        argv = ["git", "merge", "--no-edit", "t"]
        r = git(repo, *argv[1:], e=e, check=False)
        return _result(repo, path, e, r.returncode, argv)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def merge_commits(corpus, ours, theirs, paths, tmp_root=None):
    """Arm M: re-merge two real commits under F2. The fresh repository
    borrows the corpus's objects (objects/info/alternates) and none of its
    configuration. Returns {path: Merge}."""
    d, home, repo = _fresh(tmp_root)
    e = env(home)
    try:
        git(repo, "init", "-q", e=e)
        objs = git(corpus, "rev-parse", "--path-format=absolute", "--git-common-dir", e=e).stdout.decode().strip()
        with open(os.path.join(repo, ".git", "objects", "info", "alternates"), "w") as f:
            f.write(os.path.join(objs, "objects") + "\n")
        # F2: no .gitattributes. R-attributes: a corpus may commit one (a
        # built-in `merge=union` needs no configuration), so every attribute
        # that can change a merge is unset for every path in
        # $GIT_DIR/info/attributes, which outranks the tree's files. The
        # commits being merged are not changed.
        with open(os.path.join(repo, ".git", "info", "attributes"), "w") as f:
            f.write(NEUTRAL_ATTRIBUTES)
        git(repo, "checkout", "-q", "--detach", ours, e=e)
        argv = ["git", "merge", "--no-edit", "--no-ff", theirs]
        r = git(repo, *argv[1:], e=e, check=False)
        return {p: _result(repo, p, e, r.returncode, argv) for p in paths}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _result(repo, path, e, rc, argv):
    full = os.path.join(repo, path)
    data = None
    if os.path.isfile(full) and not os.path.islink(full):
        with open(full, "rb") as f:
            data = f.read()
    u = git(repo, "ls-files", "-u", "--", path, e=e, check=False).stdout.strip()
    return Merge(data, bool(u), rc, argv)


def has_new_marker(merged, inputs):
    """§5.3's "holds a conflict marker". R-marker: a line opening with seven
    '<', '>' or '|' that no input already holds; git never writes '======='
    alone, and Markdown's setext headings use it."""
    seen = set()
    for x in inputs:
        seen |= {m.group(0) for m in re.finditer(r"^(?:<{7}|>{7}|\|{7}).*$", x, re.MULTILINE)}
    return any(m.group(0) not in seen for m in re.finditer(r"^(?:<{7}|>{7}|\|{7}).*$", merged, re.MULTILINE))
