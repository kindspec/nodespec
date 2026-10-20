# boundary/class-line-without-trailing-wsp-accepted

**Expected:** accepted.

**Twin:** `boundary/class-line-with-trailing-wsp-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
class a c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

## Reasoning


