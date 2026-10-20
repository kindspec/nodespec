# applicability/stray-direction-suppresses-reserved-id

**Expected:** refused. Identifiers that apply: `stray-direction`.

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
end[go direction LR]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

§4.4:

> `reserved-id` applies wherever an id stands in a line that §4.3 classifies as a statement and refuses for nothing else: in a declaration and wherever it is named. A reserved word in a line that is refused for another reason, such as a bare `graph` at the top level (`malformed-line`), is not also `reserved-id` (§9).

## Reasoning

The line matches `node-stmt` with id `end`, but `stray-direction` refuses it, and `reserved-id` applies only to a line nothing else refuses.

## Other identifiers

- `reserved-id`: The line is refused by `stray-direction`.
