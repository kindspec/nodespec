# existence-05-delete-vs-restyle-spaced

A delete of `worker` against a new `style worker` line placed away from the deleted lines: clean, and the `style` line names an undeclared id.

From existence case `05-delete-vs-restyle` (`existence/cases/05-delete-vs-restyle/`). Declarations moved out of the edges; theirs puts its `style` line after the blank line that follows the declarations, rather than at the end, so git merges clean.

## The branches

- ours deletes `worker`: its node statement and `worker --> db`.
- theirs adds `style worker fill:#fdd` between the declarations and the edges.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; `style worker fill:#fdd` names a declared node with a style list of one `name: colour` item. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 6 and 11; theirs inserts after line 7, the blank line, which neither side changes. Clean.

## The verdict

The `style` line names `worker` (a `style` names its target), and the merged file declares no `worker`: `undeclared-id` for `worker`. Nothing else applies.

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "refusal": ["undeclared-id"], "ids": {"undeclared-id": ["worker"]}}`
