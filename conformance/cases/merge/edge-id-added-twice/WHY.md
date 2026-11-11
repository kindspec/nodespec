# edge-id-added-twice

Both branches add an edge carrying the id `e1`, on different edges: `e1@` on two links.

## The branches

- ours adds `user e1@--> auth` after `user --> api`.
- theirs adds `worker e1@--> auth` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each side's edge id is declared once, on a link with one id on each side. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11. Clean.

## The verdict

Two links carry `e1@`: `duplicate-declaration` for `e1`. The two edges have ids, so `duplicate-edge` does not apply to them, and they differ in any case.

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.
>
> SPEC.md §5.1

> An edge id is declared by the one edge that carries it (D1).
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["duplicate-declaration"], "ids": {"duplicate-declaration": ["e1"]}}`
