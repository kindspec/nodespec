# refusal/malformed-line-inline-edge-label

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
b[B]
a -- yes --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> So is a label written inside the link, `-- yes -->`, `-. yes .->` or `== yes ==>` (the owner, 2026-10-19: refused for now)

§4.1:

> link = 2*"-" ">" / 3*"-" / 2*"-" "o" / 2*"-" "x" / "<" 2*"-" ">" / "o" 2*"-" "o" / "x" 2*"-" "x" / "-" 1*"." "->" / "-" 1*"." "-" / 2*"=" ">" / 3*"=" / 3*"~"

## Reasoning

`--` alone is no alternative of `link`, so `edge-stmt` and `edge-decl` do not match; no other production does, and the line holds no `:::`, `@{` or `"` then backtick.

## Other identifiers

- `not-admitted`: §4.10: a line is `not-admitted` only as §4.2 and §4.3 say, and `-- text -->` is named as `malformed-line`.
- `undeclared-id`: The refused line names nothing.
