<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Does nodespec earn its existence?

`CRITERION.md` fixes, before any case ran, what a constructed silent-wrong
merge of a Mermaid flowchart is. `cases/` holds the candidates, each a
`base.mmd`, `ours.mmd` and `theirs.mmd` with a line on what each leg does.
`run.py` runs each once through the Mermaid spike's harness, unchanged,
and writes `results.jsonl`.

The case files are released under CC0-1.0, as org contract §6 sets for
fixtures; the prose is CC-BY-4.0 and `run.py` MIT.
