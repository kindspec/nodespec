# refusal/subgraph-without-id-quoted-title

**Expected:** refused. Identifiers that apply: `subgraph-without-id`.

## Input

````text
flowchart TD
subgraph "My Title"
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.7:

> A subgraph line with no explicit id is refused as `subgraph-without-id` (D1). It is a line whose first word is `subgraph` and in which, after `subgraph` and the whole run of `WSP` that follows it (provisional), the text is empty, or begins with `"`, or holds `WSP` before its first `[` (or anywhere, if it has none) that is not followed, after any more `WSP`, by that `[`.

§4.7:

> `subgraph` alone throws a `TypeError`; `subgraph My Title`, `subgraph "My Title"` and `subgraph s ` with a trailing space get an id `subGraphN` of Mermaid's numbering; and `subgraph a1 b1 [T]` gets the id `a1 b1`.

## Reasoning

The text after `subgraph ` begins with `"`.

## Other identifiers

- `unbalanced-block`: No block was opened.
