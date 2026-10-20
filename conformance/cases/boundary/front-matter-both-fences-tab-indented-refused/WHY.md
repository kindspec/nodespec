# boundary/front-matter-both-fences-tab-indented-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/front-matter-no-break-space-fences-with-title-refused`, which differs from this file by 4 byte edits (Levenshtein distance over bytes).

## Input

````text
⟨TAB⟩---
title: Example
⟨TAB⟩---
flowchart TD
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.2:

> Mermaid's matcher takes `---` with trailing whitespace, and indented, by any whitespace but a line end (U+00A0 included), only when both fences are indented alike; with one fence indented, or the two indented differently, Mermaid does not parse the file. The profile refuses every one of these forms, though not always with this rule's identifier.

§4.2:

> The lines of front matter are not statement lines, so the header comes after them.

## Reasoning

Both fences indented alike, by a tab, which is `WSP`.

## Other identifiers

- `no-header`: Line 4 is the header.
