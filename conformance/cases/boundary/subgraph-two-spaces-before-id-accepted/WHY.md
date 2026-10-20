# boundary/subgraph-two-spaces-before-id-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** After `subgraph`, the whole run of `WSP` is skipped before the `subgraph-without-id` test (§4.7).

**Twin:** `boundary/subgraph-two-spaces-before-id-trailing-wsp-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
subgraph  s
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§4.7:

> Skipping the whole run is how Mermaid reads it: `subgraph  s` with two spaces, and `subgraph`, a tab and a space, then `s`, both give the subgraph the id `s`.

§4.1:

> subgraph-line = *WSP "subgraph" 1*WSP id [ *WSP "[" label "]" ]

## Reasoning

After `subgraph` and the whole run of `WSP`, the text is `s`: no `WSP`, no `"`. The line matches `subgraph-line` (`1*WSP`) and opens the block.
