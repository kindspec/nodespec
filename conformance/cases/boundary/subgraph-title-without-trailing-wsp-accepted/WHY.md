# boundary/subgraph-title-without-trailing-wsp-accepted

**Expected:** accepted.

**Twin:** `boundary/subgraph-title-with-trailing-wsp-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
subgraph s [T]
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line opens a block, and the next `end-line` closes it. Blocks do not nest (D3, §6). A subgraph line is `subgraph`, its explicit id, and optionally a title in `[ ]`: `subgraph cache`, `subgraph cache [Cache tier]`, `subgraph cache["Cache tier"]`. The title is a label (§4.5). Nothing follows the title or the id, not even `WSP`.

## Reasoning


