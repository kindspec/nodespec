# examples/s5-4-base-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
  a[a]
  b[b]
  c[c]
  d[d]
  e[e]
  a --> b
  b --> c
  c --> d
  d --> e
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.4:

> One branch deletes `c`, its node statement and its two edges; the other adds `e --> c` after the last edge. Git merges them without a conflict, and the merged file declares no `c` while `e --> c` names it. It is refused as `undeclared-id` for `c`.

## Reasoning

§5.4's base file. Five node statements, each declaring one id once, and four edges between declared nodes, each distinct. The two-space indentation is the `*WSP` of `node-stmt` and `edge-stmt`.
