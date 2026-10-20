# boundary/comment-equals-space-quote-accepted

**Expected:** accepted.

**Twin:** `boundary/comment-equals-quote-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% x= "y"
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> a `comment` does not hold `="` (§4.2);

## Reasoning

No `="` (a space separates them).
