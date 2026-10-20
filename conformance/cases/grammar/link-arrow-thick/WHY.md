# grammar/link-arrow-thick

**Expected:** accepted.

## Input

````text
flowchart LR
a[A]
b[B]
c[C]
a ==> b
a ===> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> | `==>`, `===>`, … | arrow, thick |

§4.1:

> link = 2*"-" ">" / 3*"-" / 2*"-" "o" / 2*"-" "x" / "<" 2*"-" ">" / "o" 2*"-" "o" / "x" 2*"-" "x" / "-" 1*"." "->" / "-" 1*"." "-" / 2*"=" ">" / 3*"=" / 3*"~"

§4.1:

> edge-stmt = *WSP group 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP group ) *WSP

§4.3:

> Matches `edge-stmt`: in a block, `statement-in-block`; at the top level, an edge statement (§4.6).

§5.2:

> | edge statement | each id of its groups | node or subgraph |

## Reasoning

Each edge line is `id 1*WSP link 1*WSP id`, with a link from this row of §4.6's table in its shortest form and a longer one; each matches an alternative of `link`. Every end is a declared node. No two edges share start, end and link, so `duplicate-edge` does not apply.
