# boundary/percent-pair-alone-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/comment-with-a-space-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%%
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A line holding only `%%`, with nothing after it, is not a comment; Mermaid reads it as a node named `%%`.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

§4.3:

> Anything else: `malformed-line`.

## Reasoning

A line of only `%%` is a statement line after the header, and matches no production.

## Other identifiers

- `not-admitted`: The line holds no `%%{`.
