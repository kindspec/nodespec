# refusal/malformed-line-semicolon-after-edge

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
b[B]
a --> b;
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> `;` is not admitted anywhere outside a label (the owner, 2026-10-19: refused for now), so a statement line ending in `;`, two statements on one line, and a member line `a;` are `malformed-line`, and a header ending in `;` is `no-header`.

## Reasoning

A statement line ending in `;` is `malformed-line`.

## Other identifiers

- `not-admitted`: `;` is listed under §4.10's `malformed-line` forms.
