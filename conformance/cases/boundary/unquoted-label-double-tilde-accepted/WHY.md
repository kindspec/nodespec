# boundary/unquoted-label-double-tilde-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** An unquoted label holds no `~~~` (§4.5).

**Twin:** `boundary/unquoted-label-tilde-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[x ~~ y]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> the profile refuses `~~~` anywhere in an unquoted label, which is simpler to check (provisional). A quoted label may hold it.

§4.1:

> an `unquoted` label does not hold `~~~` (§4.5);

## Reasoning

Only `~~~` is refused in an unquoted label; `~` is an `lchar`.
