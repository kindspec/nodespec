# same-direction-added-same-place-accepted

Control for `same-direction-added-in-two-places`: the identical line at the same place is kept once.

## The branches

- ours adds `direction TB` at the top of block `s`.
- theirs makes the same insertion.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: the block holds one direction statement and member lines naming declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Identical insertions at the same place; git keeps one.

## The verdict

One direction statement in the block. Accepted.

> A block holds at most one direction statement: every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included. Mermaid keeps the last, so two branches that each add one merge clean and one of them is lost.
>
> SPEC.md §4.9

Expected: `{"merge": "clean", "accept": true}`
