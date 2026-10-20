# grammar/header-only

**Expected:** accepted.

## Input

````text
flowchart TD
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

§9:

> A file is either in the profile or refused. This list is complete: every refusal draft 0 has is below.

## Reasoning

The only line is the first statement line, and it matches `header` with the direction `TD`. No §9 entry requires a node, an edge or a block, and §9's list is complete, so the file is in the profile.
