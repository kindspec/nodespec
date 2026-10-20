# refusal/malformed-line-head-at-start-only

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
b[B]
a o--> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Mermaid accepts others that are not admitted: `<-.->`, `<==>`, `o-.-o` and `x==x`; and a head at the start only, `o-->`, `x-->` or `<---`, which Mermaid reads without that head. They are `malformed-line`.

## Reasoning

`o-->` is a head at the start only; the `o` form of `link` needs `o` at both ends.

## Other identifiers

- `not-admitted`: Named as `malformed-line`.
