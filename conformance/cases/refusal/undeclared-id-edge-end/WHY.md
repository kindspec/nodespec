# refusal/undeclared-id-edge-end

**Expected:** refused. Identifiers that apply: `undeclared-id` (id `b`).

## Input

````text
flowchart TD
a[A]
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.2:

> Every other place an id stands names it. A name must be declared, by a declaration anywhere in the file, before or after it; §7 orders `class` lines. An id that is named and not declared is refused as `undeclared-id`.

§5.2:

> | edge statement | each id of its groups | node or subgraph |

## Reasoning

`b` is named by the edge and declared nowhere.

## Other identifiers

- `wrong-kind`: Applies only to a declared id.
