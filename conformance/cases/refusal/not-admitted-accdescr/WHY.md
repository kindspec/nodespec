# refusal/not-admitted-accdescr

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
accDescr: A short description
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `click`; or the line begins, after `WSP`, with `accTitle` then `:`, or with `accDescr` then `:` or `{`, with any `WSP` between them: `not-admitted`.

§4.10:

> `accTitle` and `accDescr`, which are not in the spike's subset.

## Reasoning

The line begins with `accDescr` then `:`.

## Other identifiers

- `malformed-line`: Rule 6 applies before rule 12.
