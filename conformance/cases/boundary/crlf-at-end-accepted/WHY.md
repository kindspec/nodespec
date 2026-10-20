# boundary/crlf-at-end-accepted

**Expected:** accepted.

**Twin:** `boundary/lone-cr-at-end-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD⟨CR⟩
a[A]⟨CR⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A line ends at LF, or at CR followed by LF; the line ending is not part of the line. The last line need not end with one.

## Reasoning


