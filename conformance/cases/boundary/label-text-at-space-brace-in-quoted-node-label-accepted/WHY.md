# boundary/label-text-at-space-brace-in-quoted-node-label-accepted

**Expected:** accepted.

**Twin:** `boundary/label-text-at-brace-in-quoted-node-label-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
c["x@ {y"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.1:

> qchar = HTAB / %x20-21 / %x23-7E / nonascii ; not "

## Reasoning

`@` and `{` with a space between are not `@{`; the quoted label holds only `qchar`s. One byte from the refused `c["x@{y"]`.
