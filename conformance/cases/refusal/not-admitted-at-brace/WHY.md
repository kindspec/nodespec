# refusal/not-admitted-at-brace

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Pins the provisional reading (§12):** `@{ … }` is not admitted (§4.10).

## Input

````text
flowchart TD
a[A]
a@{ shape: rect }
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> Holds `:::` or `@{`, or a `"` directly followed by `` ` ``: `not-admitted`.

§4.10:

> `@{ … }`, Mermaid's newer shape and edge data form (provisional).

## Reasoning

The line matches no earlier production and holds `@{`.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
- `duplicate-declaration`: The refused line declares nothing.
