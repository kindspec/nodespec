# class-line-added-after-class-lines-accepted

Control for `statement-added-above-new-class-line`: theirs adds the same `class` line after the existing one instead.

## The branches

- ours declares `c[C]` just above `class a hot`, as in the refused case.
- theirs appends `class b hot` after `class a hot`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: `class` lines are last on each side; every id is declared once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 6, theirs after line 7. Clean.

## The verdict

Both `class` lines follow every other statement line. Accepted.

> A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.
>
> SPEC.md §7

Expected: `{"merge": "clean", "accept": true}`
