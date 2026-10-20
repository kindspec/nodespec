# boundary/comment-equals-quote-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/comment-equals-space-quote-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% x="y"
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment holding `="` is not a comment either, because Mermaid rewrites quotes before it removes comments (§4.5), so `="` in a comment changes a later label; such a line is a statement line. After the header it is `malformed-line`; before the header it is the first statement line, and §4.3's header rule makes it `no-header`.

§4.1:

> a `comment` does not hold `="` (§4.2);

## Reasoning

A comment holding `="` is a statement line, and after the header `malformed-line`.

## Other identifiers

- `not-admitted`: No `%%{`, and the `"` is followed by `y`.
