# node-replaced-by-subgraph-vs-new-edge-accepted

§11 across kinds: one branch replaces the node `cache` with a subgraph `cache`; the other's new edge ends at the subgraph.

## The branches

- ours deletes the node statement `cache[Cache]`, declares `redis[(Redis)]`, and adds a block `subgraph cache [Cache tier]` holding `redis`; the edge `api --> cache` now ends at the subgraph.
- theirs adds `worker --> cache` before `worker --> db`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each id is declared once; ours' edges end at a node or at the subgraph `cache`, which an edge may. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes line 3, inserts after line 5 and appends after line 9; theirs inserts after line 8. Clean.

## The verdict

`cache` is declared once, as a subgraph, and both edges may end at a subgraph. Accepted: the profile cannot tell this from a deliberate edit.

> The same holds across kinds (the owner, 2026-10-19): one branch replaces the node `x` with a subgraph `x`, or the reverse, and the other adds an edge to `x` or a member line naming `x`. The merged file declares `x` once, as the new kind, and the other branch's edge or member line silently lands on it, since an edge may end at either kind and a member line may name either.
>
> SPEC.md §11

> An edge may end at a subgraph (the owner, 2026-10-19).
>
> SPEC.md §5.2

Expected: `{"merge": "clean", "accept": true}`
