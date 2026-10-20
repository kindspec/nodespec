# boundary/reserved-word-capitalised-accepted

**Expected:** accepted.

**Twin:** `boundary/reserved-word-end-as-node-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
End[E]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> Nothing is normalised. Ids and keywords compare exactly, by code point, so `End` and `end` are different words.

§4.4:

> An id is refused as `reserved-id` when it is one of these words, compared exactly:

## Reasoning

`End` is not `end`: ids compare exactly.
