# grammar/header-graph-lr

**Expected:** accepted.

## Input

````text
graph LR
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

§4.1:

> dir = "TB" / "TD" / "BT" / "LR" / "RL"

§4.3:

> Matches `node-stmt`: in a block, `declaration-in-block`; at the top level, a node statement, which declares a node (§5.1).

## Reasoning

`graph` is the header's other keyword and `LR` one of the five `dir` values. `a[A]` is a top-level node statement.
