# refusal/not-admitted-triple-colon

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
b[B]
a:::c --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§4.10:

> `:::`, Mermaid's class shorthand, in any line (§4.2 rule 3).

## Reasoning

The line holds `:::`, so §4.2 rule 3 refuses it as `not-admitted` before any rule of §4.3 is tried.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
- `undeclared-id`: The refused line names nothing, so `c` is not named.
