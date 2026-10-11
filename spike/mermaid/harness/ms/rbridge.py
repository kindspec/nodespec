# SPDX-License-Identifier: MIT
"""Runs R (spike/mermaid/r/rmodel.mjs) as PRE-REGISTRATION.md §4.4 pins it.

- Node must report exactly v24.20.0.
- The install must be the committed lockfile's: every package the lockfile
  names is present at the version it names (V0 installs it with `npm ci
  --ignore-scripts` first).
- R always runs with the network off: in a new network namespace
  (`unshare --net --map-root-user`), so "no network after install" holds for
  every call, not only in V0.
- A toolchain fault (R's exit 3, the canary failing) raises Broken, which
  aborts the run with a non-zero exit (§4.4).
"""
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE_MERMAID = os.path.dirname(os.path.dirname(HERE))
R_DIR = os.path.join(SPIKE_MERMAID, "r")
WRAPPER = os.path.join(R_DIR, "rmodel.mjs")
NODE_VERSION = "v24.20.0"
CONFIG = {"startOnLoad": False, "securityLevel": "strict", "flowchart": {"htmlLabels": False},
          "maxEdges": 100000}


class Broken(Exception):
    """The toolchain is broken: the run aborts (§4.4)."""


def node_bin():
    n = shutil.which("node")
    if not n:
        raise Broken("node is not on PATH")
    v = subprocess.run([n, "--version"], capture_output=True, text=True).stdout.strip()
    if v != NODE_VERSION:
        raise Broken(f"node is {v}, §4.4 pins {NODE_VERSION}")
    return n


def check_install(r_dir=R_DIR):
    """Every package in the committed lockfile is installed at its version."""
    lock = json.load(open(os.path.join(r_dir, "package-lock.json")))
    bad = []
    for p, meta in lock.get("packages", {}).items():
        if not p:
            continue
        pj = os.path.join(r_dir, p, "package.json")
        try:
            got = json.load(open(pj)).get("version")
        except OSError:
            got = None
        if got != meta.get("version"):
            bad.append(f"{p}: installed {got}, lockfile {meta.get('version')}")
    if bad:
        raise Broken("R's install does not match package-lock.json: " + "; ".join(bad[:3]))
    return len(lock["packages"]) - 1


def offline(argv):
    return ["unshare", "--net", "--map-root-user", "--"] + argv


def run_batch(texts, env_extra=None, r_dir=R_DIR, timeout=None):
    """texts: list of str. Returns (config line, [result dict per text])."""
    node = node_bin()
    lines = "".join(json.dumps({"id": i, "text": t}) + "\n" for i, t in enumerate(texts))
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/nonexistent"),
           "LC_ALL": "C.UTF-8"}
    env.update(env_extra or {})
    p = subprocess.run(offline([node, os.path.join(r_dir, "rmodel.mjs"), "--batch"]), input=lines,
                       capture_output=True, text=True, env=env, cwd=r_dir, timeout=timeout)
    out = [json.loads(x) for x in p.stdout.splitlines() if x.strip()]
    if p.returncode == 3 or any(o.get("abort") for o in out):
        ab = next((o for o in out if o.get("abort")), {})
        raise Broken(f"R aborted: {ab.get('cls')}: {ab.get('msg')} (exit {p.returncode})")
    if p.returncode != 0 or not out or "config" not in out[0]:
        raise Broken(f"R exited {p.returncode}: {p.stderr.strip()[:300]}")
    cfg, res = out[0]["config"], out[1:]
    if len(res) != len(texts) or [o["id"] for o in res] != list(range(len(texts))):
        raise Broken("R's batch output does not match its input")
    return cfg, res


def run_one(text, env_extra=None, r_dir=R_DIR):
    """Single-shot mode, as V0 also runs it."""
    node = node_bin()
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/nonexistent"),
           "LC_ALL": "C.UTF-8"}
    env.update(env_extra or {})
    p = subprocess.run(offline([node, os.path.join(r_dir, "rmodel.mjs")]), input=text,
                       capture_output=True, text=True, env=env, cwd=r_dir)
    try:
        o = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        o = {"abort": True, "cls": "NoOutput", "msg": p.stderr.strip()[:200]}
    return p.returncode, o


def parses(res):
    """§4.4: True if R's parse succeeded."""
    return bool(res.get("parse"))


class RCache:
    """Batches R calls and remembers results by text, so a text seen in many
    cases is run once."""

    def __init__(self):
        self.cache = {}
        self.config = None

    def get_many(self, texts):
        todo = sorted({t for t in texts if t not in self.cache})
        for i in range(0, len(todo), 400):
            chunk = todo[i:i + 400]
            cfg, res = run_batch(chunk)
            self.config = cfg
            for t, r in zip(chunk, res):
                r.pop("id", None)
                self.cache[t] = r
        return [self.cache[t] for t in texts]

    def get(self, text):
        return self.get_many([text])[0]
