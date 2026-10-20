# refusal/duplicate-edge-repeated-id-in-group

**Expected:** refused. Identifiers that apply: `duplicate-edge`.

## Input

````text
flowchart TD
a[A]
b[B]
a & a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Each link makes one edge from every id of the group before it to every id of the group after it, in that order: `a & b --> c & d` makes four edges, and `a --> b --> c` makes two. The edges of a file are a list, not a set: `a & a --> b` makes two edges from `a` to `b`, and Mermaid keeps both.

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

## Reasoning

§4.6's own example: `a & a --> b` makes two edges from `a` to `b`, with no edge ids, the same link and no label.

## Other identifiers

- `malformed-line`: The line matches `edge-stmt`.
