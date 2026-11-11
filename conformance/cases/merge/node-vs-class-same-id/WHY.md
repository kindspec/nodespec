# node-vs-class-same-id

One branch adds `classDef cache`, the other a node `cache` and an edge to it: `kind-clash`, and the edge is not also `wrong-kind`.

## The branches

- ours appends `classDef cache fill:#eef`.
- theirs declares `cache[Cache]` and adds `api --> cache` before `worker --> db`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; ours' class and theirs' node are each declared once. Any refusal of the merged file is one the merge produced.

## The merge

Theirs inserts after lines 6 and 10; ours after line 11, with line 11 unchanged between. Clean.

## The verdict

`cache` is declared as a class and as a node: `kind-clash` for `cache`. The edge names an id with a node declaration, so it is not `wrong-kind`.

> An id declared as two kinds is refused as `kind-clash`: a node and a subgraph both named `cache`, a node and an edge id `e1`, a class and a node.
>
> SPEC.md §5.3

> An id declared both as a node and as a class is `kind-clash` (§5.3), and an edge naming it is not also `wrong-kind`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["kind-clash"], "ids": {"kind-clash": ["cache"]}}`
