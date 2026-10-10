# SPDX-License-Identifier: MIT
"""§10.3: what each blind role gets, as exported directories.

- F gets PRE-REGISTRATION.md (this document, whole), Mermaid 12.1.0's
  docs/syntax/flowchart.md, and Appendix D's fixture contract (inside the
  document).
- X gets §4, §5, Appendices A and C, the same Mermaid document, and Appendix
  D whole. §10.3's letter is "Appendix D's extractor contract"; giving the
  fixture contract too, a format with no answers, so X mirrors
  expect.json's fields, is the coordinator's implementation choice (LOG
  §2). Not the harness, not R, not the fixtures.

X's excerpt is spike/mermaid/blind/x/SPEC.md, cut byte for byte from the
document by `x_spec()`; V3 checks the committed file equals a fresh cut. An
export is `git archive` of the permitted paths only, at a commit, extracted
into a new directory outside the repository: no .git, no other checkout.
The prompts are Appendix E's, verbatim, with the Markdown quoting removed.
"""
import hashlib
import io
import os
import subprocess
import tarfile

from .transcript import SPIKE

DOC = os.path.join(SPIKE, "PRE-REGISTRATION.md")
MERMAID_DOC = "spike/mermaid/blind/mermaid-12.1.0-flowchart.md"
MERMAID_DOC_BLOB = "934bd13efcc6261d55dcdfa950aebd52022d5dac"  # mermaid@12.1.0 docs/syntax/flowchart.md
X_SPEC = "spike/mermaid/blind/x/SPEC.md"
F_PATHS = ["spike/mermaid/PRE-REGISTRATION.md", MERMAID_DOC]
X_PATHS = [X_SPEC, MERMAID_DOC]
SECTIONS = ["## 4. The model", "## 5. The oracle", "## Appendix A", "## Appendix C", "## Appendix D"]
X_HEADER = ("<!-- SPDX-License-Identifier: CC-BY-4.0 -->\n"
            "<!-- Cut byte for byte from spike/mermaid/PRE-REGISTRATION.md by harness/ms/blind.py:\n"
            "     its sections 4 and 5 and Appendices A, C and D, in that order. -->\n")


def _section(doc, head):
    i = doc.index("\n" + head) + 1
    j = doc.find("\n## ", i + 1)
    return doc[i:] if j < 0 else doc[i:j + 1]


def x_spec(doc_text=None):
    doc = doc_text if doc_text is not None else open(DOC, encoding="utf-8").read()
    return X_HEADER + "\n".join(_section(doc, h) for h in SECTIONS)


def prompt(role, doc_text=None):
    """Appendix E's prompt for F or X, with '> ' quoting removed."""
    doc = doc_text if doc_text is not None else open(DOC, encoding="utf-8").read()
    e = _section(doc, "## Appendix E")
    start = e.index(f"**{role}:**\n\n") + len(f"**{role}:**\n\n")
    lines = []
    for ln in e[start:].split("\n"):
        if not ln.startswith(">"):
            break
        lines.append(ln[2:] if ln.startswith("> ") else ln[1:])
    return "\n".join(lines).rstrip("\n") + "\n"


def export(role, commit, out_dir, repo=None):
    """git archive of the role's paths at commit into out_dir, which must not
    exist and must be outside the repository. Returns the manifest
    [(path, sha256)]."""
    repo = repo or SPIKE
    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True).stdout.strip()
    real = os.path.realpath(out_dir)
    if os.path.exists(out_dir):
        raise SystemExit(f"refusing: {out_dir} exists")
    if real == top or real.startswith(top + os.sep):
        raise SystemExit("refusing: an export lives outside the repository")
    paths = {"F": F_PATHS, "X": X_PATHS}[role]
    tar = subprocess.run(["git", "-C", top, "archive", "--format=tar", commit, "--", *paths],
                         capture_output=True, check=True).stdout
    os.makedirs(out_dir)
    manifest = []
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            data = tf.extractfile(m).read()
            name = os.path.basename(m.name)
            with open(os.path.join(out_dir, name), "wb") as f:
                f.write(data)
            manifest.append((name, hashlib.sha256(data).hexdigest()))
    if role == "F":
        os.makedirs(os.path.join(out_dir, "v-fixtures"))
        os.makedirs(os.path.join(out_dir, "sealed"))
    for root, dirs, _ in os.walk(out_dir):
        if ".git" in dirs:
            raise SystemExit("refusing: the export holds a .git")
    return sorted(manifest)
