# same-edge-with-id-added-in-two-places

Both branches add the identical edge `worker e1@--> auth`, in different places: still two declarations of `e1`, and not a `duplicate-edge`.

## The branches

- ours adds `worker e1@--> auth` after `user --> api`.
- theirs adds the same line after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; the edge id is declared once on each side. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11: the same text at two places, which git keeps twice. Clean.

## The verdict

`e1@` stands on two links: `duplicate-declaration` for `e1`, "however alike the two declarations are". `duplicate-edge` is for edges without edge ids, so it does not apply.

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.
>
> SPEC.md §5.1

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge`
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["duplicate-declaration"], "ids": {"duplicate-declaration": ["e1"]}}`
