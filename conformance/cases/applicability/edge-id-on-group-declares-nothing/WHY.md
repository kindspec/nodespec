# applicability/edge-id-on-group-declares-nothing

**Expected:** refused. Identifiers that apply: `edge-id-on-group` (id `e1`); `undeclared-id` (id `e1`).

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
a & b e1@--> c
classDef hot stroke:#f00
class e1 hot
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge id is declared by the one edge that carries it (D1). So an edge id is allowed only on a link with one id on each side. An edge id on a link with `&` in the group before it or after it is refused as `edge-id-on-group` (provisional).

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

The refused edge declares no `e1`, so `class e1 hot` names an undeclared id.

## Other identifiers

- `class-not-last`: The `class` line is last.
- `wrong-kind`: `e1` is undeclared, and `wrong-kind` needs a declaration.
