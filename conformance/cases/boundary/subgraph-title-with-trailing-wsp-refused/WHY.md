# boundary/subgraph-title-with-trailing-wsp-refused

**Expected:** refused. Identifiers that apply: `malformed-line`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/subgraph-title-without-trailing-wsp-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
subgraph s [T]⟨SP⟩
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

> Any other top-level line whose first word is `subgraph` and that does not match `subgraph-line` is `malformed-line`.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

Nothing follows the title. The only `WSP` before the first `[` is followed by it, so this is not `subgraph-without-id` but `malformed-line`. The refused line opens no block: `  a` is top-level `malformed-line` and `end` is `unbalanced-block`.

## Other identifiers

- `subgraph-without-id`: The trailing space comes after the first `[`.
