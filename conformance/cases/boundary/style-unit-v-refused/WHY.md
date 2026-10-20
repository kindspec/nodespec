# boundary/style-unit-v-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Style lists are narrower than Mermaid's (§4.8).

**Twin:** `boundary/style-unit-vh-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c height:1v
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A `unit` is any run of lower-case letters except the one-letter `v`.

§4.1:

> a `unit` is not the one-letter word `v`, so `vh` is a unit; neither a `name` nor the part of it before its first `-` is `v` or one of the 17 words listed in §4.4; a `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`; and the `name` before a `:` is not `accTitle` or `accDescr` (§4.8).

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

## Reasoning

The one-letter unit `v` is excluded, and `1v` is no other `word` (a `name` begins with a letter). So `classdef-stmt` does not match, and §4.3 rule 4 makes a top-level `classDef` line that does not match `malformed-line`.

## Other identifiers

- `reserved-id`: A style word is not an id, and the line is refused for another reason.
- `not-admitted`: Not one of §4.10's forms, and rule 4 classifies the line before rule 11 could.
- `stray-direction`: No `direction` in the line.
