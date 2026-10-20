# boundary/front-matter-no-break-space-fences-with-title-refused

**Expected:** refused. Identifiers that apply: `no-header`; `malformed-line`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** A front matter fence indented by anything other than `WSP`, such as U+00A0, is not a fence: it is the first statement line, so the file is `no-header`, and the lines after it are read under §4.3 as after any `no-header` line (§4.2).

**Twin:** `boundary/front-matter-both-fences-tab-indented-refused`, which differs from this file by 4 byte edits (Levenshtein distance over bytes).

## Input

````text
⟨U+00A0⟩---
title: Example
⟨U+00A0⟩---
flowchart TD
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A line indented by anything other than `WSP`, such as U+00A0, is not a fence here (provisional): it is the first statement line, so the file is `no-header`, and the lines after it, the closing fence included, are read under §4.3 as after any `no-header` line (§9). With a U+00A0 before each fence, the file `---`, `---`, `flowchart TD`, `a --> b` is `no-header` (the first fence), `malformed-line` (the second fence and the header) and `undeclared-id` for `a` and `b`.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

The first line is `no-header`; `title: Example`, the second fence and `flowchart TD` match nothing. `a[A]` is a node statement. This was the file of the e7e643e ambiguity, now settled.

## Other identifiers

- `not-admitted`: U+00A0 indentation makes no fence.
- `undeclared-id`: Nothing is named.
