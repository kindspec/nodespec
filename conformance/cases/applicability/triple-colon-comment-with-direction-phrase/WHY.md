# applicability/triple-colon-comment-with-direction-phrase

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
%% ::: direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> That includes a line that matches `comment` but is refused by §4.2 rule 3 for holding `:::` or `@{`: Mermaid removes it all the same, so `%% ::: direction LR` is `not-admitted` alone. A line holding `%%{` is a directive line, below, not a comment.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines and to comments refused for `:::` or `@{`, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

## Reasoning

§4.9's own example: `%% ::: direction LR` is `not-admitted` alone. The line matches `comment`, is refused by §4.2 rule 3 for `:::`, and is still a comment for §4.9's exemption.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
- `stray-direction`: The line matches `comment`; a comment refused by §4.2 rule 3 for `:::` or `@{` is exempt (§4.9, §9).
