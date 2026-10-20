# refusal/declaration-in-block

**Expected:** refused. Identifiers that apply: `declaration-in-block`.

## Input

````text
flowchart TD
subgraph s
  a[A]
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> a node statement in a block is refused as `declaration-in-block`;

§4.3:

> Matches `node-stmt`: in a block, `declaration-in-block`; at the top level, a node statement, which declares a node (§5.1).

## Reasoning

A node statement in a block. Nothing names `a`, so `undeclared-id` does not arise.

## Other identifiers

- `unbalanced-block`: `end` closes `s`.
- `undeclared-id`: Nothing names `a`.
