# existence-07-relabel-vs-rename-conflict

A relabel of `db` against a rename of `db`: both change `db`'s node statement, and git conflicts.

From existence case `07-relabel-vs-rename` (`existence/cases/07-relabel-vs-rename/`). Declarations moved out of the edges. The existence case is the control, and it stays one: both legs still change the line that declares `db`.

## The branches

- ours relabels `db` to `Orders store`.
- theirs renames `db` to `orders` everywhere.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Both sides change line 4, differently. Conflict.

## The verdict

A conflict carries no verdict: git stopped, which is loud.

> A merge is checked by checking its result.
>
> SPEC.md §8

Expected: `{"merge": "conflict"}`
