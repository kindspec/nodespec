# refusal/reserved-id-direction

**Expected:** refused. Identifiers that apply: `reserved-id` (id `direction`).

## Input

````text
flowchart TD
direction[D]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `direction` is reserved too, and refused as `reserved-id`.

§4.3:

> After the header, the first word of a statement line is its text after leading `WSP`, up to the next `WSP` or the end of the line.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> with trailing whitespace removed, it ends in `direction`.

## Reasoning

The first word is `direction[D]`, not `direction`, so rule 3 does not apply; the line matches `node-stmt`.

## Other identifiers

- `stray-direction`: `direction` is followed by `[`, not whitespace, and the line ends in `]`.
- `malformed-line`: Rule 3 is for a first word of exactly `direction`.
