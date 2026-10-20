# applicability/direction-phrase-before-directive-in-label

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
a[go direction LR %%{x}%%]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive: the line holds `%%{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10).

§4.9:

> Text outside the span is lexed: `a[go direction LR %%{x}%%]` declares no node. A directive line holding the text is refused as both `not-admitted` and `stray-direction`, even where the text stands inside the removed span and Mermaid swallows nothing, as in `%%{init: {"theme": "direction LR"}}%%`.

## Reasoning

§4.9's own example: the line holds `%%{`, so §4.2 rule 3 makes it a directive (`not-admitted`), and it holds `direction LR`, which a directive line is not exempt from.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line.
- `undeclared-id`: Nothing names `a`.
