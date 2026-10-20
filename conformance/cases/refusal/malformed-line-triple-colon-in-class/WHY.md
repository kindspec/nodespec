# refusal/malformed-line-triple-colon-in-class

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them; label text in a line that matches its production is just text; and where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal, for example `malformed-line` in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style`, and `link-style` in a `linkStyle` line (§4.10).

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f
class a c:::x
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.10:

> Where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal (provisional): for example, in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style` it is `malformed-line` (a subgraph title in Markdown included), and in a `linkStyle` line it is `link-style`.

§4.3:

> First word `classDef`, `class` or `style`: in a block, `statement-in-block`. At the top level, if the line matches `classdef-stmt`, `class-stmt` or `style-stmt` for its first word, it is that statement (§4.8); otherwise `malformed-line`.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

## Reasoning

The first word is `class`, so rule 4 decides the line, and `c:::x` is not an id.

## Other identifiers

- `not-admitted`: Rule 4 decides the line before rule 11.
- `class-not-last`: A refused line is not a `class` line.
