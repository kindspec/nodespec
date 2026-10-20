# boundary/wsp-missing-before-ampersand-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Links and `&` have `WSP` on both sides, and only the spike's links are admitted (§4.6).

**Twin:** `boundary/wsp-around-ampersand-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
a& b --> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Links and `&` have `WSP` on both sides (provisional): Mermaid also reads `a-->b`, but without the spaces `A---oB` is a circle-headed link to `B` and `a&b` is one node.

§4.1:

> group = id *( 1*WSP "&" 1*WSP id )

## Reasoning

`group` needs `1*WSP` before `&`; `a&` is neither an id nor an id and `WSP`.

## Other identifiers

- `undeclared-id`: The refused line names nothing.
