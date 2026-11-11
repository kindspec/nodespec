# existence-04-retarget-vs-rename-adjacent-conflict

A retarget to `auth` against a rename of `auth`, on adjacent lines: git conflicts, as it did in the existence case.

From existence case `04-retarget-vs-rename` (`existence/cases/04-retarget-vs-rename/`). Declarations moved out of the edges, keeping the edge order of the existence case, so `api --> auth` and `worker --> db` stay adjacent.

## The branches

- ours retargets `worker --> db` to `worker --> auth`.
- theirs renames `auth` to `identity` everywhere: its node statement and `api --> auth`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes line 11; theirs changes lines 5 and 10. The changes to lines 10 and 11 abut, so git reports a conflict, as it did for the existence case. `existence-04-retarget-vs-rename-spaced` is the same edit with the two lines apart.

## The verdict

A conflict carries no verdict: git stopped. The file it leaves holds conflict markers, which the profile refuses as a line rule, but no merged file is checked.

> A merge is checked by checking its result.
>
> SPEC.md §8

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.
>
> SPEC.md §4.2

Expected: `{"merge": "conflict"}`
