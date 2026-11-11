# unnamed-edge-added-twice-in-two-places

Both branches add `worker --> auth`, in different places: one unnamed edge written twice.

## The branches

- ours adds `worker --> auth` after `user --> api`.
- theirs adds the same edge after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11. Clean; the line is kept at both places.

## The verdict

Two edges without edge ids, same start, end, link and label (none): `duplicate-edge`, which carries no id.

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge`
>
> SPEC.md §4.6

> An unnamed edge has no identity but its ends, link and label, so two of them are one edge written twice: both branches adding it in different places, or both moving it, then merge loud instead of drawing it twice.
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["duplicate-edge"]}`
