# refusal/not-admitted-directive

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
%%{init: {"theme": "dark"}}%%
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive: the line holds `%%{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10).

§4.10:

> Directives, any line holding `%%{` (§4.2 rule 3).

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

Line 1 holds `%%{` and is refused as `not-admitted` by §4.2 rule 3. It is not a statement line, so line 2 is the first statement line and the header.

## Other identifiers

- `no-header`: The directive line is classified by rule 3, not as a statement line; the header is line 2.
- `malformed-line`: Rule 3 classifies the line before rule 6 could make it a statement line.
