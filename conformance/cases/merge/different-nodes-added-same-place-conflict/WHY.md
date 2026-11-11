# different-nodes-added-same-place-conflict

Both branches add a different node statement at the same place.

## The branches

- ours declares `cache[Cache]` after `worker[Worker]`.
- theirs declares `queue[Queue]` at the same place.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Different insertions at the same place: conflict, though the two nodes are unrelated.

## The verdict

A conflict carries no verdict: git stopped.

> A merge is checked by checking its result.
>
> SPEC.md §8

Expected: `{"merge": "conflict"}`
