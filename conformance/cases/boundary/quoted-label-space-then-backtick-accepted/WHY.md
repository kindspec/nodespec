# boundary/quoted-label-space-then-backtick-accepted

**Expected:** accepted.

**Twin:** `boundary/markdown-string-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[" `x`"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> does not begin with `` ` ``: `` "`…`" `` is a Markdown string, which is not admitted (§4.10);

§4.1:

> a `quoted` label holds at least one character that is not `WSP`, does not begin with `` ` ``, and does not end with `=` (§4.5);

## Reasoning

The text begins with a space; the node statement matches, so rule 11 is not reached.
