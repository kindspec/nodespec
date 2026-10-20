# refusal/reserved-id-hasownproperty

**Expected:** refused. Identifiers that apply: `reserved-id` (id `hasOwnProperty`).

## Input

````text
flowchart TD
hasOwnProperty[H]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.4:

> `hasOwnProperty` is reserved too.

## Reasoning

A node statement declaring `hasOwnProperty`.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`; `hasOwnProperty` is an `id`.
- `stray-direction`: No `direction`.
