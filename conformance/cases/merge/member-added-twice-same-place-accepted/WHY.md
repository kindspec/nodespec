# member-added-twice-same-place-accepted

Control for `member-added-twice-in-one-block`: the identical member line at the same place is kept once.

## The branches

- ours adds `a` at the bottom of block `s`.
- theirs makes the same insertion.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each node is named by at most one member line. Any refusal of the merged file is one the merge produced.

## The merge

Identical insertions at the same place; git keeps one.

## The verdict

One member line for `a`. Accepted.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

Expected: `{"merge": "clean", "accept": true}`
