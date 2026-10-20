# refusal/edge-id-on-group-after-the-link

**Expected:** refused. Identifiers that apply: `edge-id-on-group` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
a e1@--> b & c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge id is declared by the one edge that carries it (D1). So an edge id is allowed only on a link with one id on each side. An edge id on a link with `&` in the group before it or after it is refused as `edge-id-on-group`.

§4.6:

> `edge-id-on-group` applies only to a line that §4.3 classifies as an edge statement (rule 8, at the top level). A line refused as `declaration-in-edge` or `statement-in-block` is not also `edge-id-on-group`, since §4.2 reads a classified line as nothing else.

## Reasoning

The group after the link holds `&`; the rule covers `&` in the group before it or after it. The line matches `edge-stmt` at the top level, so rule 8 classifies it.

## Other identifiers

- `malformed-line`: The line matches `edge-stmt`.
- `undeclared-id`: Nothing names `e1`.
