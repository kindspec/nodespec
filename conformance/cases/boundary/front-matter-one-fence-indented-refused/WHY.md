# boundary/front-matter-one-fence-indented-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/front-matter-closed-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
---
title: Example
  ---
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.2:

> Mermaid's matcher takes `---` with trailing whitespace, and indented, by any whitespace but a line end (U+00A0 included), only when both fences are indented alike; with one fence indented, or the two indented differently, Mermaid does not parse the file. The profile refuses every one of these forms, though not always with this rule's identifier.

§4.2:

> The lines of front matter are not statement lines, so the header comes after them.

## Reasoning

The closing line is `---` with `WSP` before it, so it is "the next such line", and lines 1 to 3 are front matter, `not-admitted`. With one fence indented Mermaid does not parse the file; the profile refuses it too.

## Other identifiers

- `no-header`: Line 4 is the header.
