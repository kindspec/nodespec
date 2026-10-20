# refusal/wrong-kind-style-on-edge-id

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
a e1@--> b
style e1 stroke:#f00
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`: `style e1 …` where `e1` is an edge id, since Mermaid drops a style on an edge without a word; `class a b` where `b` is a node; an edge to an edge id or a class; a member line naming an edge id.

§5.2:

> | `style` | its target | node or subgraph (D1) |

§5.2:

> `wrong-kind` applies to a name only when the id is declared and none of its declarations is of a kind that place may name.

## Reasoning

`style` may name a node or a subgraph, and `e1` is declared only as an edge.

## Other identifiers

- `undeclared-id`: `e1` is declared.
