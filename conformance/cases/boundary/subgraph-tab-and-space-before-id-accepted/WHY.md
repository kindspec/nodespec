# boundary/subgraph-tab-and-space-before-id-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
subgraph⟨TAB⟩ s
  a
end
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§4.7:

> Skipping the whole run is how Mermaid reads it: `subgraph  s` with two spaces, and `subgraph`, a tab and a space, then `s`, both give the subgraph the id `s`.

## Reasoning

§4.7's own example: `subgraph`, a tab and a space, then `s`, has the id `s`.
