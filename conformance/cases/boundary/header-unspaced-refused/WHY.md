# boundary/header-unspaced-refused

**Expected:** refused. Identifiers that apply: `no-header`.

**Twin:** `boundary/header-spaced-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchartTD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

`1*WSP` must come before the direction.

## Other identifiers

- `malformed-line`: Header rule only.
