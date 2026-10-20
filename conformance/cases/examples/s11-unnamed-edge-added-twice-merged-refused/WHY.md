# examples/s11-unnamed-edge-added-twice-merged-refused

**Expected:** refused. Identifiers that apply: `duplicate-edge`.

## Input

````text
flowchart TD
a[A]
a --> b
b[B]
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§11:

> Where both branches move the same unnamed edge, or both add it in different places, the merged file holds it twice and is refused as `duplicate-edge` (§4.6).

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

## Reasoning

§11: both branches add `a --> b` in different places. Each branch added the unnamed edge `a --> b`, at different places; the merge keeps both lines. Two edges with no edge ids, the same ends, the same link and no labels.

## Other identifiers

- `malformed-line`: Both lines match `edge-stmt`.
