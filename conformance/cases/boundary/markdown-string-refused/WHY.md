# boundary/markdown-string-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/quoted-label-space-then-backtick-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a["`x`"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> does not begin with `` ` ``: `` "`…`" `` is a Markdown string, which is not admitted (§4.10);

§4.3:

> Holds a `"` directly followed by `` ` ``, a Markdown string: `not-admitted`.

§4.10:

> Markdown strings, `` "`…`" `` in a node or edge label, which the spike's subset left out.

§4.10:

> A Markdown string never matches a node or edge label (§4.5), so in a node or edge statement it is always `not-admitted` (§4.3 rule 11).

## Reasoning

A quoted text may not begin with a backtick, so `node-stmt` fails; rule 11 finds `"` then backtick.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
