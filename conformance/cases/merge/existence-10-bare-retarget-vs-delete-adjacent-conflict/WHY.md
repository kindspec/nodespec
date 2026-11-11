# existence-10-bare-retarget-vs-delete-adjacent-conflict

The same retarget against the same delete on §5.4's base, where `e[e]` and the retargeted edge are adjacent lines: git conflicts.

From existence case `10-bare-retarget-vs-delete` (`existence/cases/10-bare-retarget-vs-delete/`). Each node is declared as in §5.4. Declaring the nodes puts `e[e]` directly above `a --> b`, so the rewrite turns the existence case's clean merge into a conflict.

## The branches

- ours retargets `a --> b` to `a --> e`.
- theirs deletes `e`: its node statement and `d --> e`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Theirs deletes line 6 and ours changes line 7: the hunks abut, and git conflicts.

## The verdict

A conflict carries no verdict: git stopped, which is loud.

> A merge is checked by checking its result.
>
> SPEC.md §8

Expected: `{"merge": "conflict"}`
