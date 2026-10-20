# examples/s4-2-directive-in-comment-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
b[B]
%% see %%{x
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> a comment `%% see %%{x` above an edge statement removes the edge.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

## Reasoning

§4.2's example comment. Line 4 holds `%%{`, so §4.2 rule 3 refuses it as `not-admitted` before rule 5 could read it as a comment. The edge after it is an ordinary edge statement.

## Other identifiers

- `no-header`: The directive line is not a statement line, and the header is line 1.
- `malformed-line`: Rule 3 classifies the line first.
