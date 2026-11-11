# relabel-vs-new-edge-accepted

One branch relabels `api`, the other adds an edge to `api`: labels are not identity.

## The branches

- ours relabels `api` to `Gateway`.
- theirs adds `worker --> api` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes line 3; theirs appends after line 11. Clean.

## The verdict

`api` is declared once and named by the new edge. Accepted.

> Labels are not identity. The rules in §5 to §7 never read a label.
>
> SPEC.md §4.5

Expected: `{"merge": "clean", "accept": true}`
