# boundary/header-capitalised-refused

**Expected:** refused. Identifiers that apply: `no-header`.

**Twin:** `boundary/header-spaced-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
Flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A header in another case (`Flowchart`), with another direction (`td`, `<`, `v`), with `flowchart-elk`, or with a `;` after it does not match. The direction is optional, as in the spike's subset (provisional).

§4.1:

> String literals are case-sensitive, as RFC 7405's `%s` prefix marks them; this document leaves the prefix out for readability.

## Reasoning

A header in another case does not match.

## Other identifiers

- `malformed-line`: The first statement line is judged by the header rule alone; `a[A]` after it is a node statement.
