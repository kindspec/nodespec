# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`nodespec check FILE...`: its output and its exit codes."""

import os
import re
import subprocess
import sys

from nodespec import check
from nodespec.cli import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_bytes(text.encode() if isinstance(text, str) else text)
    return str(p)


def test_accepted_file_prints_nothing_and_exits_0(tmp_path, capsys):
    p = write(tmp_path, "ok.mmd", "flowchart TD\n  a[A]\n")
    assert main(["check", p]) == 0
    assert capsys.readouterr().out == ""


def test_refused_file_prints_file_message_identifier(tmp_path, capsys):
    p = write(tmp_path, "bad.mmd", "flowchart TD\n  a[A]\n  a --> b\n")
    assert main(["check", p]) == 1
    assert capsys.readouterr().out == (
        f"{p}: `b` is named by an edge and declared nowhere [undeclared-id]\n"
    )


def test_several_files(tmp_path, capsys):
    ok = write(tmp_path, "ok.mmd", "graph\n")
    bad = write(tmp_path, "bad.mmd", "")
    assert main(["check", ok, bad]) == 1
    out = capsys.readouterr().out.splitlines()
    assert out == [f"{bad}: the file holds no statement line, so no header [no-header]"]


def test_unreadable_file_is_no_verdict(tmp_path, capsys):
    assert main(["check", str(tmp_path / "absent.mmd")]) == 2
    assert "cannot be read" in capsys.readouterr().err


def test_usage(capsys):
    assert main([]) == 2
    assert main(["check"]) == 2
    assert main(["lint", "x"]) == 2


def test_module_entry_point(tmp_path):
    p = write(tmp_path, "bad.mmd", "flowchart TD\n  direction LR\n")
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "reference"))
    r = subprocess.run(
        [sys.executable, "-m", "nodespec", "check", p], capture_output=True, text=True, env=env
    )
    assert r.returncode == 1
    assert r.stdout.endswith("[direction-outside-block]\n")


def test_messages_name_entities_not_offsets():
    texts = [
        "flowchart TD\n  a --> b\n  c[C]\n  c[C]\n  x y z\n  end\n  subgraph s\n    s\n",
        "\ufeffflowchart TD\n  a[A] --> b\n<<<<<<< x\n  style q fill:red\n  linkStyle 3 x\n",
        "x\n" * 3,
        b"flowchart TD\n\xff\n",
    ]
    for t in texts:
        for f in check(t):
            assert not re.search(r"\b(line|column|col|offset|byte|position)\s*\d", f.message), f
            assert not re.search(r"\b\d+:\d+\b", f.message), f
