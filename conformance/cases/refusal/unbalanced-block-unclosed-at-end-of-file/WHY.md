# refusal/unbalanced-block-unclosed-at-end-of-file

**Expected:** refused. Identifiers that apply: `unbalanced-block`.

## Input

````text
flowchart TD
a[A]
subgraph s
  a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A file that ends inside a block is refused as `unbalanced-block`.

§6:

> an `end-line` with no open block, and a file that ends inside a block, are refused as `unbalanced-block`.

## Reasoning

The file ends inside `s`.

## Other identifiers

- `malformed-line`: `  a` is a member line in the open block.
