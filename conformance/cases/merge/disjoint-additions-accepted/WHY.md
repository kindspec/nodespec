# disjoint-additions-accepted

Each branch adds a node and an edge to it, in different places.

## The branches

- ours declares `cache[Cache]` after `api[API]` and adds `api --> cache` after `user --> api`.
- theirs declares `queue([Queue])` after `worker[Worker]` and adds `worker --> queue` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Four insertions at four places. Clean.

## The verdict

Every id is declared once; every edge names a declared node; no edge repeats. Accepted.

> D1. Every id is declared exactly once, and everything else only names it.
>
> SPEC.md §5.1

Expected: `{"merge": "clean", "accept": true}`
