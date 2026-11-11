# node-vs-edge-id-same-id

One branch adds an edge with the id `link1`, the other a node `link1`: one id declared as two kinds.

## The branches

- ours adds `api link1@--> worker` after `user --> api`.
- theirs declares a node `link1[Link]` after the other node statements.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; ours declares the edge id once on a link with one id each side, theirs declares the node once. Any refusal of the merged file is one the merge produced.

## The merge

Theirs inserts after line 6, ours after line 8. Clean.

## The verdict

`link1` is declared as an edge id and as a node: `kind-clash` for `link1`. Mermaid would drop the node statement whose id is an edge id declared above it.

> An id declared as two kinds is refused as `kind-clash`: a node and a subgraph both named `cache`, a node and an edge id `e1`, a class and a node.
>
> SPEC.md §5.3

Expected: `{"merge": "clean", "refusal": ["kind-clash"], "ids": {"kind-clash": ["link1"]}}`
