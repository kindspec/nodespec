# grammar/line-endings-crlf

**Expected:** accepted.

## Input

````text
flowchart TD⟨CR⟩
a[A]⟨CR⟩
b[B]⟨CR⟩
a --> b⟨CR⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A line ends at LF, or at CR followed by LF; the line ending is not part of the line. The last line need not end with one.

§3:

> A CR that is not followed by LF, that is a byte 0x0D not followed by a byte 0x0A, is refused as `lone-cr` (provisional).

## Reasoning

Every line ends in CR LF, which ends a line. Every CR is followed by LF, so `lone-cr` does not apply.
