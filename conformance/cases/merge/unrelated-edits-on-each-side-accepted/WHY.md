# unrelated-edits-on-each-side-accepted

Ours relabels one node, theirs changes another node's shape and an edge's link.

## The branches

- ours relabels `user` to `Customer`.
- theirs makes `worker` a stadium and its edge thick.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Ours changes line 2; theirs changes lines 6 and 11. Clean.

## The verdict

Same ids, same declarations, one edge each. Labels, shapes and links are not identity. Accepted.

> Labels are not identity. The rules in §5 to §7 never read a label.
>
> SPEC.md §4.5

Expected: `{"merge": "clean", "accept": true}`
