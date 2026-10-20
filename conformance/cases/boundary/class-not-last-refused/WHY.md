# boundary/class-not-last-refused

**Expected:** refused. Identifiers that apply: `class-not-last`.

**Pins the provisional reading (§12):** Every `class` line comes last (§7).

**Twin:** `boundary/class-last-accepted`, which differs from this file by one line, `a --> b`, moved below `class a hot`.

## Input

````text
flowchart TD
a[A]
b[B]
classDef hot fill:#f96
class a hot
a --> b
%% a trailing comment

class b hot
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> Every `class` line comes after every other statement line (provisional). That is 0001's "with class lines last", read literally. A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.

## Reasoning

`class a hot` has the edge statement `a --> b` after it. `class b hot` has nothing but `class` lines after it.

## Other identifiers

- `styled-twice`: `a` and `b` are each on one `class` line.
