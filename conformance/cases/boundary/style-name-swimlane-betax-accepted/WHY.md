# boundary/style-name-swimlane-betax-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** Style lists are narrower than Mermaid's (§4.8).

**Twin:** `boundary/style-name-swimlane-beta-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/style-name-swimlane-beta-hyphen-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:swimlane-betax
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`, which Mermaid lexes as a keyword (`swimlane` and `swimlane-x` parse).

§4.1:

> a `unit` is not the one-letter word `v`, so `vh` is a unit; neither a `name` nor the part of it before its first `-` is `v` or one of the 17 words listed in §4.4; a `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`; and the `name` before a `:` is not `accTitle` or `accDescr` (§4.8).

## Reasoning

`swimlane-betax` is not `swimlane-beta` and does not begin with `swimlane-beta-`. The line matches `classdef-stmt`, so it declares the class `c`, which nothing else declares.
