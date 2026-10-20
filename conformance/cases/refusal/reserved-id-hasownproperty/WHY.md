# refusal/reserved-id-hasownproperty

**Expected:** refused. Identifiers that apply: `reserved-id` (id `hasOwnProperty`).

**Pins the provisional reading (§12):** `default`, `direction` and `hasOwnProperty` are reserved, ids of the form `L_…_…_N` are reserved, and a class may not be `node` (§4.4).

## Input

````text
flowchart TD
hasOwnProperty[H]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `hasOwnProperty` is reserved too (provisional).

## Reasoning

A node statement declaring `hasOwnProperty`.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`; `hasOwnProperty` is an `id`.
- `stray-direction`: No `direction`.
