# existence-09-bare-delete-vs-new-edge

SPEC.md §5.4's example: a delete of `c` against a new edge to `c`.

From existence case `09-bare-delete-vs-new-edge` (`existence/cases/09-bare-delete-vs-new-edge/`). The base is SPEC.md §5.4's, character for character: the existence chart with each node declared.

## The branches

- ours deletes `c`: its node statement and its two edges, `b --> c` and `c --> d`.
- theirs adds `e --> c` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 4, 8 and 9; theirs inserts after line 10. Line 10 is unchanged between. Clean, as §5.4 says.

## The verdict

Exactly §5.4's reading: `undeclared-id` for `c`, and nothing else.

> One branch deletes `c`, its node statement and its two edges; the other adds `e --> c` after the last edge. Git merges them without a conflict, and the merged file declares no `c` while `e --> c` names it. It is refused as `undeclared-id` for `c`.
>
> SPEC.md §5.4

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["c"]}}`
