# different-styles-same-place-conflict

Both branches append a `style` line for `api`, with different fills, at the same place.

## The branches

- ours appends `style api fill:#f00`.
- theirs appends `style api fill:#0f0`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Different insertions at the same place: conflict. `style-added-on-both-branches` places them apart and is refused as `styled-twice` instead.

## The verdict

A conflict carries no verdict: git stopped, which is loud.

> A merge is checked by checking its result.
>
> SPEC.md §8

Expected: `{"merge": "conflict"}`
