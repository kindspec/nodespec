# refusal/edge-id-on-group

**Expected:** refused. Identifiers that apply: `edge-id-on-group` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
a & b e1@--> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge id is declared by the one edge that carries it (D1). So an edge id is allowed only on a link with one id on each side. An edge id on a link with `&` in the group before it or after it is refused as `edge-id-on-group`.

## Reasoning

`e1@` is on a link whose group before it holds `&`.

## Other identifiers

- `malformed-line`: The line matches `edge-stmt`.
- `undeclared-id`: Nothing names `e1`.
