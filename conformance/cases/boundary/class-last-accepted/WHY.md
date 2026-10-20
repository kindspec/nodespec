# boundary/class-last-accepted

**Expected:** accepted.

**Twin:** `boundary/class-not-last-refused`, which differs from this file by one line, `a --> b`, moved below `class a hot`.

## Input

````text
flowchart TD
a[A]
b[B]
classDef hot fill:#f96
a --> b
class a hot
%% a trailing comment

class b hot
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§7:

> Every `class` line comes after every other statement line. That is 0001's "with class lines last", read literally. A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.

## Reasoning

After each `class` line come only a comment, a blank line and another `class` line.
