# boundary/front-matter-four-dashes-refused

**Expected:** refused. Identifiers that apply: `no-header`; `malformed-line`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/front-matter-closed-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
----
title: Example
----
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

`----` is not `---`, so there is no front matter. Line 1 is the first statement line and no header; then `title: Example`, `----` and `flowchart TD` are statement lines matching nothing.

## Other identifiers

- `not-admitted`: Front matter needs `---`.
