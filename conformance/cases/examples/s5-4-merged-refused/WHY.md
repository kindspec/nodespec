# examples/s5-4-merged-refused

**Expected:** refused. Identifiers that apply: `undeclared-id` (id `c`).

## Input

````text
flowchart TD
  a[a]
  b[b]
  d[d]
  e[e]
  a --> b
  d --> e
  e --> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.4:

> One branch deletes `c`, its node statement and its two edges; the other adds `e --> c` after the last edge. Git merges them without a conflict, and the merged file declares no `c` while `e --> c` names it. It is refused as `undeclared-id` for `c`.

## Reasoning

The merged file of §5.4. This file is the merge as §5.4 describes it: the base without `c[c]`, `b --> c` and `c --> d`, with `e --> c` after the last edge. `e --> c` names `c`, and no statement declares it. The bytes are this suite's rendering of the prose; §5.4 does not print the merged file.

## Other identifiers

- `wrong-kind`: `c` is not declared.
