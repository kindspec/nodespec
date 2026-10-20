# boundary/unquoted-label-tilde-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** An unquoted label holds no `~~~` (§4.5).

**Twin:** `boundary/quoted-label-tilde-accepted`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[x ~~~ y]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> the profile refuses `~~~` anywhere in an unquoted label, which is simpler to check (provisional). A quoted label may hold it.

§4.1:

> an `unquoted` label does not hold `~~~` (§4.5);

## Reasoning

An unquoted label holds no `~~~`.

## Other identifiers

- `not-admitted`: No rule 11 form.
