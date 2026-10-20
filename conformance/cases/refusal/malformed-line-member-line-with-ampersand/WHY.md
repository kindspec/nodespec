# refusal/malformed-line-member-line-with-ampersand

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s
  a & b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> A member line holds one id: Mermaid reads `a & b` in a block, and it is `malformed-line` here.

## Reasoning

A member line holds one id.

## Other identifiers

- `statement-in-block`: `a & b` is a group, not an `edge-stmt`.
