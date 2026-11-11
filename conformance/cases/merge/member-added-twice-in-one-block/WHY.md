# member-added-twice-in-one-block

Both branches add the member line `a` to the same block, at different places.

## The branches

- ours adds `a` at the top of block `s`.
- theirs adds `a` at the bottom of block `s`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each node is named by at most one member line on each side. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 10. Clean.

## The verdict

`a` is named by two member lines in one block: `member-twice` for `a`, which §6 refuses in one block as well as in two.

> A node or a subgraph has at most one holder. An id named by more than one member line is refused as `member-twice`. Where the two lines are in two blocks, that is D3. Where both are in one block, it is refused as well: the two lines say the same thing, and a later edit that deletes one leaves the other.
>
> SPEC.md §6

Expected: `{"merge": "clean", "refusal": ["member-twice"], "ids": {"member-twice": ["a"]}}`
