# applicability/refused-subgraph-line-opens-no-block

**Expected:** refused. Identifiers that apply: `subgraph-without-id`; `malformed-line`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
a[A]
subgraph My Title
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§4.3:

> A bare id at the top level matches `member-line`, and is `malformed-line` there.

## Reasoning

§9's example: the member line is top-level and the `end` is unbalanced.

## Other identifiers

- `undeclared-id`: The refused lines name nothing.
- `nested-block`: No block is open when the subgraph line comes.
