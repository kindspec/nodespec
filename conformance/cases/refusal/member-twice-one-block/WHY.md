# refusal/member-twice-one-block

**Expected:** refused. Identifiers that apply: `member-twice` (id `a`).

**Pins the provisional reading (§12):** Two member lines naming one id in one block are refused (§6).

## Input

````text
flowchart TD
a[A]
subgraph s
  a
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> A node or a subgraph has at most one holder. An id named by more than one member line is refused as `member-twice`. Where the two lines are in two blocks, that is D3. Where both are in one block, refusing it is (provisional)

## Reasoning

Both member lines are in one block; refusing it is provisional.

## Other identifiers

- `duplicate-declaration`: Member lines declare nothing.
