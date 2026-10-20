# boundary/style-word-keyword-glued-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** Style lists are narrower than Mermaid's (§4.8).

**Twin:** `boundary/style-word-keyword-hyphen-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:classx
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> Neither a `name` nor its part before its first `-` is `v` or one of the 17 words listed in §4.4; the other reserved ids, such as `hasOwnProperty` and `direction`, parse as style words (`fill:hasOwnProperty`, `fill:direction-x`).

§4.1:

> a `unit` is not the one-letter word `v`, so `vh` is a unit; neither a `name` nor the part of it before its first `-` is `v` or one of the 17 words listed in §4.4; a `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`; and the `name` before a `:` is not `accTitle` or `accDescr` (§4.8).

§4.4:

> end graph flowchart subgraph style class classDef click linkStyle interpolate call href default _self _blank _parent _top

## Reasoning

`classx` is a `name`, and neither it nor a part before a `-` is one of the 17 words. The line matches `classdef-stmt`, so it declares the class `c`, which nothing else declares.
