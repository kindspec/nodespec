# delete-member-line-vs-move-accepted

§11: one branch takes `a` out of block `s`, the other moves `a` into block `t`; `a` is nested again.

## The branches

- ours deletes the member line `a` from block `s`.
- theirs moves the member line `a` from `s` to `t`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each node is named by at most one member line; member lines name declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Both sides delete line 10 identically; theirs inserts after line 14. Clean.

## The verdict

`a` has one holder, `t`. Accepted, though ours meant `a` to have none.

> A delete against a move of the same line. One branch deletes a node, an edge carrying an id, a subgraph, a member line or an unnamed edge, or a `class` or `style` line; the other moves that line elsewhere. Git keeps the moved line, and the deleted thing comes back: a node with none of its edges, an edge without its `class` line, a subgraph with its member lines, a member nested again, an edge drawn again, a class or a style applied again.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
