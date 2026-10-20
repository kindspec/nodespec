# refusal/not-admitted-acctitle-spaced-colon

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
accTitle : Example
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `click`; or the line begins, after `WSP`, with `accTitle` then `:`, or with `accDescr` then `:` or `{`, with any `WSP` between them: `not-admitted`.

## Reasoning

`accTitle`, then a space, then `:`: rule 6 allows any `WSP` between them.

## Other identifiers

- `malformed-line`: Rule 6 comes before rule 12.
