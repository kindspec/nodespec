# boundary/comment-triple-colon-and-percent-brace-gap-with-direction-phrase-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/comment-triple-colon-and-percent-brace-with-direction-phrase-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% use ::: %{ direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> That includes a line that matches `comment` but is refused by §4.2 rule 3 for holding `:::` or `@{`: Mermaid removes it all the same, so `%% ::: direction LR` is `not-admitted` alone. A line holding `%%{` is a directive line, below, not a comment.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.1:

> comment = *WSP "%%" ( HTAB / %x20-7A / %x7C-7E / nonascii ) *cchar ; next is not "{"

§4.1:

> cchar = HTAB / %x20-7E / nonascii

## Reasoning

`%{` is not `%%{`, so this is a comment (`{` is a `cchar`) holding `:::`: `not-admitted`, and exempt.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
- `stray-direction`: The line matches `comment`; a comment refused by §4.2 rule 3 for `:::` or `@{` is exempt (§4.9, §9).
