# refusal/styled-twice-style

**Expected:** refused. Identifiers that apply: `styled-twice` (id `a`).

**Pins the provisional reading (§12):** An id is the target of at most one `style` line and one `class` line, so with one class per `class` line an id carries at most one class (§7).

## Input

````text
flowchart TD
a[A]
style a fill:#f9f
style a stroke:#333
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> An id is the target of at most one `style` line and at most one `class` line (provisional). A second is refused as `styled-twice`.

## Reasoning

`a` is the target of two `style` lines.

## Other identifiers

- `malformed-line`: Both lines match `style-stmt`.
- `class-not-last`: There is no `class` line.
