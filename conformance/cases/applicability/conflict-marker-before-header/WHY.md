# applicability/conflict-marker-before-header

**Expected:** refused. Identifiers that apply: `conflict-marker`.

## Input

````text
<<<<<<< ours
flowchart TD
a[A]
=======
>>>>>>> theirs
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

Conflict-marker lines are not statement lines, so `flowchart TD` is the header.

## Other identifiers

- `no-header`: The first statement line is `flowchart TD`.
