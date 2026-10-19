<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Does nodespec earn its existence?

`CRITERION.md` fixes, before any case ran, what a constructed silent-wrong
merge of a Mermaid flowchart is. `cases/` holds the candidates, each a
`base.mmd`, `ours.mmd` and `theirs.mmd` with a line on what each leg does.
`RESULT.md` gives the verdict and every candidate's result.
`run.py` runs each once through the Mermaid spike's harness, unchanged,
and appends one line per candidate to `results.jsonl`, the only file it
writes.

The case files, with the one-line README beside each, are released under
CC0-1.0, as org contract §6 sets for fixtures; `CRITERION.md` and this
file are CC-BY-4.0, and `run.py` MIT.
