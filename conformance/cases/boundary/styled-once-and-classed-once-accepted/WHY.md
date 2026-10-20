# boundary/styled-once-and-classed-once-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
style a fill:#f9f
classDef c stroke:#333
class a c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> An id is the target of at most one `style` line and at most one `class` line. A second is refused as `styled-twice`.

## Reasoning

One `style` line and one `class` line for `a`.
