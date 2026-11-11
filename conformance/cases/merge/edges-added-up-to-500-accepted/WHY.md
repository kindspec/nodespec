# edges-added-up-to-500-accepted

Control for `edges-added-past-500`: a base of 498 edges, each branch adding one, gives exactly 500.

## The branches

- base declares `n0` to `n39` with 498 edges, as in the refused case less one.
- ours adds `n15 --> n34` at the top of the edges; theirs adds `n15 --> n35` at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: 499 edges in each of ours and theirs; every edge names declared nodes; no two edges share their ends. Any refusal of the merged file is one the merge produced.

## The merge

As in the refused case. Clean.

## The verdict

500 edges, which is not more than 500. Accepted.

> A file whose statements make more than 500 edges is refused as `too-many-edges` (the owner, 2026-10-19). Mermaid's default configuration accepts 500 edges and refuses 501 ("Edge limit exceeded")
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "accept": true}`
