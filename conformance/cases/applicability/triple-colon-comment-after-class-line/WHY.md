# applicability/triple-colon-comment-after-class-line

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
class a c
%% note ::: here
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.10:

> A line that holds `:::` or `@{` is `not-admitted` wherever the characters stand, label text included (the owner, 2026-10-20): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]`, `subgraph s ["a@{b"]`, `style a fill:#f00 :::x`, `linkStyle 0 :::x` and a comment `%% use ::: here` are each `not-admitted`, although Mermaid reads the characters in a label as text. §4.2 rule 3 decides this before any rule of §4.3, so no first word changes it.

§7:

> Every `class` line comes after every other statement line. That is 0001's "with class lines last", read literally. A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.

§9:

> Every other rule (`duplicate-declaration`, `undeclared-id`, `wrong-kind`, `kind-clash`, `duplicate-edge`, `too-many-edges`, the end-of-file `unbalanced-block`, `member-twice`, `membership-cycle`, `class-not-last` and `styled-twice`) is checked on the lines that are not refused.

## Reasoning

The last line is refused by §4.2 rule 3 and is not a statement line, so the `class` line has no statement line after it.

## Other identifiers

- `malformed-line`: §4.2 rule 3 classifies the line before it could be a statement line, and a classified line is never read as something else.
- `class-not-last`: Only unrefused statement lines count, and the rule-3 line is neither.
