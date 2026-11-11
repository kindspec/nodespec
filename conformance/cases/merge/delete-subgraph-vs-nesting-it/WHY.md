# delete-subgraph-vs-nesting-it

One branch deletes subgraph `inner`, the other nests it in `outer` by a member line: the member line names an undeclared id.

## The branches

- ours deletes the block `inner` and the blank line before it.
- theirs nests `inner` in `outer` by adding the member line `inner` to `outer`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: both blocks are top-level with explicit ids; member lines name declared nodes, and in theirs `inner` names a declared subgraph, which nests it. Any refusal of the merged file is one the merge produced.

## The merge

Theirs inserts after line 7; ours deletes lines 9 to 12. Line 8 (`end`) is unchanged between. Clean.

## The verdict

The member line `inner` names `inner`, and no subgraph line declares it: `undeclared-id` for `inner`. `b` is still declared and has no holder, which is allowed.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["inner"]}}`
