# statement-added-above-new-class-line

One branch adds a `class` line right after the statements, the other a node statement just above the old `class` line: the merged `class` line has a statement after it.

## The branches

- ours declares `c[C]` after the blank line, just above `class a hot`.
- theirs adds `class b hot` after `classDef hot`, before the blank line.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: in each, only blank lines and `class` lines follow the first `class` line; every id is declared once. Any refusal of the merged file is one the merge produced.

## The merge

Theirs inserts after line 5 and ours after line 6, the blank line, which neither side changes. Clean.

## The verdict

`class b hot` is followed by `c[C]`, a statement line that is not a `class` line: `class-not-last`, which carries no id. Neither `class` line names `c`, so this merge strips no class in Mermaid; the rule is read literally and refuses the order anyway.

> A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.
>
> SPEC.md §7

> With every `class` line last, both are impossible, and moving a declaration or adding a name on another branch cannot strip a class.
>
> SPEC.md §7

Expected: `{"merge": "clean", "refusal": ["class-not-last"]}`
