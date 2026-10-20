# refusal/statement-in-block-style

**Expected:** refused. Identifiers that apply: `statement-in-block`.

## Input

````text
flowchart TD
a[A]
subgraph s
  style a fill:#f9f
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> an edge statement, or a `classDef`, `class` or `style` statement, in a block is refused as `statement-in-block`; an `edge-decl` in a block is `statement-in-block` too;

§4.3:

> First word `classDef`, `class` or `style`: in a block, `statement-in-block`. At the top level, if the line matches `classdef-stmt`, `class-stmt` or `style-stmt` for its first word, it is that statement (§4.8); otherwise `malformed-line`.

## Reasoning

A `style` statement in a block.

## Other identifiers

- `malformed-line`: Rule 4's block branch applies without asking for a match.
- `styled-twice`: The refused line is not a `style` line for any later rule.
