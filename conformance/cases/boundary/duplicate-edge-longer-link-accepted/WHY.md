# boundary/duplicate-edge-longer-link-accepted

**Expected:** accepted.

**Twin:** `boundary/duplicate-edge-same-link-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a --> b
a ---> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

§4.6:

> The same link means the same characters (`-->` and `--->` differ); the same label means both have none, or both have one whose text between the `|`s is the same once leading and trailing `WSP` is removed (provisional). Labels are compared as bytes, not as what they render, so `|x|` and `|"x"|` are different labels and those two edges are not duplicates;

## Reasoning

`-->` and `--->` differ.
