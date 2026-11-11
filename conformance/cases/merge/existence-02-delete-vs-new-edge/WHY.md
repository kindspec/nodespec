# existence-02-delete-vs-new-edge

A delete against a new edge to the deleted node: the merged file names `auth`, which nothing declares.

From existence case `02-delete-vs-new-edge` (`existence/cases/02-delete-vs-new-edge/`). The existence case declared nodes inside edges; here each node has its own node statement.

## The branches

- ours deletes `auth`: its node statement and the edge `api --> auth`.
- theirs adds `worker --> auth` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; ours removes `auth` with every statement naming it, and theirs' new edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 5 and 10; theirs inserts after line 11, with the unchanged line 11 between the hunks. Clean.

## The verdict

`worker --> auth` names `auth`, and the merged file has no declaration of it: `undeclared-id` for `auth`, and nothing else.

> Under D1 the merged file names an id that no statement declares, and the file is refused.
>
> SPEC.md §1

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["auth"]}}`
