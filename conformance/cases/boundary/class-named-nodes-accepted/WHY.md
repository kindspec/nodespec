# boundary/class-named-nodes-accepted

**Expected:** accepted.

**Twin:** `boundary/class-named-node-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
node[N]
classDef nodes fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `node` remains an id for a node, a subgraph or an edge.

§4.4:

> A class may not be `node`: a `classDef` or `class` naming the class `node` is refused as `reserved-id`.

## Reasoning

`node` remains an id for a node, and a class named `nodes` is not a class named `node`.
