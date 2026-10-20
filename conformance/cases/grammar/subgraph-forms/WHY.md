# grammar/subgraph-forms

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
d[D]
subgraph s1
  a
end
subgraph s2 [Cache tier]
  b
end
subgraph s3["Cache tier"]
  c
end
subgraph s4 ⟨TAB⟩[Spaced]
  d
end
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line opens a block, and the next `end-line` closes it. Blocks do not nest (D3, §6). A subgraph line is `subgraph`, its explicit id, and optionally a title in `[ ]`: `subgraph cache`, `subgraph cache [Cache tier]`, `subgraph cache["Cache tier"]`. The title is a label (§4.5). Nothing follows the title or the id, not even `WSP`.

§4.1:

> subgraph-line = *WSP "subgraph" 1*WSP id [ *WSP "[" label "]" ]

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

## Reasoning

The first three subgraph lines are §4.7's three examples. `subgraph s4 \t[Spaced]` puts a space and a tab between id and title, which `[ *WSP "[" label "]" ]` allows; its `WSP` is followed by the `[`, so it is not `subgraph-without-id`. Nothing follows any title or id. Each block holds one member line naming a declared node.
