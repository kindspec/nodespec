# refusal/nested-block

**Expected:** refused. Identifiers that apply: `nested-block`.

## Input

````text
flowchart TD
a[A]
subgraph s
  a
  subgraph t
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `subgraph`: in a block, `nested-block`, whether or not the line is well formed. At the top level, §4.7: it opens a block, or is `subgraph-without-id`, or is `malformed-line`.

§6:

> a subgraph line in a block is refused as `nested-block`;

## Reasoning

A subgraph line in a block is `nested-block`. It opens no block, so `end` closes `s`.

## Other identifiers

- `unbalanced-block`: One block opened, one closed.
- `undeclared-id`: The refused line names nothing; `t` is named nowhere.
