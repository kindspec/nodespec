# boundary/duplicate-edge-quoted-label-accepted

**Expected:** accepted.

**Twin:** `boundary/duplicate-edge-label-padding-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a -->|x| b
a -->|"x"| b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> The same link means the same characters (`-->` and `--->` differ); the same label means both have none, or both have one whose text between the `|`s is the same once leading and trailing `WSP` is removed (provisional). Labels are compared as bytes, not as what they render, so `|x|` and `|"x"|` are different labels and those two edges are not duplicates;

## Reasoning

`|x|` and `|"x"|` are different labels.
