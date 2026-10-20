# examples/s7-class-before-style-refused

**Expected:** refused. Identifiers that apply: `class-not-last`.

## Input

````text
flowchart TD
a[A]
subgraph s
  a
end
classDef c fill:#f9f
class s c
style s fill:#eee
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> `class s c` followed by `style s …`, `a --> s` or a member line `s` renders `s` without `c`.

§7:

> Every `class` line comes after every other statement line. That is 0001's "with class lines last", read literally. A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.

## Reasoning

§7's example of `class s c` followed by `style s …`. `class s c` has `style s fill:#eee`, a statement line that is not a `class` line, after it.

## Other identifiers

- `styled-twice`: `s` has one `class` line and one `style` line.
- `statement-in-block`: The `class` and `style` lines are at the top level.
