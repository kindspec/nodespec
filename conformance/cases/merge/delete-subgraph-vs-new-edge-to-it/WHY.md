# delete-subgraph-vs-new-edge-to-it

One branch deletes a subgraph, the other adds an edge ending at it: the edge names an undeclared id.

## The branches

- ours deletes the block `backend` (its subgraph line, member lines and `end`) and the blank line after it.
- theirs adds `user --> backend`, an edge ending at the subgraph, after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once at the top level; the block has an explicit id and holds member lines naming declared nodes; theirs' edge ends at a declared subgraph, which an edge may. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 6 to 10; theirs inserts after line 12. Clean.

## The verdict

`user --> backend` names `backend`, and no subgraph line declares it any more: `undeclared-id` for `backend`. This is the merge §5.2 names when it lets an edge end at a subgraph.

> An edge may end at a subgraph (the owner, 2026-10-19). Mermaid accepts one, and D1 still holds for it: an edge to a subgraph that the other branch deleted names an undeclared id.
>
> SPEC.md §5.2

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["backend"]}}`
