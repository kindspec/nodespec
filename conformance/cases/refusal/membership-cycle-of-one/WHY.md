# refusal/membership-cycle-of-one

**Expected:** refused. Identifiers that apply: `membership-cycle` (id `s`).

## Input

````text
flowchart TD
subgraph s
  s
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> Nesting has no cycle. Following holders from a subgraph never returns to it. A cycle is refused as `membership-cycle`; a member line naming its own block's subgraph is a cycle of one.

## Reasoning

A member line naming its own block's subgraph.

## Other identifiers

- `wrong-kind`: A member line may name a subgraph.
- `member-twice`: One member line.
