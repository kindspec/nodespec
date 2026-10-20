# refusal/duplicate-declaration-edge-id

**Expected:** refused. Identifiers that apply: `duplicate-declaration` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
a e1@--> b
b e1@--> a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.1:

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.

§5.1:

> | `id@` before a link in an edge statement | edge |

## Reasoning

`e1@` on two links.

## Other identifiers

- `duplicate-edge`: That rule is about edges without edge ids.
