# boundary/reserved-word-end-as-node-refused

**Expected:** refused. Identifiers that apply: `reserved-id` (id `end`).

**Twin:** `boundary/reserved-word-capitalised-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
end[E]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> After the header, the first word of a statement line is its text after leading `WSP`, up to the next `WSP` or the end of the line.

§4.3:

> Matches `node-stmt`: in a block, `declaration-in-block`; at the top level, a node statement, which declares a node (§5.1).

§4.4:

> An id is refused as `reserved-id` when it is one of these words, compared exactly:

§4.4:

> `reserved-id` applies wherever an id stands in a line that §4.3 classifies as a statement and refuses for nothing else: in a declaration and wherever it is named. A reserved word in a line that is refused for another reason, such as a bare `graph` at the top level (`malformed-line`), is not also `reserved-id` (§9).

## Reasoning

The first word is `end[E]`, not `end`, so rule 2 does not apply; the line matches `node-stmt` and its id is `end`.

## Other identifiers

- `malformed-line`: Rule 2 needs a first word of exactly `end`.
- `unbalanced-block`: Same reason.
