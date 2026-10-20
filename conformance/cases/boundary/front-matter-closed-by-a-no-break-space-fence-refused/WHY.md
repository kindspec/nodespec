# boundary/front-matter-closed-by-a-no-break-space-fence-refused

**Expected:** refused. Identifiers that apply: `not-admitted`; `no-header`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/front-matter-closed-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
---
title: Example
⟨U+00A0⟩---
flowchart TD
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.2:

> A line indented by anything other than `WSP`, such as U+00A0, is not a fence here: it is the first statement line, so the file is `no-header`, and the lines after it, the closing fence included, are read under §4.3 as after any `no-header` line (§9). With a U+00A0 before each fence, the file `---`, `---`, `flowchart TD`, `a --> b` is `no-header` (the first fence), `malformed-line` (the second fence and the header) and `undeclared-id` for `a` and `b`.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place.

## Reasoning

Line 1 is a fence. Line 3 is indented by U+00A0, so it is not "the next such line", and front matter runs to the end of the file. No statement line is left.

## Other identifiers

- `malformed-line`: Every line is front matter.
