# boundary/markdown-string-in-edge-label-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
b[B]
a -->|"`x`"| b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> A Markdown string never matches a node or edge label (§4.5), so in a node or edge statement it is always `not-admitted` (§4.3 rule 11).

§4.10:

> Markdown strings, `` "`…`" `` in a node or edge label, which the spike's subset left out.

§4.3:

> Holds a `"` directly followed by `` ` ``, a Markdown string: `not-admitted`.

## Reasoning

A Markdown string never matches a node or edge label, so in an edge statement it is always `not-admitted`.

## Other identifiers

- `malformed-line`: Rule 11 finds `"` then a backtick before rule 12.
