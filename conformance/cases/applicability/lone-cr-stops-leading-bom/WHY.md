# applicability/lone-cr-stops-leading-bom

**Expected:** refused. Identifiers that apply: `lone-cr`.

## Input

````text
⟨BOM⟩flowchart TD⟨CR⟩a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported.

§3:

> A file that begins with a byte-order mark is refused as `leading-bom`.

## Reasoning

The file begins with a byte-order mark and holds a lone CR. `lone-cr` applies, and §9 says `leading-bom` is not reported.

## Other identifiers

- `leading-bom`: §9: not reported when `lone-cr` applies.
- `no-header`: Not checked.
