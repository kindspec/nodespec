# existence-04-retarget-vs-rename-spaced

The same retarget against the same rename, with the two edges apart: git merges clean and the retargeted edge names `auth`, which the rename removed.

From existence case `04-retarget-vs-rename` (`existence/cases/04-retarget-vs-rename/`). Declarations moved out of the edges, and `api --> auth` moved to the top of the edges so that it is not next to `worker --> db`, which makes the merge clean where the existence case conflicted.

## The branches

- ours retargets `worker --> db` to `worker --> auth`.
- theirs renames `auth` to `identity`: its node statement and `api --> auth`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes line 11; theirs changes lines 5 and 8. Lines 9 and 10 lie unchanged between the nearest hunks. Clean.

## The verdict

The merged file declares `identity`, not `auth`, and ours' `worker --> auth` names `auth`: `undeclared-id` for `auth`. `identity` is declared and named; nothing else applies.

> Under D1 the merged file names an id that no statement declares, and the file is refused.
>
> SPEC.md §1

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["auth"]}}`
