# boundary/too-many-edges-500-accepted

**Expected:** accepted.

**Twin:** `boundary/too-many-edges-501-refused`, which differs from this file by one line, `n500 --> n0`, added.

## Input

flowchart TD, then n0[N0] … n500[N500] (501 lines), then n0 --> n1 … n499 --> n500 (500 lines), LF line endings.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> A file whose statements make more than 500 edges is refused as `too-many-edges` (the owner, 2026-10-19).

§4.6:

> Mermaid's default configuration accepts 500 edges and refuses 501 ("Edge limit exceeded");

## Reasoning

501 node statements `n0[N0]` … `n500[N500]`, then 500 edges `n{i} --> n{i+1}` for i = 0 … 499. 500 is not more than 500. The edges are pairwise distinct.
