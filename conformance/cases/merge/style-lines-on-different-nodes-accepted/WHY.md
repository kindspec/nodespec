# style-lines-on-different-nodes-accepted

Each branch adds a `style` line, for different nodes.

## The branches

- ours adds `style user fill:#eee` after the node statements.
- theirs adds `style db fill:#ddd,stroke-width:2px` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each style list is colours and a number with a unit. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 6, theirs after line 11. Clean.

## The verdict

Each node is the target of at most one `style` line; `style` lines may come in any order. Accepted.

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`. Mermaid applies both, in file order, so where they set the same property the later one wins; two branches that each style or class the same id would merge clean, and the order of their lines would decide the picture.
>
> SPEC.md §7

> Apart from `class` lines, D4 orders nothing. Declarations, edges, blocks and `style` lines may come in any order
>
> SPEC.md §7

Expected: `{"merge": "clean", "accept": true}`
