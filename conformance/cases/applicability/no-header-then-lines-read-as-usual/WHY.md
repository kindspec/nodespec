# applicability/no-header-then-lines-read-as-usual

**Expected:** refused. Identifiers that apply: `no-header`; `undeclared-id` (id `b`).

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** After a `no-header` line, the lines that follow are read as if a header stood there; the header's direction is optional; and `flowchart-elk` is not admitted (§4.3).

## Input

````text
Flowchart TD
a[A]
a --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

§9:

> So `a[A] --> b` declares nothing; a node statement in a block declares nothing, and an edge naming that node is `undeclared-id` too; a refused `subgraph` line opens no block, so its member lines are top-level `malformed-line` and its `end` is `unbalanced-block`; and a `no-header` line is followed by lines read as usual.

## Reasoning

After the `no-header` line, `a[A]` declares and `a --> b` names an undeclared `b`.

## Other identifiers

- `malformed-line`: `a[A]` and `a --> b` are read as if a header stood before them.
