# classdef-added-twice

Both branches add a `classDef warm`, with different styles, in different places.

## The branches

- ours adds `classDef warm fill:#fd0` after the node statements.
- theirs adds `classDef warm fill:#f80` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each side's `classDef` declares `warm` once with a one-item style list. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 6, theirs after line 11. Clean.

## The verdict

Two `classDef` lines declare `warm`: `duplicate-declaration` for `warm`. Mermaid would join their styles, and the later `fill` would win.

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.
>
> SPEC.md §5.1

Expected: `{"merge": "clean", "refusal": ["duplicate-declaration"], "ids": {"duplicate-declaration": ["warm"]}}`
