# delete-edge-with-id-vs-move-accepted

§11: one branch deletes the edge `e1` and its `class` line, the other moves the edge; the edge comes back without its class.

## The branches

- ours deletes `a e1@--> b` and `class e1 hot`.
- theirs moves `a e1@--> b` below `b --> c`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: nodes, the edge id and the class are each declared once; the `class` line is last and names a declared edge and class. Any refusal of the merged file is one the merge produced.

## The merge

Both sides delete line 6. Theirs inserts after line 7; ours deletes line 10. Clean.

## The verdict

The merged file declares `e1` once and has no `class` line. `hot` is declared and unused. Accepted.

> A delete against a move of the same line. One branch deletes a node, an edge carrying an id, a subgraph, a member line or an unnamed edge, or a `class` or `style` line; the other moves that line elsewhere. Git keeps the moved line, and the deleted thing comes back: a node with none of its edges, an edge without its `class` line, a subgraph with its member lines, a member nested again, an edge drawn again, a class or a style applied again.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
