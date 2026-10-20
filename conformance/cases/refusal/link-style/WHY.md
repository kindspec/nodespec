# refusal/link-style

**Expected:** refused. Identifiers that apply: `link-style`.

## Input

````text
flowchart TD
a[A]
b[B]
a --> b
linkStyle 0 stroke:#f00
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> First word `linkStyle`: `link-style`.

§7:

> `linkStyle` is refused as `link-style`.

## Reasoning

The first word is `linkStyle`.

## Other identifiers

- `malformed-line`: Rule 5 applies by first word alone.
- `duplicate-edge`: One edge.
