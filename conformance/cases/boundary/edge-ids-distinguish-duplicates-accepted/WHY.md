# boundary/edge-ids-distinguish-duplicates-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
a e1@--> b
a e2@--> b
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

## Reasoning

Only edges without edge ids are compared; one of the three a→b edges has none.
