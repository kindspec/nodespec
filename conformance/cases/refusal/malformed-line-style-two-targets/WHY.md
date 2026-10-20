# refusal/malformed-line-style-two-targets

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** One class per `classDef` and per `class` line, and one target per `style` line (§4.8).

## Input

````text
flowchart TD
a[A]
b[B]
style a,b fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> `style a,b …` is `malformed-line`: Mermaid styles a new node named `a,b`.

§4.1:

> style-stmt = *WSP "style" 1*WSP id 1*WSP style-list *WSP

## Reasoning

`style-stmt` has one id before the style list.

## Other identifiers

- `undeclared-id`: The refused line names nothing.
