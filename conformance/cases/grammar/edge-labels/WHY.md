# grammar/edge-labels

**Expected:** accepted.

## Input

````text
flowchart LR
a[A]
b[B]
c[C]
a -->|yes| b
a -.->|"maybe [later]"| c
b ==>| padded | c
c ---|plain| a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge statement is a group of ids, then one or more links, each followed by a group. A link may carry an edge id directly before it, `a e1@--> b`, and a label directly after it, `a -->|yes| b`.

§4.1:

> edge-stmt = *WSP group 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP group ) *WSP

§4.1:

> label = unquoted / quoted unquoted = *WSP lead *lchar quoted = DQUOTE 1*qchar DQUOTE

## Reasoning

A label stands directly after its link between `|`s and is a `label`: `yes` and `plain` unquoted, ` padded ` unquoted with `*WSP` on both sides, and `"maybe [later]"` quoted, which may hold brackets. The `1*WSP` before the next group follows the closing `|`.
