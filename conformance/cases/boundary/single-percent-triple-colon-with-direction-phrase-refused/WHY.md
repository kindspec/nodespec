# boundary/single-percent-triple-colon-with-direction-phrase-refused

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Twin:** `boundary/comment-triple-colon-with-direction-phrase-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
% use ::: direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> comment = *WSP "%%" ( HTAB / %x20-7A / %x7C-7E / nonascii ) *cchar ; next is not "{"

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.9:

> That includes a line that matches `comment` but is refused by §4.2 rule 3 for holding `:::` or `@{`: Mermaid removes it all the same, so `%% ::: direction LR` is `not-admitted` alone. A line holding `%%{` is a directive line, below, not a comment.

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines and to comments refused for `:::` or `@{`, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

## Reasoning

One `%` is not `%%`, so the line does not match `comment`. §4.2 rule 3 refuses it for `:::`; as it is no comment, the exemption does not reach it. It holds `direction`, a space, `LR`, and `stray-direction` applies whatever else applies to the line.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
