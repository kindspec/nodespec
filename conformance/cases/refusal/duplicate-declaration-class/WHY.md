# refusal/duplicate-declaration-class

**Expected:** refused. Identifiers that apply: `duplicate-declaration` (id `c`).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
classDef c stroke:#333
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.1:

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.

§5.1:

> | a `classDef` line | class |

## Reasoning

Two `classDef` lines for `c`.

## Other identifiers

- `kind-clash`: Both declarations are classes.
- `malformed-line`: Both lines match `classdef-stmt`.
