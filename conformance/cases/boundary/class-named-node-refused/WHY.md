# boundary/class-named-node-refused

**Expected:** refused. Identifiers that apply: `reserved-id` (id `node`).

**Pins the provisional reading (§12):** `default`, `direction` and `hasOwnProperty` are reserved, ids of the form `L_…_…_N` are reserved, and a class may not be `node` (§4.4).

**Twin:** `boundary/class-named-nodes-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
node[N]
classDef node fill:#f9f
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> A class may not be `node` (provisional): a `classDef` or `class` naming the class `node` is refused as `reserved-id`.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

A `classDef` naming the class `node`. The refused line declares nothing, so `node` has one declaration.

## Other identifiers

- `kind-clash`: The `classDef` line is refused and declares nothing.
