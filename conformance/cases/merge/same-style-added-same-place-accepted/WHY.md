# same-style-added-same-place-accepted

Control for `style-added-on-both-branches`: the identical `style` line at the same place is kept once.

## The branches

- ours appends `style api fill:#f00`.
- theirs appends the identical line.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; `api` is styled once. Any refusal of the merged file is one the merge produced.

## The merge

Identical insertions at the same place; git keeps one.

## The verdict

`api` is the target of one `style` line. Accepted.

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`. Mermaid applies both, in file order, so where they set the same property the later one wins; two branches that each style or class the same id would merge clean, and the order of their lines would decide the picture.
>
> SPEC.md §7

Expected: `{"merge": "clean", "accept": true}`
