# refusal/malformed-line-id-with-hyphen

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Ids are ASCII letters, digits and `_` (§4.4).

## Input

````text
flowchart TD
a-b[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id is one or more ASCII letters, digits and underscores. Mermaid accepts more, including `-`, `.` and non-ASCII letters; the profile does not (provisional).

§4.1:

> id = 1*( ALPHA / DIGIT / "_" )

## Reasoning

`-` is not an id character, so `a-b[A]` matches no production.

## Other identifiers

- `not-admitted`: Other ids are `malformed-line` (§4.10).
