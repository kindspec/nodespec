# refusal/statement-in-block-with-edge-id-on-group

**Expected:** refused. Identifiers that apply: `statement-in-block`.

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
subgraph s
  a & b e1@--> c
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> `edge-id-on-group` applies only to a line that §4.3 classifies as an edge statement (rule 8, at the top level). A line refused as `declaration-in-edge` or `statement-in-block` is not also `edge-id-on-group`, since §4.2 reads a classified line as nothing else.

§4.3:

> Matches `edge-stmt`: in a block, `statement-in-block`; at the top level, an edge statement (§4.6).

## Reasoning

An edge statement in a block is `statement-in-block`, and not also `edge-id-on-group`.

## Other identifiers

- `edge-id-on-group`: Applies only at the top level.
