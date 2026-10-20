# boundary/comment-double-colon-with-direction-phrase-accepted

**Expected:** accepted.

**Twin:** `boundary/comment-triple-colon-with-direction-phrase-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% use :: direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment matches `comment`. It is allowed anywhere, inside a block included (provisional, as are blank lines in a block), and is otherwise ignored.

§4.9:

> So a line other than a comment, a front matter line or a line that matches `direction-stmt` is refused as `stray-direction` when:

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

## Reasoning

No `:::`, so this is an ordinary comment, exempt from `stray-direction`.
