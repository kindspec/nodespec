# grammar/shape-doublecircle

**Expected:** accepted.

## Input

````text
flowchart LR
a(((A)))
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A node statement is an id and a shape, with nothing between them: `a [A]` does not parse in Mermaid. The shapes are Mermaid's classic fourteen:

§4.5:

> | `a>A]` | odd | | `a(((A)))` | doublecircle |

§4.1:

> node-stmt = *WSP id shape *WSP

§4.3:

> Matches `node-stmt`: in a block, `declaration-in-block`; at the top level, a node statement, which declares a node (§5.1).

## Reasoning

`a(((A)))` is the table's own example of this shape: the id `a`, then the shape's delimiters around the unquoted label `A`, with nothing between id and shape. Its delimiters hold no label character that could make another alternative of `shape` match instead, since `lchar` excludes `[ ] ( ) { }` and `lead` excludes `/` and `\`. At the top level it is a node statement declaring `a`.
