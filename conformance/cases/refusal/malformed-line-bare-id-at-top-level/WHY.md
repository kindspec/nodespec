# refusal/malformed-line-bare-id-at-top-level

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A bare id at the top level matches `member-line`, and is `malformed-line` there.

§4.3:

> Matches `member-line`: in a block, a member line (§6); at the top level, `malformed-line`.

## Reasoning

`a` matches `member-line`, and at the top level that is `malformed-line`.

## Other identifiers

- `duplicate-declaration`: A bare id is not a declaration.
- `undeclared-id`: `a` is declared, and the refused line names nothing anyway.
