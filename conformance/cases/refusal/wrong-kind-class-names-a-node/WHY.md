# refusal/wrong-kind-class-names-a-node

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `b`).

## Input

````text
flowchart TD
a[A]
b[B]
class a b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> A statement that names an id declared as a kind it may not name is refused as `wrong-kind`: `style e1 …` where `e1` is an edge id, since Mermaid drops a style on an edge without a word; `class a b` where `b` is a node; an edge to an edge id or a class; a member line naming an edge id.

§5.2:

> | `class` | its last id, the class | class |

§5.2:

> A `class` statement's targets are the ids before its last one.

## Reasoning

The last id of a `class` line is its class and may only be a class; `b` is a node.

## Other identifiers

- `undeclared-id`: Both ids are declared.
- `class-not-last`: The `class` line is last.
