# boundary/too-many-edges-501-refused

**Expected:** refused. Identifiers that apply: `too-many-edges`.

**Twin:** `boundary/too-many-edges-500-accepted`, which differs from this file by one line, `n500 --> n0`, added.

## Input

As too-many-edges-500-accepted, with one more line: n500 --> n0.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> A file whose statements make more than 500 edges is refused as `too-many-edges` (the owner, 2026-10-19).

§4.6:

> Mermaid's default configuration accepts 500 edges and refuses 501 ("Edge limit exceeded");

## Reasoning

The 500-edge file plus `n500 --> n0`: 501 edges. No one-byte twin exists (see README).

## Other identifiers

- `duplicate-edge`: n500→n0 is distinct from every other edge.
