# refusal/malformed-line-markdown-subgraph-title

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them; label text in a line that matches its production is just text; and where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal, for example `malformed-line` in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style`, and `link-style` in a `linkStyle` line (§4.10).

## Input

````text
flowchart TD
subgraph s ["`T`"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.10:

> Where an earlier rule of §4.3 decides a line that does not match, the text gets that rule's refusal (provisional): for example, in a line whose first word is `subgraph`, `end`, `direction`, `classDef`, `class` or `style` it is `malformed-line` (a subgraph title in Markdown included), and in a `linkStyle` line it is `link-style`.

§4.7:

> Any other top-level line whose first word is `subgraph` and that does not match `subgraph-line` is `malformed-line`.

§4.5:

> does not begin with `` ` ``: `` "`…`" `` is a Markdown string, which is not admitted (§4.10);

## Reasoning

The first word is `subgraph`, so §4.3 rule 1 decides the line. The title is not a quoted label (it begins with a backtick), so the line does not match `subgraph-line`, and it is `malformed-line`; §4.10 names a subgraph title in Markdown. The refused line opens no block.

## Other identifiers

- `not-admitted`: Rule 1 decides the line before rule 11.
- `subgraph-without-id`: The only `WSP` before the first `[` is followed by it.
- `unbalanced-block`: No block is opened.
