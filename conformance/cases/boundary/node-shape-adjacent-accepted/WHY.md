# boundary/node-shape-adjacent-accepted

**Expected:** accepted.

**Twin:** `boundary/node-shape-spaced-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A node statement is an id and a shape, with nothing between them: `a [A]` does not parse in Mermaid. The shapes are Mermaid's classic fourteen:

## Reasoning


