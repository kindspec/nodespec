# style-added-on-both-branches

Each branch adds a `style` line for `api`, with different fills.

## The branches

- ours adds `style api fill:#f00` after the node statements.
- theirs adds `style api fill:#0f0` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each side styles `api` once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 6, theirs after line 11. Clean.

## The verdict

`api` is the target of two `style` lines: `styled-twice` for `api`. Mermaid would apply both and the later fill would win.

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`. Mermaid applies both, in file order, so where they set the same property the later one wins; two branches that each style or class the same id would merge clean, and the order of their lines would decide the picture.
>
> SPEC.md §7

Expected: `{"merge": "clean", "refusal": ["styled-twice"], "ids": {"styled-twice": ["api"]}}`
