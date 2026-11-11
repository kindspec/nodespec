# delete-node-vs-member-line

One branch deletes `c`, the other moves `c` into a block by adding a member line: the member line names an undeclared id.

## The branches

- ours deletes `c`: its node statement and `b --> c`.
- theirs moves `c` into subgraph `s` by adding the member line `c`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: nodes are declared once at the top level, the block `s` holds member lines naming declared nodes, and no id has two holders. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 4 and 6; theirs inserts after line 10. Clean.

## The verdict

The member line `c` names `c`, which nothing declares: `undeclared-id` for `c`. This is the merge D3 exists for: a move into a block adds a name, so a delete on the other branch leaves a name with no declaration rather than a node back in the block.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["c"]}}`
