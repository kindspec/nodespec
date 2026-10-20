# refusal/statement-in-block-bare-classdef

**Expected:** refused. Identifiers that apply: `statement-in-block`.

## Input

````text
flowchart TD
a[A]
subgraph s
  a
  classDef
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `classDef`, `class` or `style`: in a block, `statement-in-block`. At the top level, if the line matches `classdef-stmt`, `class-stmt` or `style-stmt` for its first word, it is that statement (§4.8); otherwise `malformed-line`.

## Reasoning

In a block, a first word of `classDef` is `statement-in-block` without the line needing to match `classdef-stmt`.

## Other identifiers

- `malformed-line`: Rule 4's block branch does not ask for a match.
