# existence-06-subgraph-vs-node-same-id

One branch adds a subgraph `cache`, the other a node `cache`: one id declared as two kinds.

From existence case `06-subgraph-vs-node-same-id` (`existence/cases/06-subgraph-vs-node-same-id/`). The existence case put `db` inside the block by position and declared nodes inside edges. Here the block holds the member line `db`, and theirs declares `cache` by a node statement and adds `api --> cache`.

## The branches

- ours adds a block `subgraph cache[Cache tier]` holding the member line `db`, at the end.
- theirs declares a node `cache[Cache]` and adds `api --> cache` before `worker --> db`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; ours' block has an explicit id and holds one member line naming a declared node. Any refusal of the merged file is one the merge produced.

## The merge

Ours appends after line 11; theirs inserts after lines 6 and 10. Line 11 is unchanged between theirs' second insertion and ours' block. Clean.

## The verdict

`cache` is declared by a subgraph line and by a node statement: `kind-clash` for `cache`. The edge `api --> cache` names an id that has a node declaration, which an edge may name, so it is not `wrong-kind`; the subgraph and the node are each declared once, so it is not `duplicate-declaration`.

> An id declared as two kinds is refused as `kind-clash`: a node and a subgraph both named `cache`, a node and an edge id `e1`, a class and a node.
>
> SPEC.md §5.3

> `wrong-kind` applies to a name only when the id is declared and none of its declarations is of a kind that place may name.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["kind-clash"], "ids": {"kind-clash": ["cache"]}}`
