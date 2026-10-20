# boundary/l-form-non-digit-tail-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** `default`, `direction` and `hasOwnProperty` are reserved, ids of the form `L_…_…_N` are reserved, and a class may not be `node` (§4.4).

**Twin:** `boundary/l-form-digit-tail-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
L_a_b_x[X]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id of the form `L_`, one or more characters, `_`, one or more characters, `_`, one or more digits, such as `L_a_b_0`, is refused as `reserved-id` (provisional).

## Reasoning

The form ends in `_` and one or more digits; `L_a_b_x` ends in `x`.
