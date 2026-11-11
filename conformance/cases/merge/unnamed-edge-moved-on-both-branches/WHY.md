# unnamed-edge-moved-on-both-branches

Both branches move the edge `api --> db`, to different places: git keeps both moved copies.

## The branches

- ours moves `api --> db` up, after `user --> api`.
- theirs moves `api --> db` down, after `worker --> db`.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once; every edge names declared nodes and appears once; blank lines are allowed anywhere. Any refusal of the merged file is one the merge produced.

## The merge

Both sides delete line 11 identically. Ours inserts after line 8, theirs after line 13. Clean, with the edge at both new places.

## The verdict

The merged file holds `api --> db` twice: `duplicate-edge`.

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge`
>
> SPEC.md §4.6

> Where both branches move the same unnamed edge, or both add it in different places, the merged file holds it twice and is refused as `duplicate-edge` (§4.6).
>
> SPEC.md §11

Expected: `{"merge": "clean", "refusal": ["duplicate-edge"]}`
