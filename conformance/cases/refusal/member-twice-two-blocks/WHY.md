# refusal/member-twice-two-blocks

**Expected:** refused. Identifiers that apply: `member-twice` (id `a`).

## Input

````text
flowchart TD
a[A]
subgraph s
  a
end
subgraph t
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> A node or a subgraph has at most one holder. An id named by more than one member line is refused as `member-twice`. Where the two lines are in two blocks, that is D3. Where both are in one block, it is refused as well

## Reasoning

`a` is named by member lines in `s` and in `t`.

## Other identifiers

- `membership-cycle`: `s` and `t` hold only the node `a`.
- `duplicate-declaration`: Member lines declare nothing.
