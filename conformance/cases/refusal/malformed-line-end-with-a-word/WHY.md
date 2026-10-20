# refusal/malformed-line-end-with-a-word

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
end a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `end`: if the line matches `end-line`, it closes the open block, or at the top level is `unbalanced-block`. Otherwise `malformed-line`.

§4.7:

> `end-line` is `end` alone. Mermaid reads `end x` as the end of the block and a node `x`.

## Reasoning

The first word is `end` and the line does not match `end-line`.

## Other identifiers

- `unbalanced-block`: That is for a line that matches `end-line`.
