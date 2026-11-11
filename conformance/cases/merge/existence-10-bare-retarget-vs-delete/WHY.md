# existence-10-bare-retarget-vs-delete

A retarget to `e` against a delete of `e`, with a blank line between declarations and edges: the merged edge names `e`, which nothing declares.

From existence case `10-bare-retarget-vs-delete` (`existence/cases/10-bare-retarget-vs-delete/`). Each node is declared as in §5.4, and a blank line separates the declarations from the edges. Without it, deleting `e[e]` abuts the retargeted first edge and git conflicts (`existence-10-bare-retarget-vs-delete-adjacent-conflict`).

## The branches

- ours retargets `a --> b` to `a --> e`.
- theirs deletes `e`: its node statement and `d --> e`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes; a blank line is allowed anywhere. Any refusal of the merged file is one the merge produced.

## The merge

Theirs deletes lines 6 and 11; ours changes line 8. The blank line 7 is unchanged between them, and lines 9 and 10 between ours' change and theirs' second deletion. Clean.

## The verdict

Ours' `a --> e` names `e`, and theirs removed its only declaration: `undeclared-id` for `e`. `b` is still declared, now with only `b --> c`; that is not a refusal.

> Under D1 the merged file names an id that no statement declares, and the file is refused.
>
> SPEC.md §1

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["e"]}}`
