# boundary/link-invisible-shortest-accepted

**Expected:** accepted.

**Twin:** `boundary/link-invisible-too-short-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a ~~~ b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> link = 2*"-" ">" / 3*"-" / 2*"-" "o" / 2*"-" "x" / "<" 2*"-" ">" / "o" 2*"-" "o" / "x" 2*"-" "x" / "-" 1*"." "->" / "-" 1*"." "-" / 2*"=" ">" / 3*"=" / 3*"~"

## Reasoning

`~~~` is the shortest form of its `link` alternative.
