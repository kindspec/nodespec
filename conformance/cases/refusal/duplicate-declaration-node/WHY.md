# refusal/duplicate-declaration-node

**Expected:** refused. Identifiers that apply: `duplicate-declaration` (id `a`).

## Input

````text
flowchart TD
a[A]
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.1:

> An id declared twice as the same kind is refused as `duplicate-declaration`: two node statements for `a`, two subgraph lines for `s`, `e1@` on two links, two `classDef` lines for `c`. This holds however alike the two declarations are.

## Reasoning

Two node statements for `a`, identical. The rule holds however alike they are.

## Other identifiers

- `kind-clash`: Both are of one kind.
- `malformed-line`: Both lines match `node-stmt`.
