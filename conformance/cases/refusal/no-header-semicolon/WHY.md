# refusal/no-header-semicolon

**Expected:** refused. Identifiers that apply: `no-header`.

## Input

````text
flowchart TD;
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A header in another case (`Flowchart`), with another direction (`td`, `<`, `v`), with `flowchart-elk`, or with a `;` after it does not match. The direction is optional, as in the spike's subset.

§4.3:

> `;` is not admitted anywhere outside a label (the owner, 2026-10-19: refused for now), so a statement line ending in `;`, two statements on one line, and a member line `a;` are `malformed-line`, and a header ending in `;` is `no-header`.

## Reasoning

A header with a `;` after it does not match. The lines after it are read as if a header stood there, and `a[A]` is an ordinary node statement.

## Other identifiers

- `malformed-line`: A header ending in `;` is `no-header`, as §4.3 says.
