# boundary/header-spaced-accepted

**Expected:** accepted.

**Twin:** `boundary/header-unspaced-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/header-capitalised-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

## Reasoning


