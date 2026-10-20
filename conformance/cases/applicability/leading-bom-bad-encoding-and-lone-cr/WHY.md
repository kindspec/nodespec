# applicability/leading-bom-bad-encoding-and-lone-cr

**Expected:** refused. Identifiers that apply: `bad-encoding`; `lone-cr`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
⟨BOM⟩flowchart TD⟨CR⟩a[⟨xFF⟩]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported.

§3:

> A file is UTF-8. Bytes that are not well-formed UTF-8 are refused as `bad-encoding`.

§3:

> A CR that is not followed by LF, that is a byte 0x0D not followed by a byte 0x0A, is refused as `lone-cr`.

## Reasoning

A byte-order mark, a lone CR and the byte 0xFF. Both whole-file refusals apply and both are reported; `leading-bom` is not.

## Other identifiers

- `leading-bom`: §9: not reported when `bad-encoding` or `lone-cr` applies.
