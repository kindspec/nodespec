# boundary/style-name-swimlane-beta-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/style-name-swimlane-betax-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:swimlane-beta
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`, which Mermaid lexes as a keyword (`swimlane` and `swimlane-x` parse).

§4.1:

> a `unit` is not the one-letter word `v`, so `vh` is a unit; neither a `name` nor the part of it before its first `-` is `v` or one of the 17 words listed in §4.4; a `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`; and the `name` before a `:` is not `accTitle` or `accDescr` (§4.8).

## Reasoning

A `name` is not `swimlane-beta`. So `classdef-stmt` does not match, and §4.3 rule 4 makes a top-level `classDef` line that does not match `malformed-line`.

## Other identifiers

- `reserved-id`: A style word is not an id, and the line is refused for another reason.
- `not-admitted`: Not one of §4.10's forms, and rule 4 classifies the line before rule 11 could.
- `stray-direction`: No `direction` in the line.
