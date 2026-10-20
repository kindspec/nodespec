# applicability/stray-direction-inside-an-id

**Expected:** refused. Identifiers that apply: `malformed-line`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
xdirection LRX
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> The text may stand anywhere in the line: in a label, a title, a style, an id (`xdirection LRX` matches). `stray-direction` applies whatever else applies to the line. Comment lines are exempt because Mermaid removes them before it lexes.

## Reasoning

§4.9's own example `xdirection LRX` matches; the line also matches no production.

## Other identifiers

- `reserved-id`: No reserved word, and the line is refused anyway.
