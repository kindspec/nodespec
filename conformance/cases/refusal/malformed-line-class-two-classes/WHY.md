# refusal/malformed-line-class-two-classes

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
classDef c1 fill:#f9f
classDef c2 stroke:#333
class a c1,c2
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> `class a c1,c2` is `malformed-line`: Mermaid gives `a` one class named `c1,c2`.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

## Reasoning

`class-stmt` has one id after the last `1*WSP`; `c1,c2` is two.

## Other identifiers

- `class-not-last`: It is the last line; and a refused line is not a `class` line for any later rule.
