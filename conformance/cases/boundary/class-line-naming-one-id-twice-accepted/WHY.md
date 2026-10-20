# boundary/class-line-naming-one-id-twice-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** An id is the target of at most one `style` line and one `class` line, so with one class per `class` line an id carries at most one class (§7).

## Input

````text
flowchart TD
a[A]
classDef c stroke:#333
class a,a c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> An id is the target of at most one `style` line and at most one `class` line (provisional). A second is refused as `styled-twice`.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

## Reasoning

`a` is the target of one `class` line; the limit counts lines ("at most one `class` line").
