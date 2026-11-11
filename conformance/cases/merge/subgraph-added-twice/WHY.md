# subgraph-added-twice

Both branches add a subgraph `tier`, in different places: two subgraph lines for one id.

## The branches

- ours adds `subgraph tier` holding `api`, between the declarations and the edges.
- theirs adds `subgraph tier` holding `db`, at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each side's block is the only one, with an explicit id and one member line naming a declared node. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 7; theirs inserts after line 11. Clean.

## The verdict

Two subgraph lines declare `tier`: `duplicate-declaration` for `tier`. The two member lines name different nodes, so no id has two holders. Mermaid would fuse the two blocks into one subgraph.

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.
>
> SPEC.md §5.1

Expected: `{"merge": "clean", "refusal": ["duplicate-declaration"], "ids": {"duplicate-declaration": ["tier"]}}`
