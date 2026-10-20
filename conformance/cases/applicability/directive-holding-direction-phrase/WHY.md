# applicability/directive-holding-direction-phrase

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
%%{init: {"theme": "direction LR"}}%%
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.9:

> A directive line is not exempt: Mermaid removes only the text its directive pattern matches and lexes the rest.

§4.9:

> Text outside the span is lexed: `a[go direction LR %%{x}%%]` declares no node. A directive line holding the text is refused as both `not-admitted` and `stray-direction`, even where the text stands inside the removed span and Mermaid swallows nothing, as in `%%{init: {"theme": "direction LR"}}%%`.

## Reasoning

§4.9's own example: a directive line holding the text is refused as both, although Mermaid swallows nothing here.

## Other identifiers

- `no-header`: The directive line is not a statement line; line 2 is the header.
