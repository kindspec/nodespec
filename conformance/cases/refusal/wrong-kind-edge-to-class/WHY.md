# refusal/wrong-kind-edge-to-class

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `c`).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
a --> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`: `style e1 …` where `e1` is an edge id, since Mermaid drops a style on an edge without a word; `class a b` where `b` is a node; an edge to an edge id or a class; a member line naming an edge id.

§5.2:

> | edge statement | each id of its groups | node or subgraph |

## Reasoning

An edge end may be a node or a subgraph; `c` is declared only as a class.

## Other identifiers

- `kind-clash`: `c` has one declaration.
