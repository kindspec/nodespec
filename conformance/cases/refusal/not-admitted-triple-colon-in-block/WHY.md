# refusal/not-admitted-triple-colon-in-block

**Expected:** refused. Identifiers that apply: `not-admitted`.

## Input

````text
flowchart TD
a[A]
subgraph s
  a:::c
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.10:

> So `:::`, `@{` and a Markdown string are `not-admitted` only where §4.3 rule 11 reaches them: in a line that matches none of §4.3's earlier rules, at the top level or in a block, for example where a label does not match its production.

§4.10:

> Label text in a line that matches its production is just text (provisional): `a[x:::y]`, `a["x@{y"]`, `a -->|x:::y| b`, `subgraph s [a:::b]` and `subgraph s ["a@{b"]` each match, are accepted, and Mermaid reads each as a label or title holding those characters. The rule is about the line, not the characters: `a[x:::y] q` matches no production, so rule 11 reaches it and it is `not-admitted`, though its `:::` is label text. A Markdown string never matches a node or edge label (§4.5), so in a node or edge statement it is always `not-admitted`.

§4.3:

> Holds `:::` or `@{`, or a `"` directly followed by `` ` ``: `not-admitted`.

## Reasoning

In a block, `a:::c` matches no production of rules 7 to 10, so rule 11 reaches it: `not-admitted`, in a block as at the top level.

## Other identifiers

- `malformed-line`: Rule 11 comes before rule 12.
- `statement-in-block`: The line is not an edge statement.
- `declaration-in-block`: The line does not match `node-stmt`.
