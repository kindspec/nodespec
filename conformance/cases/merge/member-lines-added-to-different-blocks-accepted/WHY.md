# member-lines-added-to-different-blocks-accepted

Each branch adds a member line, for a different node, to a different block.

## The branches

- ours adds `api` to block `front`.
- theirs adds `worker` to block `data`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each node is declared once and has at most one holder. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 12, theirs after line 16. Clean.

## The verdict

Each member line names a declared node, each node has one holder at most. Accepted.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

Expected: `{"merge": "clean", "accept": true}`
