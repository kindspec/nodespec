# examples/s4-9-member-line-ending-in-direction-refused

**Expected:** refused. Identifiers that apply: `stray-direction`; `undeclared-id` (id `LR`).

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
a[A]
subgraph s
  a
  xdirection
  LR
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> What it swallows is gone: `a[go direction LR]` declares no node, an edge labelled `|direction RL|` is no edge, and a member line ending in `direction` followed by a line starting with `LR` holds neither.

§4.9:

> with trailing whitespace removed, it ends in `direction`.

## Reasoning

§4.9's example of a member line ending in `direction` followed by `LR`. `  xdirection` matches `member-line`, but with trailing whitespace removed it ends in `direction`, so it is `stray-direction` and is not a member line for any later rule. `  LR` is a member line naming `LR`, which nothing declares. `LR` is not a reserved word.

## Other identifiers

- `malformed-line`: `xdirection` matches `member-line`.
- `reserved-id`: No reserved word.
