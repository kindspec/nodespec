# applicability/conflict-marker-holding-triple-colon

**Expected:** refused. Identifiers that apply: `conflict-marker`.

## Input

````text
flowchart TD
a[A]
<<<<<<< a:::b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.

§4.2:

> Each line is classified by the first rule below that matches it. A line that is classified is never also read as something else.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

## Reasoning

§4.2 rule 2 comes before rule 3: the line's first seven characters are `<`, so it is a conflict marker and is never also read under rule 3.

## Other identifiers

- `not-admitted`: A classified line is never also read as something else; rule 2 classified it.
