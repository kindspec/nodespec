# applicability/direction-phrase-before-directive-in-label

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
a[go direction LR %%{x}%%]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.9:

> Text outside the span is lexed: `a[go direction LR %%{x}%%]` declares no node. A directive line holding the text is refused as both `not-admitted` and `stray-direction`, even where the text stands inside the removed span and Mermaid swallows nothing, as in `%%{init: {"theme": "direction LR"}}%%`.

## Reasoning

§4.9's own example: the line holds `%%{`, so §4.2 rule 3 makes it a directive (`not-admitted`), and it holds `direction LR`, which a directive line is not exempt from.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line.
- `undeclared-id`: Nothing names `a`.
