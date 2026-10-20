# boundary/class-line-with-trailing-wsp-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/class-line-without-trailing-wsp-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
class a c⟨SP⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A `class` line ends at its class id: Mermaid refuses `WSP` after it. `classDef` and `style` lines may end in `WSP`, which Mermaid keeps in the last style.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

## Reasoning

`class-stmt` has no trailing `WSP`.

## Other identifiers

- `undeclared-id`: The refused line names nothing.
