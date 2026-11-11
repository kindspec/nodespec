# unnamed-edge-moved-on-one-branch-accepted

Control for `unnamed-edge-moved-on-both-branches`: only ours moves the edge; theirs relabels a node.

## The branches

- ours moves `api --> db` up, after `user --> api`, as in the refused case.
- theirs relabels `worker` and leaves the edge where it is.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once; every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Theirs changes line 6; ours deletes line 11 and inserts after line 8. Clean.

## The verdict

The edge appears once. Labels are not identity. Accepted.

> Labels are not identity. The rules in §5 to §7 never read a label.
>
> SPEC.md §4.5

Expected: `{"merge": "clean", "accept": true}`
