# delete-subgraph-vs-move-block-accepted

§11: one branch deletes subgraph `s`, the other moves its block to the end; the subgraph comes back with its member lines.

## The branches

- ours deletes the block `s` and the blank line after it.
- theirs moves the block below the six edges.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every id declared once; the block's member lines name declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Both sides delete lines 7 to 11 identically; theirs appends after line 17, the last. The six edges lie unchanged between, more lines than the block, so git reads theirs as moving the block rather than the edges. Clean.

## The verdict

One subgraph `s` holding `a` and `b`. Accepted.

> A delete against a move of the same line. One branch deletes a node, an edge carrying an id, a subgraph, a member line or an unnamed edge, or a `class` or `style` line; the other moves that line elsewhere. Git keeps the moved line, and the deleted thing comes back: a node with none of its edges, an edge without its `class` line, a subgraph with its member lines, a member nested again, an edge drawn again, a class or a style applied again.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
