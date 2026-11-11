# existence-05-delete-vs-restyle-adjacent-conflict

A delete of `worker` against a new `style worker` line appended after the deleted edge: git conflicts, as in the existence case.

From existence case `05-delete-vs-restyle` (`existence/cases/05-delete-vs-restyle/`). Declarations moved out of the edges, keeping `worker --> db` last, so theirs' appended `style` line abuts ours' deletion as in the existence case.

## The branches

- ours deletes `worker`: its node statement and `worker --> db`, the last line.
- theirs appends `style worker fill:#fdd`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; theirs' `style` line names the declared node `worker`. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes the last line and theirs appends after it: the two hunks abut at the end of the file, and git conflicts. `existence-05-delete-vs-restyle-spaced` places the `style` line elsewhere.

## The verdict

A conflict carries no verdict: git stopped, which is loud.

> A merge is checked by checking its result.
>
> SPEC.md §8

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.
>
> SPEC.md §4.2

Expected: `{"merge": "conflict"}`
