# grammar/nesting-by-member-line-nested-block-later

**Expected:** accepted.

## Input

````text
flowchart LR
a[A]
b[B]
subgraph outer [Outer]
  inner
  a
end
subgraph inner [Inner]
  b
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph. Mermaid nests a subgraph named on a member line as it nests a block written inside another, whichever of the two blocks comes first in the file.

§5.2:

> | member line | its id | node or subgraph (D3) |

§6:

> Nesting has no cycle. Following holders from a subgraph never returns to it. A cycle is refused as `membership-cycle`; a member line naming its own block's subgraph is a cycle of one.

## Reasoning

The member line `inner` names a declared subgraph and nests it in `outer`, although `inner`'s block comes later. Holders: inner and a in outer, b in inner. No id is on two member lines and no chain of holders returns to its start.
