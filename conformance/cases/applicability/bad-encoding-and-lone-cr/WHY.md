# applicability/bad-encoding-and-lone-cr

**Expected:** refused. Identifiers that apply: `bad-encoding`; `lone-cr`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** When `bad-encoding` or `lone-cr` applies, both are reported where both apply, and `leading-bom` is not (§9).

## Input

````text
flowchart TD⟨CR⟩a[⟨xFF⟩]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A file is UTF-8 (provisional). Bytes that are not well-formed UTF-8 are refused as `bad-encoding`.

§3:

> A CR that is not followed by LF, that is a byte 0x0D not followed by a byte 0x0A, is refused as `lone-cr` (provisional).

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported (provisional).

§9:

> A conformance case names every identifier that applies to its file, and for each entry about an id, every id it applies to; a report passes if its identifier, and its id where the entry has one, are among them.

## Reasoning

The file holds the byte 0xFF, which is not well-formed UTF-8, and a byte 0x0D followed by `a`, not 0x0A. §9 says both are reported when both apply, so the case lists both; a report of either passes.

## Other identifiers

- `no-header`: Not checked: `bad-encoding` or `lone-cr` stops checking.
- `malformed-line`: Not checked.
