# refusal/conflict-marker-pipes

**Expected:** refused. Identifiers that apply: `conflict-marker`.

## Input

````text
flowchart TD
a[A]
|||||||
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.

## Reasoning

Seven `|`: the diff3 base marker.

## Other identifiers

- `malformed-line`: §4.2 rule 2 classifies the line before it could be a statement line.
