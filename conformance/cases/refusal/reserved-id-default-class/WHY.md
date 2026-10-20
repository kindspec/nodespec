# refusal/reserved-id-default-class

**Expected:** refused. Identifiers that apply: `reserved-id` (id `default`).

## Input

````text
flowchart TD
a[A]
classDef default fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `default` is among them, so `classDef default`, Mermaid's class for every node, is refused.

§4.4:

> end graph flowchart subgraph style class classDef click linkStyle interpolate call href default _self _blank _parent _top

## Reasoning

`classDef default` is named as refused.

## Other identifiers

- `malformed-line`: The line matches `classdef-stmt`.
- `undeclared-id`: Nothing names `default`.
