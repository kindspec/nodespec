# refusal/lone-cr

**Expected:** refused. Identifiers that apply: `lone-cr`.

## Input

````text
flowchart TD⟨CR⟩a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A CR that is not followed by LF, that is a byte 0x0D not followed by a byte 0x0A, is refused as `lone-cr`.

§3:

> A file refused as `bad-encoding` or `lone-cr` is checked no further (§9).

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported.

## Reasoning

The CR after `TD` is followed by `a`, not LF. The file is refused as `lone-cr` and checked no further.

## Other identifiers

- `no-header`: To this profile the first line is `flowchart TD<CR>a[A]`, which is no header, but nothing else is checked once `lone-cr` applies.
