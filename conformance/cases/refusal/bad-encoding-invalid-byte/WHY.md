# refusal/bad-encoding-invalid-byte

**Expected:** refused. Identifiers that apply: `bad-encoding`.

**Pins the provisional reading (§12):** UTF-8 is required; a leading BOM and a lone CR are refused (§3).

## Input

````text
flowchart TD
a[⟨xFF⟩]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A file is UTF-8 (provisional). Bytes that are not well-formed UTF-8 are refused as `bad-encoding`.

§3:

> A file refused as `bad-encoding` or `lone-cr` is checked no further (§9).

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported (provisional).

## Reasoning

The byte 0xFF never occurs in well-formed UTF-8, so the file is refused as `bad-encoding` and checked no further.

## Other identifiers

- `malformed-line`: The label line might otherwise be examined, but nothing else is checked once `bad-encoding` applies.
