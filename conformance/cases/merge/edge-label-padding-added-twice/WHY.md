# edge-label-padding-added-twice

Both branches add the labelled edge `worker --> api`, one as `|retry|`, one as `| retry |`: the same label once `WSP` is trimmed.

## The branches

- ours adds `worker -->|retry| api` after `user --> api`.
- theirs adds `worker -->| retry | api` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; both labels are unquoted labels: leading `WSP` is allowed before the first character and a space is a label character. Any refusal of the merged file is one the merge produced.

## The merge

Different lines at different places; ours inserts after line 8, theirs after line 11. Clean.

## The verdict

Same start, end and link, and labels whose text is `retry` once leading and trailing `WSP` is removed: `duplicate-edge`.

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge`
>
> SPEC.md §4.6

> the same label means both have none, or both have one whose text between the `|`s is the same once leading and trailing `WSP` is removed.
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["duplicate-edge"]}`
