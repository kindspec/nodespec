# grammar/direction-in-two-blocks

**Expected:** accepted.

**Pins the provisional reading (§12):** A direction statement only in a block, at most one per block (§4.9).

## Input

````text
flowchart TB
a[A]
b[B]
subgraph s
  direction LR
  a
end
subgraph t
  direction RL
  b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> A block holds at most one direction statement (provisional): every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included (provisional).

§4.9:

> A direction statement, `direction LR`, sets a block's direction. It stands only in a block (provisional): at the top level it is refused as `direction-outside-block`.

## Reasoning

The limit is one direction statement per block. Each block holds one, so `direction-twice` does not apply.
