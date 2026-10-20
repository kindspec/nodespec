# refusal/duplicate-declaration-subgraph

**Expected:** refused. Identifiers that apply: `duplicate-declaration` (id `s`).

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s
  a
end
subgraph s
  b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.1:

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.

§5.1:

> | a subgraph line | subgraph |

## Reasoning

Two subgraph lines for `s`.

## Other identifiers

- `member-twice`: `a` and `b` are each on one member line.
