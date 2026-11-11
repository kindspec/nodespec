# subgraph-replaced-by-node-vs-member-line-accepted

§11 across kinds, the reverse: one branch replaces the subgraph `cache` with a node `cache`; the other's new member line, meant to nest the subgraph, holds the node.

## The branches

- ours deletes the block `cache` and the blank line before it, and declares a node `cache[Cache]`.
- theirs nests the subgraph `cache` in `backend` by adding the member line `cache`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each id is declared once; member lines name declared nodes or, in theirs, the declared subgraph `cache`; no id has two holders and there is no cycle. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 4 and deletes lines 13 to 16; theirs inserts after line 11. Line 12 is unchanged between. Clean.

## The verdict

`cache` is declared once, as a node, and a member line may name a node. Accepted.

> The same holds across kinds (the owner, 2026-10-19): one branch replaces the node `x` with a subgraph `x`, or the reverse, and the other adds an edge to `x` or a member line naming `x`. The merged file declares `x` once, as the new kind, and the other branch's edge or member line silently lands on it, since an edge may end at either kind and a member line may name either.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
