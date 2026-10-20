# boundary/front-matter-closing-fence-two-dashes-refused

**Expected:** refused. Identifiers that apply: `not-admitted`; `no-header`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/front-matter-closed-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
---
title: Example
--
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

`--` is not `---`, so there is no closing line and front matter runs to the end of the file. No statement line is left, so the file is also `no-header`.

## Other identifiers

- `malformed-line`: No line is a statement line.
