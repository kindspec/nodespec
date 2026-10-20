# boundary/style-colour-hex-accepted

**Expected:** accepted.

**Twin:** `boundary/style-colour-non-hex-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:#abc
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> colour = "#" 1*HEXDIG

§4.1:

> `HEXDIG` is `DIGIT` or `A` to `F` in either case.

## Reasoning

`#abc` is `#` and three `HEXDIG`s.
