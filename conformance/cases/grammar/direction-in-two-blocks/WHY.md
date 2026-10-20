# grammar/direction-in-two-blocks

**Expected:** accepted.

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

> A block holds at most one direction statement: every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included.

§4.9:

> A direction statement, `direction LR`, sets a block's direction. It stands only in a block: at the top level it is refused as `direction-outside-block`.

## Reasoning

The limit is one direction statement per block. Each block holds one, so `direction-twice` does not apply.
