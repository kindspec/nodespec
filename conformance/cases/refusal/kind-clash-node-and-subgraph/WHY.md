# refusal/kind-clash-node-and-subgraph

**Expected:** refused. Identifiers that apply: `kind-clash` (id `cache`).

## Input

````text
flowchart TD
a[A]
cache[Cache]
subgraph cache
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.3:

> One namespace holds every id. An id declared as two kinds is refused as `kind-clash`: a node and a subgraph both named `cache`, a node and an edge id `e1`, a class and a node.

## Reasoning

`cache` is declared as a node and as a subgraph.

## Other identifiers

- `duplicate-declaration`: The two declarations are of different kinds.
- `wrong-kind`: Nothing names `cache`.
