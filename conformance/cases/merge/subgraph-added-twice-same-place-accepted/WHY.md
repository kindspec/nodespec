# subgraph-added-twice-same-place-accepted

Control for `subgraph-added-twice`: both branches add the identical block at the same place, and git keeps one.

## The branches

- ours appends a block `subgraph tier` holding `db`.
- theirs appends the identical block.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; the block has an explicit id and one member line naming a declared node. Any refusal of the merged file is one the merge produced.

## The merge

Both sides make the identical insertion at the same place; git keeps it once.

## The verdict

The merged file is ours' file: one subgraph line for `tier`, one member line for `db`. Accepted. §11 names this residual: the same declaration added at the same place is one declaration.

> The same declaration added on both branches at the same place. Git keeps one line, so two authors' identical `cache[Cache]` are one node, with both branches' edges. The same is true of an identical unnamed edge added at the same place.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
