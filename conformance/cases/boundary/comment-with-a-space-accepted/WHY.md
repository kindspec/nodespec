# boundary/comment-with-a-space-accepted

**Expected:** accepted.

**Twin:** `boundary/percent-pair-alone-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%%⟨SP⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> comment = *WSP "%%" ( HTAB / %x20-7A / %x7C-7E / nonascii ) *cchar ; next is not "{"

## Reasoning

`%%` then a space is a comment.
