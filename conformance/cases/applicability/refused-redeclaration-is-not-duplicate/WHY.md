# applicability/refused-redeclaration-is-not-duplicate

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Which refusals apply once a line is refused, and that refusals of a line or a file carry no id (§9).

## Input

````text
flowchart TD
a[A]
a[B];
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

§4.3:

> `;` is not admitted anywhere outside a label (the owner, 2026-10-19: refused for now), so a statement line ending in `;`, two statements on one line, and a member line `a;` are `malformed-line`, and a header ending in `;` is `no-header`.

## Reasoning

The second line is refused and declares nothing.

## Other identifiers

- `duplicate-declaration`: Only unrefused lines declare.
