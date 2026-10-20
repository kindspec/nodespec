# refusal/reserved-id-named-in-edge

**Expected:** refused. Identifiers that apply: `reserved-id` (id `end`).

## Input

````text
flowchart TD
a[A]
a --> end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id is refused as `reserved-id` when it is one of these words, compared exactly:

§4.4:

> end graph flowchart subgraph style class classDef click linkStyle interpolate call href default _self _blank _parent _top

§4.4:

> `reserved-id` applies wherever an id stands in a line that §4.3 classifies as a statement and refuses for nothing else: in a declaration and wherever it is named. A reserved word in a line that is refused for another reason, such as a bare `graph` at the top level (`malformed-line`), is not also `reserved-id` (§9).

## Reasoning

`a --> end` matches `edge-stmt` at the top level, and `end` is an id there. Nothing else refuses the line, so `end` is `reserved-id`.

## Other identifiers

- `undeclared-id`: The refused line names nothing (§9).
- `unbalanced-block`: The first word is `a`, not `end`.
