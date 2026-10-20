# refusal/malformed-line-link-not-admitted

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Links and `&` have `WSP` on both sides, and only the spike's links are admitted (§4.6).

## Input

````text
flowchart TD
a[A]
b[B]
a <==> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Mermaid accepts others that are not admitted (provisional): `<-.->`, `<==>`, `o-.-o` and `x==x`; and a head at the start only, `o-->`, `x-->` or `<---`, which Mermaid reads without that head. They are `malformed-line`.

§4.1:

> link = 2*"-" ">" / 3*"-" / 2*"-" "o" / 2*"-" "x" / "<" 2*"-" ">" / "o" 2*"-" "o" / "x" 2*"-" "x" / "-" 1*"." "->" / "-" 1*"." "-" / 2*"=" ">" / 3*"=" / 3*"~"

## Reasoning

`<==>` is none of the `link` alternatives (the `<` form takes only `-`). §4.6 names it `malformed-line`.

## Other identifiers

- `not-admitted`: §4.10 sends "the other links" to `malformed-line`.
