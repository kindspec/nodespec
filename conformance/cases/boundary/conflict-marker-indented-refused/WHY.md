# boundary/conflict-marker-indented-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
 <<<<<<< ours
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.

## Reasoning

The first seven characters are a space and six `<`, so this is no conflict marker, and as a statement line it matches nothing.

## Other identifiers

- `conflict-marker`: The test is the line's first seven characters.
- `not-admitted`: No §4.10 form.
