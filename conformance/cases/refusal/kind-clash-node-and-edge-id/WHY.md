# refusal/kind-clash-node-and-edge-id

**Expected:** refused. Identifiers that apply: `kind-clash` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
e1[E]
a e1@--> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.3:

> One namespace holds every id. An id declared as two kinds is refused as `kind-clash`: a node and a subgraph both named `cache`, a node and an edge id `e1`, a class and a node.

## Reasoning

`e1` is declared as a node and as an edge.

## Other identifiers

- `duplicate-declaration`: The two declarations are of different kinds.
- `wrong-kind`: Nothing names `e1`.
