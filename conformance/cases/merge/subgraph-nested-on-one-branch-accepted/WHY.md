# subgraph-nested-on-one-branch-accepted

Control for `subgraphs-nested-each-in-the-other`: ours nests `t` in `s`; theirs relabels a node.

## The branches

- ours adds the member line `t` to block `s`, as in the refused case.
- theirs relabels `b`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: nodes declared once; `t` is nested once, in `s`. Any refusal of the merged file is one the merge produced.

## The merge

Theirs changes line 3; ours inserts after line 7. Clean.

## The verdict

`s` holds `a` and `t`; `t` holds `b`; no cycle. Accepted.

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph.
>
> SPEC.md §6

Expected: `{"merge": "clean", "accept": true}`
