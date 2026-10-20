# applicability/stray-direction-with-declaration-in-edge

**Expected:** refused. Identifiers that apply: `declaration-in-edge`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
b[B]
a[go direction LR] --> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

§4.9:

> The text may stand anywhere in the line: in a label, a title, a style, an id (`xdirection LRX` matches). `stray-direction` applies whatever else applies to the line. Comment lines are exempt because Mermaid removes them before it lexes.

## Reasoning

`stray-direction` applies whatever else applies to the line.

## Other identifiers

- `undeclared-id`: The refused line names nothing.
- `malformed-line`: The line matches `edge-decl`.
