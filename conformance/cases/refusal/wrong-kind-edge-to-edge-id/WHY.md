# refusal/wrong-kind-edge-to-edge-id

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
a e1@--> b
a --> e1
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`: `style e1 …` where `e1` is an edge id, since Mermaid drops a style on an edge without a word; `class a b` where `b` is a node; an edge to an edge id or a class; a member line naming an edge id.

§5.2:

> | edge statement | each id of its groups | node or subgraph |

§5.2:

> `wrong-kind` applies to a name only when the id is declared and none of its declarations is of a kind that place may name.

## Reasoning

§5.2's own example, an edge to an edge id: an edge end may be a node or a subgraph, and `e1` is declared only as an edge.

## Other identifiers

- `undeclared-id`: `e1` is declared.
- `duplicate-edge`: a→b and a→e1 differ in end.
