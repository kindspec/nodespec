# grammar/class-node-as-target

**Expected:** accepted.

## Input

````text
flowchart TD
node[N]
classDef c fill:#f9f
class node c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> A class may not be `node`: a `classDef` or `class` naming the class `node` is refused as `reserved-id`.

§4.4:

> `node` remains an id for a node, a subgraph or an edge.

§5.2:

> A `class` statement's targets are the ids before its last one.

## Reasoning

Only a class named `node` is refused. Here `node` is a target, a declared node, and the class is `c`.
