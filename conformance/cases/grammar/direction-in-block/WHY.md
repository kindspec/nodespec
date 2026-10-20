# grammar/direction-in-block

**Expected:** accepted.

## Input

````text
flowchart TB
a[A]
subgraph s
  direction LR
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> A direction statement, `direction LR`, sets a block's direction. It stands only in a block (provisional): at the top level it is refused as `direction-outside-block`.

§4.1:

> direction-stmt = *WSP "direction" 1*WSP dir *WSP

§4.3:

> First word `direction`: if the line matches `direction-stmt`, it is a direction statement in a block (§4.9), or at the top level `direction-outside-block`. Otherwise `malformed-line`.

§4.9:

> So a line other than a comment, a front matter line or a line that matches `direction-stmt` is refused as `stray-direction` when (provisional, in this exact form):

## Reasoning

`  direction LR` in a block has first word `direction` and matches `direction-stmt`, so it is a direction statement in a block. A line that matches `direction-stmt` is exempt from `stray-direction`.
