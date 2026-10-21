# boundary/label-text-double-colon-in-unquoted-node-label-accepted

**Expected:** accepted.

**Twin:** `boundary/label-text-triple-colon-in-unquoted-node-label-refused`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
c[x::y]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> And a line that holds `:::` or `@{` is `not-admitted` before any production is tried (§4.2 rule 3), so a label that the grammar admits holding them, such as `a[x:::y]`, is still refused.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.1:

> lchar = HTAB / %x20-21 / %x23-27 / %x2A-3F / %x41-5A / %x5C / %x5E-7A / %x7E / nonascii ; a label character: not [ ] ( ) { } | " @

## Reasoning

Two colons are not `:::`, and `:` is an `lchar`: an ordinary node statement. One byte from the refused `c[x:::y]`.
