# boundary/lone-cr-at-end-refused

**Expected:** refused. Identifiers that apply: `lone-cr`.

**Pins the provisional reading (§12):** UTF-8 is required; a leading BOM and a lone CR are refused (§3).

**Twin:** `boundary/crlf-at-end-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD⟨CR⟩
a[A]⟨CR⟩
(no line ending after the last line)
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A CR that is not followed by LF, that is a byte 0x0D not followed by a byte 0x0A, is refused as `lone-cr` (provisional).

## Reasoning

The last CR is followed by no LF.

## Other identifiers

- `malformed-line`: Checking stops at `lone-cr`.
