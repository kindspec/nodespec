# applicability/declaration-in-block-declares-nothing

**Expected:** refused. Identifiers that apply: `declaration-in-block`; `undeclared-id` (id `a`).

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
b[B]
subgraph s
  a[A]
end
b --> a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

## Reasoning

§9's example: a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too.

## Other identifiers

- `statement-in-block`: `a[A]` is a node statement.
- `unbalanced-block`: The block is closed.
