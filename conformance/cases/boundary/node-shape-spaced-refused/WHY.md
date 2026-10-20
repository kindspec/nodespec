# boundary/node-shape-spaced-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/node-shape-adjacent-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a [A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A node statement is an id and a shape, with nothing between them: `a [A]` does not parse in Mermaid. The shapes are Mermaid's classic fourteen:

## Reasoning

Nothing may stand between id and shape.

## Other identifiers

- `declaration-in-edge`: `[A]` is neither a link nor a group, so `edge-decl` does not match.
- `not-admitted`: No §4.10 form.
