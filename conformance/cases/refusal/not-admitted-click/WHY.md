# refusal/not-admitted-click

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
click a callback
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `click`; or the line begins, after `WSP`, with `accTitle` then `:`, or with `accDescr` then `:` or `{`, with any `WSP` between them: `not-admitted`.

§4.10:

> `click`, which attaches a link or a callback to a node;

## Reasoning

The first word is `click`, so §4.3 rule 6 refuses the line as `not-admitted`.

## Other identifiers

- `malformed-line`: Rule 6 applies first.
- `undeclared-id`: The refused line names nothing.
