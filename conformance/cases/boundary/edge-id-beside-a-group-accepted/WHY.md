# boundary/edge-id-beside-a-group-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** An edge id on a link with `&` on either side is refused (§4.6).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
d[D]
a & b --> c e1@--> d
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge id is declared by the one edge that carries it (D1). So an edge id is allowed only on a link with one id on each side. An edge id on a link with `&` in the group before it or after it is refused as `edge-id-on-group` (provisional).

## Reasoning

`e1@` is on the link between `c` and `d`, one id each; the `&` is in the group before the other link. Contrast `refusal/edge-id-on-group`.
