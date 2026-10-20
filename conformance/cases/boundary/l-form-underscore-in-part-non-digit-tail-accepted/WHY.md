# boundary/l-form-underscore-in-part-non-digit-tail-accepted

**Expected:** accepted.

**Twin:** `boundary/l-form-underscore-in-part-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
L_a_b__x[X]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> An id of the form `L_`, one or more characters, `_`, one or more characters, `_`, one or more digits, such as `L_a_b_0`, is refused as `reserved-id`.

§4.4:

> The characters may be any id characters, `_` included, so `L_a_b__0` has the form (`a`, then `b_`, then `0`); in regular-expression terms the whole id matches `L_.+_.+_[0-9]+`.

## Reasoning

`L_.+_.+_[0-9]+` must end in one or more digits after a `_`; `L_a_b__x` ends in `x`, so no split fits.
