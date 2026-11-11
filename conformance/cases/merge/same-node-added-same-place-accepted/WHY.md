# same-node-added-same-place-accepted

§11: both branches add the identical `cache[Cache]` at the same place, each with its own edge.

## The branches

- ours declares `cache[Cache]` after `worker[Worker]` and adds `api --> cache` after `user --> api`.
- theirs declares the identical `cache[Cache]` at the same place and adds `worker --> cache` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

The two node statements are identical insertions at the same place, kept once; the edges go in after lines 8 and 11. Clean.

## The verdict

One node statement for `cache`, named by both edges. Accepted.

> The same declaration added on both branches at the same place. Git keeps one line, so two authors' identical `cache[Cache]` are one node, with both branches' edges. The same is true of an identical unnamed edge added at the same place.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
