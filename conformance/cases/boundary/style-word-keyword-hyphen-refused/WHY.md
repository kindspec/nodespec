# boundary/style-word-keyword-hyphen-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/style-word-keyword-glued-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:class-x
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

`class-x`'s part before its first `-` is `class`, one of the 17 words. So `classdef-stmt` does not match, and §4.3 rule 4 makes a top-level `classDef` line that does not match `malformed-line`.

## Other identifiers

- `reserved-id`: A style word is not an id, and the line is refused for another reason.
- `not-admitted`: Not one of §4.10's forms, and rule 4 classifies the line before rule 11 could.
- `stray-direction`: No `direction` in the line.
