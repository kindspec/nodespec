# boundary/stray-direction-word-continues-accepted

**Expected:** accepted.

**Twin:** `boundary/stray-direction-line-ends-in-direction-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:directionx
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> with trailing whitespace removed, it ends in `direction`.

§4.8:

> Neither a `name` nor its part before its first `-` is `v` or one of the 17 words listed in §4.4; the other reserved ids, such as `hasOwnProperty` and `direction`, parse as style words (`fill:hasOwnProperty`, `fill:direction-x`).

## Reasoning

The line ends in `directionx`, not `direction`.
