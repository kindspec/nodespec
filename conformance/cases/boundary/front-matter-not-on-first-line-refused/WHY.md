# boundary/front-matter-not-on-first-line-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
---
title: Example
---
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

Front matter is only the file's first line. Here the three lines are statement lines matching nothing.

## Other identifiers

- `not-admitted`: Rule 1 is for the first line.
