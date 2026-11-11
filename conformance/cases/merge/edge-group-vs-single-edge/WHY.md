# edge-group-vs-single-edge

One branch adds `user & worker --> auth`, the other `worker --> auth`: the group already makes the edge from `worker`.

## The branches

- ours adds `user & worker --> auth` after `user --> api`: two edges.
- theirs adds `worker --> auth` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; ours' group has `WSP` around `&` and carries no edge id. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11. Clean.

## The verdict

The group makes `user --> auth` and `worker --> auth`; theirs' line makes `worker --> auth` again. Two unnamed edges with the same ends, link and label: `duplicate-edge`.

> Each link makes one edge from every id of the group before it to every id of the group after it, in that order: `a & b --> c & d` makes four edges, and `a --> b --> c` makes two.
>
> SPEC.md §4.6

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge`
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["duplicate-edge"]}`
