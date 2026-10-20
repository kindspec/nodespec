# applicability/accdescr-block-lines-read-one-by-one

**Expected:** refused. Identifiers that apply: `not-admitted`; `malformed-line`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
accDescr {
  A description
}
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `click`; or the line begins, after `WSP`, with `accTitle` then `:`, or with `accDescr` then `:` or `{`, with any `WSP` between them: `not-admitted`.

§4.2:

> Each line is classified by the first rule below that matches it. A line that is classified is never also read as something else.

§4.10:

> A line is `not-admitted` only as §4.2 and §4.3 say.

## Reasoning

Only `accDescr {` is `not-admitted`; each later line is classified on its own and matches nothing.

## Other identifiers

- `no-header`: The header is line 1.
