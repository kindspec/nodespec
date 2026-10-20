# boundary/duplicate-edge-same-link-refused

**Expected:** refused. Identifiers that apply: `duplicate-edge`.

**Twin:** `boundary/duplicate-edge-longer-link-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a --> b
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

## Reasoning

Two unnamed edges a→b, same link, no labels.

## Other identifiers

- `malformed-line`: Both lines match `edge-stmt`.
