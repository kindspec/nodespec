# grammar/edge-ids

**Expected:** accepted.

## Input

````text
flowchart LR
a[A]
b[B]
c[C]
a e1@--> b
b e2@-.-> c
a e3@--> c e4@==> b
classDef hot stroke:#f00
class e1 hot
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge statement is a group of ids, then one or more links, each followed by a group. A link may carry an edge id directly before it, `a e1@--> b`, and a label directly after it, `a -->|yes| b`.

§4.1:

> edge-stmt = *WSP group 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP group ) *WSP

§5.1:

> | `id@` before a link in an edge statement | edge |

§4.6:

> An edge id is declared by the one edge that carries it (D1). So an edge id is allowed only on a link with one id on each side. An edge id on a link with `&` in the group before it or after it is refused as `edge-id-on-group` (provisional).

§5.2:

> | `class` | each target | node, subgraph or edge (D1) |

## Reasoning

`id "@"` directly before a link declares an edge id. Each link carrying one has a single id on each side, including both links of the chain `a e3@--> c e4@==> b`. `e1` to `e4` are declared once each, as edges. `class e1 hot` targets an edge, which a `class` target may be, and is the last statement line.
