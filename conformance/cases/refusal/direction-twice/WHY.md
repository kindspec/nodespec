# refusal/direction-twice

**Expected:** refused. Identifiers that apply: `direction-twice`.

## Input

````text
flowchart TD
a[A]
subgraph s
  direction LR
  direction TB
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> A block holds at most one direction statement: every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included.

## Reasoning

The second direction statement in `s`.

## Other identifiers

- `stray-direction`: Both lines match `direction-stmt`.
- `direction-outside-block`: Both are in a block.
