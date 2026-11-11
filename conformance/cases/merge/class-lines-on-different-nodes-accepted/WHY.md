# class-lines-on-different-nodes-accepted

Each branch adds a `class` line among the class lines, for different nodes.

## The branches

- ours adds `class a hot` before `class b hot`.
- theirs adds `class c hot` after it.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: one `classDef`; `class` lines last, each node classed once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 7, theirs after line 8. Clean.

## The verdict

Three `class` lines, all last, each for a different node. Accepted.

> A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.
>
> SPEC.md §7

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`. Mermaid applies both, in file order, so where they set the same property the later one wins; two branches that each style or class the same id would merge clean, and the order of their lines would decide the picture.
>
> SPEC.md §7

Expected: `{"merge": "clean", "accept": true}`
