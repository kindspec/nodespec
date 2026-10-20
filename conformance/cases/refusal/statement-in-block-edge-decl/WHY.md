# refusal/statement-in-block-edge-decl

**Expected:** refused. Identifiers that apply: `statement-in-block`.

## Input

````text
flowchart TD
b[B]
subgraph s
  a[A] --> b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> Matches `edge-decl`: in a block, `statement-in-block`; at the top level, `declaration-in-edge`.

§6:

> an edge statement, or a `classDef`, `class` or `style` statement, in a block is refused as `statement-in-block`; an `edge-decl` in a block is `statement-in-block` too;

## Reasoning

`a[A] --> b` matches `edge-decl`; in a block that is `statement-in-block`.

## Other identifiers

- `declaration-in-edge`: That is the top-level branch of rule 9.
