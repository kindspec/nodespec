# existence-01-rename-vs-new-edge

A rename against a new edge from the old name: the merged file names `api`, which nothing declares.

From existence case `01-rename-vs-new-edge` (`existence/cases/01-rename-vs-new-edge/`). The existence case declared nodes inside edges (`user[User] --> api[API]`), which is `declaration-in-edge`; here every node has its own node statement and the edges name them. Theirs' new node `cache` needs its own node statement too, so theirs adds a node statement and an edge.

## The branches

- ours renames `api` to `gateway` everywhere: its node statement and its three edges.
- theirs declares a new node `cache[Cache]` and adds `api --> cache` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; in ours `gateway` replaces `api` in every place, and in theirs `cache` is declared. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes lines 3 and 8 to 10; theirs inserts after line 6 and after line 11. No change touches or abuts another, so git takes both.

## The verdict

The merged file declares `gateway` and `cache`, and no statement declares `api`; theirs' edge `api --> cache` names it. That is `undeclared-id` for `api`. Nothing else applies: every other name is declared once, as a node.

> Under D1 the merged file names an id that no statement declares, and the file is refused.
>
> SPEC.md §1

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["api"]}}`
