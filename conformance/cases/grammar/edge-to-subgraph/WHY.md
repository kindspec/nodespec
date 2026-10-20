# grammar/edge-to-subgraph

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s [Group]
  a
end
b --> s
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> An edge may end at a subgraph (the owner, 2026-10-19).

§5.2:

> | edge statement | each id of its groups | node or subgraph |

## Reasoning

An edge's ends may be nodes or subgraphs. `s` is declared by its subgraph line, so `b --> s` names a declared id of a kind that place may name.
