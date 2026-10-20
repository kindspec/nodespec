# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`reference/` imports the standard library and nothing else.

The audit parses the tree rather than importing it, so an import inside a
function no test calls is still seen.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE = os.path.join(ROOT, "reference")
INTERNAL = {"nodespec"}


def imports(path):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            yield node.module.split(".")[0]


def py_files():
    for dirpath, dirnames, files in os.walk(REFERENCE):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in sorted(files):
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)


def test_reference_is_stdlib_only():
    files = list(py_files())
    assert files, "found no Python under reference/"
    bad = [
        (os.path.relpath(p, ROOT), m)
        for p in files
        for m in imports(p)
        if m not in sys.stdlib_module_names and m not in INTERNAL
    ]
    assert bad == []


def test_the_audit_sees_a_third_party_import(tmp_path):
    p = tmp_path / "x.py"
    p.write_text("def f():\n    import yaml\n")
    assert "yaml" in set(imports(str(p)))
    assert "yaml" not in sys.stdlib_module_names
