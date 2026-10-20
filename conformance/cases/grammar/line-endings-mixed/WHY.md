# grammar/line-endings-mixed

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]⟨CR⟩
b[B]
a --> b⟨CR⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A line ends at LF, or at CR followed by LF; the line ending is not part of the line. The last line need not end with one.

## Reasoning

LF and CR LF each end a line; nothing requires one style per file.
