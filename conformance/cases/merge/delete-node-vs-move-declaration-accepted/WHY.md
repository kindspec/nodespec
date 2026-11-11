# delete-node-vs-move-declaration-accepted

§11: one branch deletes `c`, the other moves `c`'s node statement; the node comes back with none of its edges.

## The branches

- ours deletes `c`: its node statement and its two edges.
- theirs moves `c[c]` from after `b[b]` to after `e[e]`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Both sides delete line 4, identically. Theirs inserts after line 6; ours deletes lines 8 and 9, with line 7 unchanged between. Clean.

## The verdict

`c[c]` is declared and named by nothing, which is allowed; every edge names a declared node. Accepted, though ours deleted `c`.

> A delete against a move of the same line. One branch deletes a node, an edge carrying an id, a subgraph, a member line or an unnamed edge, or a `class` or `style` line; the other moves that line elsewhere. Git keeps the moved line, and the deleted thing comes back: a node with none of its edges, an edge without its `class` line, a subgraph with its member lines, a member nested again, an edge drawn again, a class or a style applied again.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
