# applicability/stray-direction-with-triple-colon-in-label

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
a[go direction LR :::]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines and to comments refused for `:::` or `@{`, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

§4.9:

> So a line other than a comment, a front matter line or a line that matches `direction-stmt` is refused as `stray-direction` when:

## Reasoning

The line holds `:::` (`not-admitted`) and `direction LR`. It is not a comment, front matter or a direction statement, and `stray-direction` applies whatever else applies.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
