# delete-edge-id-vs-class-on-it

One branch deletes the edge `e1`, the other gives it a class: the `class` line names an undeclared id.

## The branches

- ours deletes the edge `a e1@--> b`.
- theirs adds `class e1 hot` after the last `class` line.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: the edge id `e1` is declared once, on a link with one id on each side; `class` lines are last and each names declared targets and a declared class. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes line 5; theirs inserts after line 8. Clean.

## The verdict

`class e1 hot` names `e1` as a target, and nothing declares `e1` any more: `undeclared-id` for `e1`. `hot` is still declared.

> An edge id is declared by the one edge that carries it (D1).
>
> SPEC.md §4.6

> A `class` statement's targets are the ids before its last one.
>
> SPEC.md §5.2

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["e1"]}}`
