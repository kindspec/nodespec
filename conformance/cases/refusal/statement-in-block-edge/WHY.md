# refusal/statement-in-block-edge

**Expected:** refused. Identifiers that apply: `statement-in-block`.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s
  a --> b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> an edge statement, or a `classDef`, `class` or `style` statement, in a block is refused as `statement-in-block`; an `edge-decl` in a block is `statement-in-block` too;

§4.3:

> Matches `edge-stmt`: in a block, `statement-in-block`; at the top level, an edge statement (§4.6).

## Reasoning

An edge statement in a block.

## Other identifiers

- `declaration-in-block`: The line matches `edge-stmt`, not `node-stmt`.
- `undeclared-id`: The refused line names nothing.
