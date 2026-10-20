# refusal/malformed-line-triple-colon-in-style

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
style a:::c fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§4.3:

> First word `classDef`, `class` or `style`: in a block, `statement-in-block`. At the top level, if the line matches `classdef-stmt`, `class-stmt` or `style-stmt` for its first word, it is that statement (§4.8); otherwise `malformed-line`.

## Reasoning

Changed at 374b8a9 from `malformed-line`. The line holds `:::`, and §4.2 rule 3 decides it before §4.3 rule 4: "no first word changes it".

## Other identifiers

- `malformed-line`: Rule 4 of §4.3 never sees the line: §4.2 rule 3 classified it first.
