# refusal/malformed-line-classdef-two-classes

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** One class per `classDef` and per `class` line, and one target per `style` line (§4.8).

## Input

````text
flowchart TD
a[A]
classDef c1,c2 fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> One statement, one class, one style target (provisional):

§4.8:

> `classDef c1,c2 …`, which Mermaid reads as two classes, is `malformed-line`; each class has its own `classDef` line.

§4.1:

> classdef-stmt = *WSP "classDef" 1*WSP id 1*WSP style-list *WSP

## Reasoning

`classdef-stmt` takes one id before the style list.

## Other identifiers

- `duplicate-declaration`: The refused line declares nothing.
