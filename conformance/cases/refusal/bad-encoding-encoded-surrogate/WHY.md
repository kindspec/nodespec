# refusal/bad-encoding-encoded-surrogate

**Expected:** refused. Identifiers that apply: `bad-encoding`.

## Input

````text
flowchart TD
a[⟨xED⟩⟨xA0⟩⟨x80⟩]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A file is UTF-8. Bytes that are not well-formed UTF-8 are refused as `bad-encoding`.

§3:

> A file refused as `bad-encoding` or `lone-cr` is checked no further (§9).

§4.1:

> nonascii = %xA0-2027 / %x202A-D7FF / %xE000-10FFFF ; not U+2028 or U+2029 (§4.2)

## Reasoning

ED A0 80 is the three-byte form of U+D800, a surrogate. Surrogates are not encodable in well-formed UTF-8, so these bytes are not well-formed UTF-8. `nonascii` also leaves out U+D800 to U+DFFF.

## Other identifiers

- `malformed-line`: Checking stops at `bad-encoding`.
