# boundary/comment-triple-colon-and-percent-brace-with-direction-phrase-refused

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/comment-triple-colon-and-percent-brace-gap-with-direction-phrase-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% use ::: %%{ direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> That includes a line that matches `comment` but is refused by §4.2 rule 3 for holding `:::` or `@{`: Mermaid removes it all the same, so `%% ::: direction LR` is `not-admitted` alone. A line holding `%%{` is a directive line, below, not a comment.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.9:

> A directive line is not exempt: Mermaid removes only the text its directive pattern matches and lexes the rest.

## Reasoning

The line holds `%%{`, so it is a directive line, not a comment, and a directive line is not exempt. It holds `direction`, a space, `LR`, and `stray-direction` applies whatever else applies to the line.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
