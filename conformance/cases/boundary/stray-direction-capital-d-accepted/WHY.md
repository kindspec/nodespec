# boundary/stray-direction-capital-d-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

**Twin:** `boundary/stray-direction-in-label-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[go Direction LR]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> The words compare exactly (provisional, as Mermaid's lexer does): `direction` in lower case, and `TB`, `BT`, `RL`, `LR` and `TD` in upper case. `a[go direction lr]`, `a[go direction Lr]`, `a[go Direction LR]` and `a[go DIRECTION LR]` each declare their node in Mermaid, and none is `stray-direction`.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

## Reasoning

`Direction` is not `direction`. The words compare exactly, and §4.9 names this label as declaring its node and not `stray-direction`. The line is an ordinary node statement.
