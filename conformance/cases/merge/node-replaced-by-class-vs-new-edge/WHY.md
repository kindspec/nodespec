# node-replaced-by-class-vs-new-edge

One branch replaces the node `cache` by a class `cache`, the other adds an edge to `cache`: the edge names a class, `wrong-kind`.

## The branches

- ours deletes the node `cache` (its node statement and `api --> cache`) and appends `classDef cache fill:#eef`.
- theirs adds `worker --> cache` before `worker --> db`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each id is declared once, as one kind; every edge names declared nodes; ours has no `class` line, so its `classDef` may stand last. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 3 and 7 and appends after line 9; theirs inserts after line 8, with line 9 unchanged before ours' insertion. Clean.

## The verdict

`cache` is declared only as a class, and an edge may name a node or a subgraph: `wrong-kind` for `cache`. Unlike §11's node-to-subgraph reuse, which is accepted because an edge may end at either kind, an edge may not end at a class.

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`
>
> SPEC.md §5.2

> an edge to an edge id or a class; a member line naming an edge id. Mermaid accepts each and reads something other than what it says: an edge to an edge id ends at no node, and an edge to a class makes a node with the class's name.
>
> SPEC.md §5.2

> `wrong-kind` applies to a name only when the id is declared and none of its declarations is of a kind that place may name.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["wrong-kind"], "ids": {"wrong-kind": ["cache"]}}`
