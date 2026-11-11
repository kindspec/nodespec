# node-id-reused-for-new-node-accepted

§11: one branch deletes `cache` and declares a different node `cache`; the other's new edge lands on the new node.

## The branches

- ours deletes `cache[Cache]` and its edge `api --> cache`, and declares a new node `cache[(Redis)]` after `worker[Worker]`.
- theirs adds `worker --> cache` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each id is declared once as a node; every edge names declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours deletes lines 3 and 7 and inserts after line 5; theirs appends after line 9. Clean.

## The verdict

`cache` is declared once, by ours' new node statement, and theirs' edge names it. Accepted: the id is the node's identity.

> An id reused for a new meaning. One branch deletes `cache` and declares a different node named `cache`; the other branch's new edge to `cache` lands on the new node. The id is the node's identity, so reusing it says it is the same node.
>
> SPEC.md §11

Expected: `{"merge": "clean", "accept": true}`
