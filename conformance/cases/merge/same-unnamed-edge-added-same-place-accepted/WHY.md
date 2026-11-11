# same-unnamed-edge-added-same-place-accepted

§11: both branches add the identical unnamed edge at the same place; git keeps one.

## The branches

- ours relabels `user` and appends `worker --> auth`.
- theirs appends the identical `worker --> auth`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

The appended lines are identical insertions at the same place, kept once; ours' relabel is on line 2. Clean.

## The verdict

`worker --> auth` appears once. Contrast `unnamed-edge-added-twice-in-two-places`. Accepted.

> The same declaration added on both branches at the same place. Git keeps one line, so two authors' identical `cache[Cache]` are one node, with both branches' edges. The same is true of an identical unnamed edge added at the same place.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
