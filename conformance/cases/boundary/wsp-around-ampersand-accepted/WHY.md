# boundary/wsp-around-ampersand-accepted

**Expected:** accepted.

**Twin:** `boundary/wsp-missing-after-ampersand-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/wsp-missing-before-ampersand-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
a & b --> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Links and `&` have `WSP` on both sides: Mermaid also reads `a-->b`, but without the spaces `A---oB` is a circle-headed link to `B` and `a&b` is one node.

§4.1:

> group = id *( 1*WSP "&" 1*WSP id )

## Reasoning

`WSP` on both sides of `&`.
