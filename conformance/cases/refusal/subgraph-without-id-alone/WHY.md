# refusal/subgraph-without-id-alone

**Expected:** refused. Identifiers that apply: `subgraph-without-id`.

## Input

````text
flowchart TD
subgraph
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

## Reasoning

After `subgraph` the text is empty.

## Other identifiers

- `reserved-id`: No id stands in the line.
- `unbalanced-block`: No block was opened.
