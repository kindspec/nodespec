# refusal/wrong-kind-style-on-class

**Expected:** refused. Identifiers that apply: `wrong-kind` (id `c`).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
style c stroke:#333
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> | `style` | its target | node or subgraph (D1) |

§5.2:

> `wrong-kind` applies to a name only when the id is declared and none of its declarations is of a kind that place may name.

## Reasoning

`style` may name a node or a subgraph; `c` is declared only as a class.

## Other identifiers

- `undeclared-id`: `c` is declared.
- `styled-twice`: One `style` line.
