# grammar/header-without-direction

**Expected:** accepted.

## Input

````text
flowchart
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

§4.3:

> A header in another case (`Flowchart`), with another direction (`td`, `<`, `v`), with `flowchart-elk`, or with a `;` after it does not match. The direction is optional, as in the spike's subset.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

## Reasoning

The direction in `header` is optional (`[ 1*WSP dir ]`), and §4.3 says so in prose, marked provisional. `flowchart` alone is the header; `a[A]` is a node statement.
