# delete-node-vs-new-edge-between-others-accepted

Control for `existence-09-bare-delete-vs-new-edge`: the same delete of `c`, against a new edge that names only surviving nodes.

## The branches

- ours deletes `c`: its node statement and its two edges.
- theirs adds `e --> a` after the last edge; it differs from the refused case's theirs by one byte.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

As in the refused case: ours deletes lines 4, 8 and 9, theirs inserts after line 10. Clean.

## The verdict

Every id named, `a`, `b`, `d` and `e`, is declared once as a node; no edge is repeated. Accepted.

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "accept": true}`
