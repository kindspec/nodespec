# edges-added-past-500

A base of 499 edges; each branch adds one, reaching 500; the merged file has 501.

## The branches

- base declares nodes `n0` to `n39` and has 499 edges, `n{i} --> n{j}` for distinct pairs i < j, in order.
- ours adds the 500th pair's edge, `n15 --> n35`, at the top of the edges; theirs adds the 501st pair's edge, `n15 --> n36`, at the end.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: ours and theirs make 500 edges each, which is not more than 500; every edge names declared nodes and no two edges share their ends. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 42, the blank line; theirs appends after the last line. Clean.

## The verdict

The merged file's statements make 501 edges: `too-many-edges`. Every id is declared and no edge repeats, so nothing else applies.

> A file whose statements make more than 500 edges is refused as `too-many-edges` (the owner, 2026-10-19). Mermaid's default configuration accepts 500 edges and refuses 501 ("Edge limit exceeded")
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "refusal": ["too-many-edges"]}`
