# class-added-on-both-branches

Each branch gives node `a` a class, a different one: two `class` lines for `a`.

## The branches

- ours adds `class a hot` before `class b hot`.
- theirs adds `class a cold` after `class b hot`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: classes and nodes declared once; the `class` lines are last on each side and each id is classed once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 6, theirs after line 7. Line 7 is unchanged between. Clean.

## The verdict

`a` is the target of two `class` lines: `styled-twice` for `a`. With one class per line, `a` would carry two classes. The `class` lines are still all last.

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`. Mermaid applies both, in file order, so where they set the same property the later one wins; two branches that each style or class the same id would merge clean, and the order of their lines would decide the picture.
>
> SPEC.md §7

> A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.
>
> SPEC.md §7

Expected: `{"merge": "clean", "refusal": ["styled-twice"], "ids": {"styled-twice": ["a"]}}`
