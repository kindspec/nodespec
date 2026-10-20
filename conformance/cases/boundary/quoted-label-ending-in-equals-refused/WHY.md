# boundary/quoted-label-ending-in-equals-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/quoted-label-equals-then-space-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a["x="]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> does not end with `=`.

§4.1:

> a `quoted` label holds at least one character that is not `WSP`, does not begin with `` ` ``, and does not end with `=` (§4.5);

## Reasoning

A quoted label ending in `=` matches no production.

## Other identifiers

- `not-admitted`: No `"` followed by a backtick.
