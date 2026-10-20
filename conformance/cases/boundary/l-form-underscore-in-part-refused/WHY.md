# boundary/l-form-underscore-in-part-refused

**Expected:** refused. Identifiers that apply: `reserved-id` (id `L_a_b__0`).

**Pins the provisional reading (§12):** In the `L_…_…_N` form, the characters include `_` (§4.4).

**Twin:** `boundary/l-form-underscore-in-part-non-digit-tail-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
L_a_b__0[X]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id of the form `L_`, one or more characters, `_`, one or more characters, `_`, one or more digits, such as `L_a_b_0`, is refused as `reserved-id` (provisional).

§4.4:

> The characters may be any id characters, `_` included (provisional), so `L_a_b__0` has the form (`a`, then `b_`, then `0`); in regular-expression terms the whole id matches `L_.+_.+_[0-9]+`.

## Reasoning

§4.4's own example: `L_a_b__0` matches `L_.+_.+_[0-9]+` as `a`, then `b_`, then `0`.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`; `L_a_b__0` is an `id`.
