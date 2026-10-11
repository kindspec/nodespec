# SPDX-License-Identifier: MIT
"""§11.1: every invocation of an arm, the aggregator, a blind role or the
sealed run writes a transcript under spike/mermaid/results/, aborted runs
included. The transcript opens before the arguments are parsed, is written
line-buffered, and is closed in a `finally` with the exit status; SIGTERM and
SIGHUP are turned into an exit so they are recorded too.

An execution marker line ("# executed: ...") is written when a corpus (or,
for the aggregator, its inputs) is opened (blockspec LOG §18, H3).
"""
import datetime
import os
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(os.path.dirname(HERE))          # spike/mermaid
RESULTS = os.path.join(SPIKE, "results")
DEFAULT_DIR = os.path.join(RESULTS, "transcripts")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cmd(*a):
    try:
        r = subprocess.run(list(a), capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or r.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unavailable ({e.__class__.__name__})"


class _Tee:
    def __init__(self, stream, f):
        self.stream, self.f = stream, f

    def write(self, s):
        self.stream.write(s)
        self.f.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()
        self.f.flush()

    def __getattr__(self, n):
        return getattr(self.stream, n)


class Transcript:
    def __init__(self, cmd, argv, out_dir=None):
        out_dir = out_dir or DEFAULT_DIR
        os.makedirs(out_dir, exist_ok=True)
        stamp = now().replace(":", "")
        base = os.path.join(out_dir, f"{stamp}-{cmd}")
        path, n = base + ".txt", 1
        while os.path.exists(path):
            n += 1
            path = f"{base}.{n}.txt"
        self.path = path
        self.f = open(path, "w", encoding="utf-8", buffering=1)
        self.f.write(f"# mermaid-spike {cmd}\n# argv: {' '.join(argv)}\n# start: {now()}\n"
                     f"# nodespec HEAD: {_cmd('git', '-C', SPIKE, 'rev-parse', 'HEAD')}\n"
                     f"# python: {sys.version.split()[0]}\n# git: {_cmd('git', '--version')}\n"
                     f"# node: {_cmd('node', '--version')}\n")
        self._out, self._err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = _Tee(sys.stdout, self.f), _Tee(sys.stderr, self.f)
        for s in (signal.SIGTERM, signal.SIGHUP):
            signal.signal(s, self._signal)

    def note(self, line):
        self.f.write(f"# {line}\n")

    def binding(self, state):
        self.f.write(f"# bound: {state['bound']}"
                     + (f" (validation commit {state['validation_commit']})" if state["bound"] else "") + "\n")
        for r in state.get("reasons", []):
            self.f.write(f"#   not bound: {r}\n")
        self.f.write("\n")

    def mark_executed(self):
        self.f.write(f"\n# executed: {now()}\n")
        self.f.flush()

    def _signal(self, signum, frame):
        raise SystemExit(128 + signum)

    def close(self, rc, how):
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = self._out, self._err
        self.f.write(f"\n# end: {now()}\n# {how}: exit status {rc}\n")
        self.f.close()
