# refusal/unbalanced-block-end-at-top-level

**Expected:** refused. Identifiers that apply: `unbalanced-block`.

## Input

````text
flowchart TD
a[A]
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `end`: if the line matches `end-line`, it closes the open block, or at the top level is `unbalanced-block`. Otherwise `malformed-line`.

§6:

> an `end-line` with no open block, and a file that ends inside a block, are refused as `unbalanced-block`.

## Reasoning

An `end-line` with no open block.

## Other identifiers

- `reserved-id`: `end` is no id here.
