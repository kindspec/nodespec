# boundary/label-text-at-brace-in-quoted-node-label-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/label-text-at-brace-in-quoted-node-label-unclosed-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/label-text-at-brace-in-unquoted-node-label-refused`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

**Twin:** `boundary/label-text-at-space-brace-in-quoted-node-label-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
c["x@{y"]
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

Changed at 374b8a9 from accepted. §4.10's own example `a["x@{y"]`: the line holds `@{`. §4.2 rule 3 refuses a line holding `:::` or `@{` anywhere, label text included, before any production is tried.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
