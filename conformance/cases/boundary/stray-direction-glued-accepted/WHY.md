# boundary/stray-direction-glued-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

**Twin:** `boundary/stray-direction-in-label-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[go directionLR]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> with trailing whitespace removed, it ends in `direction`.

## Reasoning

`direction` is followed by `L`, not whitespace, and the line ends in `]`.
