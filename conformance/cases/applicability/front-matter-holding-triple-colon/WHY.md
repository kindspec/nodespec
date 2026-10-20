# applicability/front-matter-holding-triple-colon

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
---
title: a:::b
---
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.2:

> Each line is classified by the first rule below that matches it. A line that is classified is never also read as something else.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

## Reasoning

Rule 1 comes before rule 3, so line 2 is front matter like lines 1 and 3. Either way the identifier is `not-admitted`; the case pins that the header is still line 4.

## Other identifiers

- `no-header`: Front-matter lines are not statement lines; line 4 is the header.
