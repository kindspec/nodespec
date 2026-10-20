# refusal/malformed-line-direction-unknown-word

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
subgraph s
  direction XY
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `direction`: if the line matches `direction-stmt`, it is a direction statement in a block (§4.9), or at the top level `direction-outside-block`. Otherwise `malformed-line`.

§4.1:

> dir = "TB" / "TD" / "BT" / "LR" / "RL"

## Reasoning

The first word is `direction`, and `XY` is no `dir`, so `direction-stmt` does not match.

## Other identifiers

- `stray-direction`: `XY` is not `TB`, `BT`, `RL`, `LR` or `TD`, and the line does not end in `direction`.
- `direction-outside-block`: The line is in a block, and it is not a direction statement.
