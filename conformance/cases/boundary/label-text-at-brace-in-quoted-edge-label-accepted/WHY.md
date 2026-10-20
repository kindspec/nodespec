# boundary/label-text-at-brace-in-quoted-edge-label-accepted

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/label-text-at-brace-in-unquoted-edge-label-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a -->|"x@{y"| b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§4.1:

> And a line that holds `:::` or `@{` is `not-admitted` before any production is tried (§4.2 rule 3), so a label that the grammar admits holding them, such as `a[x:::y]`, is still refused.

## Reasoning

Changed at 374b8a9 from accepted. The quoted edge label holds `@{`, so the line does. §4.2 rule 3 refuses a line holding `:::` or `@{` anywhere, label text included, before any production is tried.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
