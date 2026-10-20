# refusal/direction-outside-block

**Expected:** refused. Identifiers that apply: `direction-outside-block`.

## Input

````text
flowchart TD
a[A]
direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `direction`: if the line matches `direction-stmt`, it is a direction statement in a block (§4.9), or at the top level `direction-outside-block`. Otherwise `malformed-line`.

§4.9:

> A direction statement, `direction LR`, sets a block's direction. It stands only in a block: at the top level it is refused as `direction-outside-block`.

## Reasoning

At the top level, a line matching `direction-stmt`.

## Other identifiers

- `stray-direction`: A line that matches `direction-stmt` is exempt.
- `malformed-line`: The line matches `direction-stmt`.
