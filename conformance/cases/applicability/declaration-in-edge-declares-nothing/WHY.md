# applicability/declaration-in-edge-declares-nothing

**Expected:** refused. Identifiers that apply: `declaration-in-edge`; `undeclared-id` (id `a`).

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
b[B]
c[C]
a[A] --> b
c --> a
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

## Reasoning

The refused line declares nothing, so `c --> a` names an undeclared `a`.

## Other identifiers

- `malformed-line`: The line matches `edge-decl`.
- `wrong-kind`: `a` is not declared at all.
