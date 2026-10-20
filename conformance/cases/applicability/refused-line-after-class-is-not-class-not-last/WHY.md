# applicability/refused-line-after-class-is-not-class-not-last

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
b[B]
classDef c fill:#f9f
class a c
a -->b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> Every other rule (`duplicate-declaration`, `undeclared-id`, `wrong-kind`, `kind-clash`, `duplicate-edge`, `too-many-edges`, the end-of-file `unbalanced-block`, `member-twice`, `membership-cycle`, `class-not-last` and `styled-twice`) is checked on the lines that are not refused.

§4.6:

> Links and `&` have `WSP` on both sides: Mermaid also reads `a-->b`, but without the spaces `A---oB` is a circle-headed link to `B` and `a&b` is one node.

## Reasoning

`class-not-last` is checked on unrefused lines only.

## Other identifiers

- `class-not-last`: The only line after the `class` line is refused.
