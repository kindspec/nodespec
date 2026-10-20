# refusal/direction-twice-three-statements

**Expected:** refused. Identifiers that apply: `direction-twice`.

**Pins the provisional reading (§12):** Every direction statement in a block after the first is `direction-twice` (§4.9).

## Input

````text
flowchart TD
a[A]
subgraph s
  direction LR
  direction TB
  direction RL
  a
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> A block holds at most one direction statement (provisional): every direction statement in a block after its first is refused as `direction-twice`, the third and later ones included (provisional).

§9:

> The refusals of a single line are `conflict-marker`, `no-header` (for its line), `malformed-line`, `not-admitted` (front matter included), `reserved-id`, `stray-direction`, `subgraph-without-id`, `declaration-in-edge`, `edge-id-on-group`, `declaration-in-block`, `statement-in-block`, `nested-block`, `unbalanced-block` (for an `end-line`), `direction-outside-block`, `direction-twice` (for each direction statement in a block after the first) and `link-style`.

## Reasoning

The second and third direction statements in `s` are each refused as `direction-twice`.

## Other identifiers

- `stray-direction`: Each line matches `direction-stmt`.
