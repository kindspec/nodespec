# applicability/directive-looking-like-comment-ending-in-direction

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
a[A]
%% x %%{y}%% direction
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Each line is classified by the first rule below that matches it. A line that is classified is never also read as something else.

§4.2:

> A directive: the line holds `%%{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10).

§4.9:

> A directive line is not exempt (provisional): Mermaid removes only the text its directive pattern matches and lexes the rest.

§4.9:

> with trailing whitespace removed, it ends in `direction`.

## Reasoning

Rule 3 makes the line a directive before rule 5 could read it as a comment. Not being a comment, it is not exempt, and with trailing whitespace removed it ends in `direction`.

## Other identifiers

- `malformed-line`: Rule 3 classifies the line first.
