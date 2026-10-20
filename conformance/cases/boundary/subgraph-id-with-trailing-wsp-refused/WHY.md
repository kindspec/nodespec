# boundary/subgraph-id-with-trailing-wsp-refused

**Expected:** refused. Identifiers that apply: `subgraph-without-id`; `malformed-line`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/subgraph-id-without-trailing-wsp-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
subgraph s⟨SP⟩
  a
end
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line opens a block, and the next `end-line` closes it. Blocks do not nest (D3, §6). A subgraph line is `subgraph`, its explicit id, and optionally a title in `[ ]`: `subgraph cache`, `subgraph cache [Cache tier]`, `subgraph cache["Cache tier"]`. The title is a label (§4.5). Nothing follows the title or the id, not even `WSP`.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§4.7:

> `subgraph` alone throws a `TypeError`; `subgraph My Title`, `subgraph "My Title"` and `subgraph s ` with a trailing space get an id `subGraphN` of Mermaid's numbering; and `subgraph a1 b1 [T]` gets the id `a1 b1`.

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

## Reasoning

`s ` holds `WSP` with no `[`. The refused line opens no block, so `  a` is top-level (`malformed-line`) and `end` is `unbalanced-block`.

## Other identifiers

- `undeclared-id`: The refused lines name nothing.
