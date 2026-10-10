# SPDX-License-Identifier: MIT
"""§11.1 and §11.3: "H, X and R at commit 3 are the implementation", and "the
first execution of each arm binds". Checked before every bound run.

THE VALIDATION COMMIT IS DERIVED, never named: it is the one commit in HEAD's
history that adds spike/mermaid/results/VALIDATION (blockspec LOG §18, H2).
VALIDATION holds the sealed fixtures' hash and the lockfile's sha256.

A bound run is refused unless:
- exactly one commit added VALIDATION, and it never changed after;
- the validation commit does not itself change a bound path, and no later
  commit does (bound paths: the harness, R's tracked files, X, the
  V-fixtures, and PRE-REGISTRATION.md);
- the work tree holds the validation commit's bytes at every bound path,
  with no untracked file there (R's node_modules/ is ignored by its own
  .gitignore and checked by rbridge.check_install instead);
- nothing under results/ is uncommitted except this run's transcript;
- this arm has not executed: no marker results/executed/<arm>.json in the
  work tree or in any ref's history.

Threat model (README): this stops honest mistakes -- a stale checkout, an
edit after validation, a re-run of an arm. It does not try to stop an
operator who edits this file or forges history; the review step
(reverify.sh, in a fresh clone) is the check on that.
"""
import json
import os
import re
import subprocess

from . import gitops as G
from .transcript import SPIKE

BOUND = ("harness", "r", "x", "v-fixtures", "PRE-REGISTRATION.md")
VALIDATION_REL = os.path.join("results", "VALIDATION")
EXECUTED_REL = os.path.join("results", "executed")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _git(spike, *a):
    r = subprocess.run(["git", "-C", spike, *a], capture_output=True, text=True, env=G.env(os.devnull))
    return r.returncode, r.stdout, r.stderr


def derive(spike=SPIKE):
    """(validation commit or None, VALIDATION's content or None, reasons)."""
    _, added, _ = _git(spike, "log", "--full-history", "--format=%H", "--diff-filter=A", "--", VALIDATION_REL)
    added = added.split()
    if len(added) != 1:
        return None, None, [f"{len(added)} commits add {VALIDATION_REL}; exactly one must"]
    vc = added[0]
    _, touched, _ = _git(spike, "log", "--full-history", "--format=%H", "--", VALIDATION_REL)
    if touched.split() != [vc]:
        return vc, None, [f"{VALIDATION_REL} changed after the validation commit added it"]
    _, top, _ = _git(spike, "rev-parse", "--show-toplevel")
    rel = os.path.relpath(os.path.join(spike, VALIDATION_REL), top.strip())
    _, raw, _ = _git(spike, "show", f"{vc}:{rel}")
    try:
        v = json.loads(raw)
        assert set(v) == {"sealed_sha256", "lockfile_sha256"}
        assert all(HEX64.match(v[k]) for k in v)
    except (ValueError, AssertionError, TypeError):
        return vc, None, [f"{VALIDATION_REL} must hold exactly sealed_sha256 and lockfile_sha256, 64 hex each"]
    return vc, v, []


def marker_rel(arm):
    return os.path.join(EXECUTED_REL, f"{arm}.json")


def executed(spike, arm):
    rel = marker_rel(arm)
    if os.path.lexists(os.path.join(spike, rel)):
        return True
    _, out, _ = _git(spike, "log", "--all", "--full-history", "--format=%H", "--diff-filter=A", "--", rel)
    return bool(out.strip())


def mark_executed(spike, arm, transcript):
    p = os.path.join(spike, marker_rel(arm))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps({"arm": arm, "transcript": os.path.basename(transcript)}, sort_keys=True) + "\n")


def check(spike=SPIKE, arm=None, own_transcript=None):
    reasons = []
    rc, head, _ = _git(spike, "rev-parse", "HEAD")
    state = {"head": head.strip() or None, "validation_commit": None, "validation": None}
    if rc != 0:
        return dict(state, bound=False, reasons=["not a git work tree"])
    vc, v, rs = derive(spike)
    reasons += rs
    state.update(validation_commit=vc, validation=v)
    if vc and not rs:
        if _git(spike, "rev-parse", "--verify", "-q", f"{vc}^")[0] != 0 or \
                _git(spike, "diff", "--quiet", f"{vc}^", vc, "--", *BOUND)[0] != 0:
            reasons.append(f"the validation commit {vc[:12]} changes a bound path or has no parent")
        _, later, _ = _git(spike, "rev-list", "--full-history", f"{vc}..HEAD", "--", *BOUND)
        if later.strip():
            reasons.append(f"a commit after the validation commit changes a bound path: {later.split()[0][:12]}")
        if _git(spike, "diff", "--quiet", vc, "--", *BOUND)[0] != 0:
            reasons.append("the work tree's bound paths differ from the validation commit")
    _, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all", "--", *BOUND)
    if st.strip():
        reasons.append("uncommitted or untracked files under a bound path: " + "; ".join(st.splitlines()[:3]))
    _, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all", "--", "results")
    _, top, _ = _git(spike, "rev-parse", "--show-toplevel")
    own = os.path.realpath(own_transcript) if own_transcript else None
    for line in st.splitlines():
        if own and os.path.realpath(os.path.join(top.strip(), line[3:])) == own:
            continue
        reasons.append(f"uncommitted under results/: {line}")
    if arm and executed(spike, arm):
        reasons.append(f"{arm} has already executed ({marker_rel(arm)}); the first execution binds")
    state["bound"] = not reasons
    state["reasons"] = reasons
    return state
