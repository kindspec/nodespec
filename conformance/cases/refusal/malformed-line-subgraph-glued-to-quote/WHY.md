# refusal/malformed-line-subgraph-glued-to-quote

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
subgraph"x"
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> After the header, the first word of a statement line is its text after leading `WSP`, up to the next `WSP` or the end of the line.

§4.3:

> First word `subgraph`: in a block, `nested-block`, whether or not the line is well formed. At the top level, §4.7: it opens a block, or is `subgraph-without-id`, or is `malformed-line`.

§4.3:

> Anything else: `malformed-line`.

## Reasoning

The first word is the text up to the next `WSP`, so it is `subgraph"x"`, not `subgraph`, and rule 1 does not apply. No production matches (`subgraph"x"` is no id and no node statement), and the line has no `"` followed by a backtick, so rule 12 makes it `malformed-line`.

## Other identifiers

- `subgraph-without-id`: Its definition needs a first word of `subgraph`.
- `reserved-id`: No id stands in a matching line.
- `not-admitted`: No rule 11 form.
