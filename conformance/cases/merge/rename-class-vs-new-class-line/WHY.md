# rename-class-vs-new-class-line

One branch renames class `hot` to `warm`, the other gives `hot` to another node: the new `class` line names an undeclared class.

## The branches

- ours renames the class `hot` to `warm`: its `classDef` line and `class a hot`.
- theirs adds `class b hot` after the last `class` line.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: nodes and classes are each declared once; `class` lines come last, each with one target and one declared class, and no id is classed twice. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes lines 7 and 9; theirs inserts after line 10. Line 10 is unchanged between. Clean.

## The verdict

A `class` line names its last id as a class. `class b hot` names `hot`, and the merged file declares `warm`, not `hot`: `undeclared-id` for `hot`. The class lines are still last, and `b` is classed once.

> A `class` statement's targets are the ids before its last one.
>
> SPEC.md §5.2

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["hot"]}}`
