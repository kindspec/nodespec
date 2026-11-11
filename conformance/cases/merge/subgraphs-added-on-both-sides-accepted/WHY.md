# subgraphs-added-on-both-sides-accepted

Each branch adds its own subgraph with its own members.

## The branches

- ours adds `subgraph front [Frontend]` holding `user` and `api`, before the edges.
- theirs adds `subgraph data [Data]` holding `db`, at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; each block is top-level with an explicit id and member lines naming declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 7, theirs after line 11. Clean.

## The verdict

Two subgraphs, each declared once; each node has at most one holder. Accepted.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

Expected: `{"merge": "clean", "accept": true}`
