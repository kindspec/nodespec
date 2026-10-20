# boundary/front-matter-holding-direction-phrase-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
---
title: go direction LR
---
flowchart TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Front matter. If the file's first line is `---`, with any `WSP` before or after it, that line and every line up to and including the next such line, or to the end of the file if there is none, are refused together as `not-admitted` (§4.10).

§4.9:

> Front matter lines are exempt too (provisional): Mermaid removes front matter before it lexes, so `title: go direction LR` in it swallows nothing (the file is still `not-admitted`, §4.2).

§9:

> `stray-direction` applies to a line whatever else applies to it, except to front matter lines, which §4.9 exempts; `reserved-id` applies only to a line that nothing else refuses (§4.4).

## Reasoning

§4.9's own example: `title: go direction LR` in front matter swallows nothing, and front matter lines are exempt from `stray-direction`. The three front-matter lines are `not-admitted`.

## Other identifiers

- `stray-direction`: Front matter lines are exempt (§4.9, §9).
- `no-header`: Line 4 is the header.
