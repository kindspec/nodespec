# applicability/comment-with-quote-before-header

**Expected:** refused. Identifiers that apply: `no-header`; `malformed-line`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
%% x="y"
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment holding `="` is not a comment either, because Mermaid rewrites quotes before it removes comments (§4.5), so `="` in a comment changes a later label; such a line is a statement line. After the header it is `malformed-line`; before the header it is the first statement line, and §4.3's header rule makes it `no-header`.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

The comment holding `="` is the first statement line (`no-header`); then `flowchart TD` is read as a later statement line and matches nothing.

## Other identifiers

- `not-admitted`: The `"` is followed by `y`.
