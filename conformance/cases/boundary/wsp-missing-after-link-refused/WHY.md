# boundary/wsp-missing-after-link-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/wsp-around-link-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a -->b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> Links and `&` have `WSP` on both sides: Mermaid also reads `a-->b`, but without the spaces `A---oB` is a circle-headed link to `B` and `a&b` is one node.

§4.1:

> edge-stmt = *WSP group 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP group ) *WSP

## Reasoning

No `WSP` between link and group.

## Other identifiers

- `not-admitted`: §4.10 sends forms Mermaid accepts and this grammar does not to `malformed-line`.
- `undeclared-id`: The refused line names nothing.
