# refusal/malformed-line-style-property-acctitle

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Style lists are narrower than Mermaid's (§4.8).

## Input

````text
flowchart TD
a[A]
classDef c accTitle:red
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A property's name is not `accTitle` or `accDescr`.

§4.1:

> a `unit` is not the one-letter word `v`, so `vh` is a unit; neither a `name` nor the part of it before its first `-` is `v` or one of the 17 words listed in §4.4; a `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`; and the `name` before a `:` is not `accTitle` or `accDescr` (§4.8).

## Reasoning

The name before a `:` is `accTitle`, which a style item may not have.

## Other identifiers

- `not-admitted`: Rule 6 asks that the line *begin* with `accTitle`; this line begins with `classDef`, so rule 4 classifies it and finds no match.
