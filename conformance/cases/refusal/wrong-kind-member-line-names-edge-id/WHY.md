# refusal/wrong-kind-member-line-names-edge-id

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `e1`).

## Input

````text
flowchart TD
a[A]
b[B]
a e1@--> b
subgraph s
  e1
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`: `style e1 …` where `e1` is an edge id, since Mermaid drops a style on an edge without a word; `class a b` where `b` is a node; an edge to an edge id or a class; a member line naming an edge id.

§5.2:

> | member line | its id | node or subgraph (D3) |

## Reasoning

A member line may name a node or a subgraph; `e1` is an edge id.

## Other identifiers

- `undeclared-id`: `e1` is declared.
