# refusal/membership-cycle-two-subgraphs

**Expected:** refused. Identifiers that apply: `membership-cycle` (id `s`, `t`).

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
subgraph s
  t
end
subgraph t
  s
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> Nesting has no cycle. Following holders from a subgraph never returns to it. A cycle is refused as `membership-cycle`; a member line naming its own block's subgraph is a cycle of one.

## Reasoning

`t` is held by `s` and `s` by `t`. Both are on the cycle.

## Other identifiers

- `member-twice`: Each is on one member line.
