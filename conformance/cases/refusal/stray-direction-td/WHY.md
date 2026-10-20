# refusal/stray-direction-td

**Expected:** refused. Identifiers that apply: `stray-direction`.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
a[go direction TD]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> The words compare exactly (provisional, as Mermaid's lexer does): `direction` in lower case, and `TB`, `BT`, `RL`, `LR` and `TD` in upper case. `a[go direction lr]`, `a[go direction Lr]`, `a[go Direction LR]` and `a[go DIRECTION LR]` each declare their node in Mermaid, and none is `stray-direction`.

## Reasoning

`TD` is one of the five words, upper case as required: the line holds `direction`, a space, `TD`.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`.
- `undeclared-id`: Nothing names `a`.
