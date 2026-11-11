# classdef-added-twice-same-place-accepted

Control for `classdef-added-twice`: the identical `classDef` added at the same place is one line.

## The branches

- ours appends `classDef warm fill:#fd0`.
- theirs appends the identical line.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Identical insertions at the same place; git keeps one.

## The verdict

One `classDef` for `warm`. A class need not be used. Accepted; §11's same-place residual.

> The same declaration added on both branches at the same place. Git keeps one line, so two authors' identical `cache[Cache]` are one node, with both branches' edges. The same is true of an identical unnamed edge added at the same place.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
