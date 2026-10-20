# refusal/malformed-line-id-non-ascii

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
café[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id is one or more ASCII letters, digits and underscores. Mermaid accepts more, including `-`, `.` and non-ASCII letters; the profile does not.

§4.1:

> id = 1*( ALPHA / DIGIT / "_" )

## Reasoning

`é` is not an ASCII letter, so no production matches.

## Other identifiers

- `bad-encoding`: The file is well-formed UTF-8.
