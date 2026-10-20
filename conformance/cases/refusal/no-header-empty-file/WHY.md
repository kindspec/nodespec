# refusal/no-header-empty-file

**Expected:** refused. Identifiers that apply: `no-header`.

## Input

````text
(empty file: zero bytes)
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

A file of zero bytes has no statement line.

## Other identifiers

- `malformed-line`: There are no lines to classify.
