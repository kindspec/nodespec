# applicability/refused-class-line-is-not-styled-twice

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
classDef d stroke:#333
class a c
class a d⟨SP⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

§4.8:

> A `class` line ends at its class id: Mermaid refuses `WSP` after it. `classDef` and `style` lines may end in `WSP`, which Mermaid keeps in the last style.

## Reasoning

The second `class` line ends in a space and is refused; it is not a `class` line for any later rule.

## Other identifiers

- `styled-twice`: Only one unrefused `class` line targets `a`.
