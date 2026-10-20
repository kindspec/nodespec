# applicability/lone-cr-stops-checking

**Expected:** refused. Identifiers that apply: `lone-cr`.

## Input

````text
Flowchart TD⟨CR⟩a --> b
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> `bad-encoding` and `lone-cr` are about the whole file, and when either applies, nothing else is checked: both are reported when both apply, and `leading-bom` is not reported.

## Reasoning

Nothing else is checked.

## Other identifiers

- `no-header`: Not checked.
- `undeclared-id`: Not checked.
