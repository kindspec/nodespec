# boundary/comment-before-header-holding-at-space-brace-accepted

**Expected:** accepted.

**Twin:** `boundary/comment-before-header-holding-at-brace-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
%% see @ {x}
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment matches `comment`. It is allowed anywhere, inside a block included (provisional, as are blank lines in a block), and is otherwise ignored.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

## Reasoning

A comment before the header; `@ {` is not `@{`.
