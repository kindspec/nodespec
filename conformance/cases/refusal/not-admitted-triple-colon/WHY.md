# refusal/not-admitted-triple-colon

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
b[B]
a:::c --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> Holds `:::` or `@{`, or a `"` directly followed by `` ` ``: `not-admitted`.

§4.10:

> `:::`, a class given inside a node or edge statement.

## Reasoning

`a:::c --> b` matches neither `node-stmt`, `edge-stmt`, `edge-decl` nor `member-line`, since `:` is not an id character and the first group is followed by `:::`. Rule 11 then finds `:::`.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
- `undeclared-id`: The refused line names nothing, so `c` is not named.
