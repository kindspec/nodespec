# boundary/style-name-swimlane-hyphen-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
classDef c fill:swimlane-x
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> A `name` is not `swimlane-beta` and does not begin with `swimlane-beta-`, which Mermaid lexes as a keyword (`swimlane` and `swimlane-x` parse).

## Reasoning

§4.8 names `swimlane-x` as parsing; it is not `swimlane-beta` and does not begin with `swimlane-beta-`.
