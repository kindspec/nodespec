# boundary/quoted-label-equals-then-space-accepted

**Expected:** accepted.

**Twin:** `boundary/quoted-label-ending-in-equals-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a["x= "]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> does not end with `=`.

§4.1:

> a `quoted` label holds at least one character that is not `WSP`, does not begin with `` ` ``, and does not end with `=` (§4.5);

## Reasoning

The text ends in a space, not `=`.
