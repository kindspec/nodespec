# applicability/leading-bom-and-front-matter

**Expected:** refused. Identifiers that apply: `leading-bom`; `not-admitted`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
⟨BOM⟩---
title: x
---
flowchart TD
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> The mark is not part of the first line: the lines are read as if it were absent.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

## Reasoning

The mark is not part of the first line, so line 1 is `---` and front matter.

## Other identifiers

- `no-header`: The header follows the front matter.
