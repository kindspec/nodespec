# applicability/reserved-word-in-malformed-line

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
a[A]
graph
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `reserved-id` applies wherever an id stands in a line that §4.3 classifies as a statement and refuses for nothing else: in a declaration and wherever it is named. A reserved word in a line that is refused for another reason, such as a bare `graph` at the top level (`malformed-line`), is not also `reserved-id` (§9).

§4.3:

> A bare id at the top level matches `member-line`, and is `malformed-line` there.

## Reasoning

§4.4's own example: a bare `graph` is `malformed-line` and not also `reserved-id`.

## Other identifiers

- `reserved-id`: Applies only to a line nothing else refuses.
