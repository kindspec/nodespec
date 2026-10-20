# refusal/link-style-holding-triple-colon

**Expected:** refused. Identifiers that apply: `link-style`.

## Input

````text
flowchart TD
a[A]
b[B]
a --> b
linkStyle 0 stroke:#f00 :::x
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.10:

> Where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal (provisional): for example, in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style` it is `malformed-line` (a subgraph title in Markdown included), and in a `linkStyle` line it is `link-style`.

§4.3:

> First word `linkStyle`: `link-style`.

## Reasoning

Rule 5 decides a line whose first word is `linkStyle`, and §4.10 says the same text there is `link-style`.

## Other identifiers

- `not-admitted`: Rule 5 comes before rule 11.
