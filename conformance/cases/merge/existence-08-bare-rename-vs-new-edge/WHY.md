# existence-08-bare-rename-vs-new-edge

A rename of `b` against a new edge from `b`: the merged file names `b`, which nothing declares.

From existence case `08-bare-rename-vs-new-edge` (`existence/cases/08-bare-rename-vs-new-edge/`). The existence case wrote every node bare, which is `malformed-line` or `undeclared-id` in the profile. Here each node is declared as SPEC.md §5.4 declares them, `a[a]`; the rename rewrites the id in the declaration and its label with it.

## The branches

- ours renames `b` to `x` everywhere: `x[x]`, `a --> x`, `x --> c`.
- theirs adds `b --> e` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each of `a` to `e` is declared once by a node statement (`a[a]`, a rectangle labelled with its id, as 0001 rewrites a bare chart), and each edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes lines 3, 7 and 8; theirs inserts after line 10. Lines 9 and 10 are unchanged between. Clean.

## The verdict

`b --> e` names `b`, and the merged file declares `x`, not `b`: `undeclared-id` for `b`. Mermaid would have drawn a new node `b`; the profile refuses the file instead.

> Under D1 the merged file names an id that no statement declares, and the file is refused.
>
> SPEC.md §1

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["b"]}}`
