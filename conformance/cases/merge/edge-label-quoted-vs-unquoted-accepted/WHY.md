# edge-label-quoted-vs-unquoted-accepted

Control for `edge-label-padding-added-twice`: `|retry|` and `|"retry"|` are different labels, so the two edges are not duplicates.

## The branches

- ours adds `worker -->|retry| api` after `user --> api`.
- theirs adds `worker -->|"retry"| api` after the last edge.

`base.mmd`, `ours.mmd` and `theirs.mmd` are each in the profile: every node is declared once by a top-level node statement, and every edge names declared nodes and appears once; theirs' quoted label holds non-`WSP` text, does not begin with a backtick and does not end with `=`. Any refusal of the merged file is one the merge produced.

## The merge

Ours inserts after line 8, theirs after line 11. Clean.

## The verdict

Labels compare as bytes: `retry` and `"retry"` differ, so the two edges are not duplicates. Every name is declared. Accepted, deliberately.

> Labels are compared as bytes, not as what they render, so `|x|` and `|"x"|` are different labels and those two edges are not duplicates
>
> SPEC.md §4.6

Expected: `{"merge": "clean", "accept": true}`
