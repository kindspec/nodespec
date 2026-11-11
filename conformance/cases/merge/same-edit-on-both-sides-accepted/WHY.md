# same-edit-on-both-sides-accepted

Both branches make the same relabel of `db`.

## The branches

- ours relabels `db` to `Orders store`.
- theirs makes the identical change.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Identical changes to line 4; git takes it once.

## The verdict

One node statement for `db`. Accepted.

> D1. Every id is declared exactly once, and everything else only names it.
>
> SPEC.md §5.1

Expected: `{"merge": "clean", "accept": true}`
