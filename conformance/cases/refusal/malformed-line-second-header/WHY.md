# refusal/malformed-line-second-header

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
flowchart TD
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

§4.3:

> Anything else: `malformed-line`.

## Reasoning

Only the first statement line is the header. Later, `flowchart TD` matches no production.

## Other identifiers

- `no-header`: The first statement line is a header.
- `reserved-id`: `flowchart TD` is not an id in a matching line.
