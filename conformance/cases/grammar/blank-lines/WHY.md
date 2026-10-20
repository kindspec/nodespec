# grammar/blank-lines

**Expected:** accepted.

## Input

````text

 ⟨TAB⟩⟨SP⟩
flowchart TD

a[A]
⟨SP⟩⟨SP⟩⟨SP⟩
⟨TAB⟩
b[B]

````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A blank line matches `blank`. It is allowed anywhere.

§4.1:

> blank = *WSP

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

## Reasoning

The empty lines and the lines of only spaces and tabs match `blank` and are allowed anywhere, before the header included.
