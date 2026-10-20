# refusal/reserved-id-underscore-top

**Expected:** refused. Identifiers that apply: `reserved-id` (id `_top`).

## Input

````text
flowchart TD
_top[T]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id is refused as `reserved-id` when it is one of these words, compared exactly:

§4.4:

> end graph flowchart subgraph style class classDef click linkStyle interpolate call href default _self _blank _parent _top

## Reasoning

`_top` is one of the listed words.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`.
