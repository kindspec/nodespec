# boundary/label-text-at-brace-in-unquoted-edge-label-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Pins the provisional reading (§12):** `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them; label text in a line that matches its production is just text; and where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal, for example `malformed-line` in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style`, and `link-style` in a `linkStyle` line (§4.10).

**Twin:** `boundary/label-text-at-brace-in-quoted-edge-label-accepted`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a -->|x@{y| b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> Label text in a line that matches its production is just text (provisional): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]` and `subgraph s ["a@{b"]` each match, are accepted, and Mermaid reads each as a label or title holding those characters. The rule is about the line, not the characters: `a[x:::y] q` matches no production, so rule 11 reaches it and it is `not-admitted`, though its `:::` is label text. A Markdown string never matches a node or edge label (§4.5), so in a node or edge statement it is always `not-admitted`.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.3:

> Holds `:::` or `@{`, or a `"` directly followed by `` ` ``: `not-admitted`.

## Reasoning

Unquoted, the label may not hold `@` or `{`, so the line matches nothing and rule 11 finds `@{`.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
