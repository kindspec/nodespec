# boundary/subgraph-two-spaces-before-id-trailing-wsp-refused

**Expected:** refused. Identifiers that apply: `subgraph-without-id`; `malformed-line`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** After `subgraph`, the whole run of `WSP` is skipped before the `subgraph-without-id` test (§4.7).

**Twin:** `boundary/subgraph-two-spaces-before-id-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
subgraph  s⟨SP⟩
  a
end
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

## Reasoning

After the run of `WSP` the text is `s `, which holds `WSP` and no `[`. The refused line opens no block, so `  a` is top-level `malformed-line` and `end` is `unbalanced-block`.

## Other identifiers

- `undeclared-id`: The refused lines name nothing.
