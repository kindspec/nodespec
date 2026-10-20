# boundary/comment-before-header-holding-at-brace-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/comment-before-header-holding-at-space-brace-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
%% see @{x}
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

Line 1 holds `@{`: §4.2 rule 3 refuses it as `not-admitted`. It is not a statement line, so line 2 is still the first statement line and the header.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
- `no-header`: A rule-3 line is not a statement line; the header is line 2.
