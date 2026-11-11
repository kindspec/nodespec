# node-moved-into-two-blocks

Each branch moves node `a` into a different block: two holders.

## The branches

- ours adds the member line `a` to block `s`.
- theirs adds the member line `a` to block `t`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: each node has at most one holder on each side; member lines name declared nodes. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 9, theirs after line 13. Clean.

## The verdict

`a` is named by two member lines, in two blocks: `member-twice` for `a`.

> A node or a subgraph has at most one holder. An id named by more than one member line is refused as `member-twice`. Where the two lines are in two blocks, that is D3. Where both are in one block, it is refused as well: the two lines say the same thing, and a later edit that deletes one leaves the other.
>
> SPEC.md §6

Expected: `{"merge": "clean", "refusal": ["member-twice"], "ids": {"member-twice": ["a"]}}`
