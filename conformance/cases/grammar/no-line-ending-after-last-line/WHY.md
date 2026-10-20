# grammar/no-line-ending-after-last-line

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
(no line ending after the last line)
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A line ends at LF, or at CR followed by LF; the line ending is not part of the line. The last line need not end with one.

## Reasoning

The last line need not end with a line ending.
