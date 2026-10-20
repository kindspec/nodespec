# boundary/wsp-around-link-accepted

**Expected:** accepted.

**Twin:** `boundary/wsp-missing-after-link-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/wsp-no-break-space-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Links and `&` have `WSP` on both sides: Mermaid also reads `a-->b`, but without the spaces `A---oB` is a circle-headed link to `B` and `a&b` is one node.

## Reasoning

`WSP` on both sides of the link.
