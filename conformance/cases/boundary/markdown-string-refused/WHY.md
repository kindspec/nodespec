# boundary/markdown-string-refused

**Expected:** refused. Identifiers that apply: `not-admitted`.

**Twin:** `boundary/quoted-label-space-then-backtick-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a["`x`"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> does not begin with `` ` ``: `` "`…`" `` is a Markdown string, which is not admitted (§4.10);

§4.3:

> Holds `:::` or `@{`, or a `"` directly followed by `` ` ``: `not-admitted`.

§4.10:

> Markdown strings, `` "`…`" `` in a node or edge label, which the spike's subset left out.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.10:

> Label text in a line that matches its production is just text (provisional): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]` and `subgraph s ["a@{b"]` each match, are accepted, and Mermaid reads each as a label or title holding those characters. The rule is about the line, not the characters: `a[x:::y] q` matches no production, so rule 11 reaches it and it is `not-admitted`, though its `:::` is label text. A Markdown string never matches a node or edge label (§4.5), so in a node or edge statement it is always `not-admitted`.

## Reasoning

A quoted text may not begin with a backtick, so `node-stmt` fails; rule 11 finds `"` then backtick.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
