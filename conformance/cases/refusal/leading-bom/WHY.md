# refusal/leading-bom

**Expected:** refused. Identifiers that apply: `leading-bom`.

## Input

````text
⟨BOM⟩flowchart TD
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> A file that begins with a byte-order mark is refused as `leading-bom`.

§3:

> The mark is not part of the first line: the lines are read as if it were absent.

## Reasoning

The file begins with EF BB BF, the UTF-8 byte-order mark. The lines are read as if it were absent, so the first line is the header `flowchart TD` and nothing else is wrong.

## Other identifiers

- `no-header`: The mark is not part of the first line, so the header matches.
- `bad-encoding`: EF BB BF is well-formed UTF-8 (U+FEFF).
