# refusal/malformed-line-whitespace-only-quoted-label

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[" "]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> a `quoted` label holds at least one character that is not `WSP`, does not begin with `` ` ``, and does not end with `=` (§4.5);

## Reasoning

A quoted label must hold a character that is not `WSP`.

## Other identifiers

- `not-admitted`: No `:::`, `@{` or `"` followed by a backtick.
