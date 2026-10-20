# grammar/nesting-by-member-line-nested-block-first

**Expected:** accepted.

## Input

````text
flowchart LR
a[A]
subgraph inner
  a
end
subgraph outer
  inner
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph. Mermaid nests a subgraph named on a member line as it nests a block written inside another, whichever of the two blocks comes first in the file.

§5.2:

> | member line | its id | node or subgraph (D3) |

## Reasoning

The same nesting with the nested block first. A name may be declared before or after it (§5.2), and §6 nests "whichever of the two blocks comes first".
