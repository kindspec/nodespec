# same-direction-added-in-two-places

Both branches add `direction TB` to the same block, at different places: two direction statements, though they agree.

## The branches

- ours adds `direction TB` at the top of block `s`.
- theirs adds `direction TB` at the bottom of block `s`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each side's block holds one direction statement and member lines naming declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11. Clean.

## The verdict

The rule counts direction statements, not their values: the second is `direction-twice`.

> A block holds at most one direction statement: every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included. Mermaid keeps the last, so two branches that each add one merge clean and one of them is lost.
>
> SPEC.md §4.9

Expected: `{"merge": "clean", "refusal": ["direction-twice"]}`
