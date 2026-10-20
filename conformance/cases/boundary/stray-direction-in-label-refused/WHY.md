# boundary/stray-direction-in-label-refused

**Expected:** refused. Identifiers that apply: `stray-direction`.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

**Twin:** `boundary/stray-direction-glued-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/stray-direction-in-comment-accepted`, which differs from this file by 7 byte edits (Levenshtein distance over bytes).

**Twin:** `boundary/stray-direction-lower-case-second-letter-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/stray-direction-capital-d-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

**Twin:** `boundary/stray-direction-lower-case-direction-word-accepted`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[go direction LR]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> What it swallows is gone: `a[go direction LR]` declares no node, an edge labelled `|direction RL|` is no edge, and a member line ending in `direction` followed by a line starting with `LR` holds neither.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> The text may stand anywhere in the line: in a label, a title, a style, an id (`xdirection LRX` matches). `stray-direction` applies whatever else applies to the line. Comment lines are exempt because Mermaid removes them before it lexes.

## Reasoning

§4.9's own example. The line matches `node-stmt` as well, but is refused and declares nothing.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`.
- `undeclared-id`: Nothing names `a`.
