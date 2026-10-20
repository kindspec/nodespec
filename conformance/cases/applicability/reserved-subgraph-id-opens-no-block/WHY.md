# applicability/reserved-subgraph-id-opens-no-block

**Expected:** refused. Identifiers that apply: `reserved-id` (id `graph`); `malformed-line`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
a[A]
subgraph graph
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `reserved-id` applies wherever an id stands in a line that §4.3 classifies as a statement and refuses for nothing else: in a declaration and wherever it is named. A reserved word in a line that is refused for another reason, such as a bare `graph` at the top level (`malformed-line`), is not also `reserved-id` (§9).

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

The subgraph line matches and is refused only as `reserved-id`, so it opens no block.

## Other identifiers

- `subgraph-without-id`: The line has the explicit id `graph`.
