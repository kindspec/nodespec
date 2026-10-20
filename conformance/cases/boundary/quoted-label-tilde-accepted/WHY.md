# boundary/quoted-label-tilde-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** An unquoted label holds no `~~~` (§4.5).

**Twin:** `boundary/unquoted-label-tilde-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a["x ~~~ y"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> the profile refuses `~~~` anywhere in an unquoted label, which is simpler to check (provisional). A quoted label may hold it.

## Reasoning

A quoted label may hold `~~~`.
