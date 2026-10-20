# applicability/nested-block-opens-no-block

**Expected:** refused. Identifiers that apply: `nested-block`; `unbalanced-block`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
a[A]
subgraph s
  subgraph t
    a
  end
end
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§6:

> a subgraph line in a block is refused as `nested-block`;

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

`subgraph t` opens nothing; the first `end` closes `s` and the second has no open block.

## Other identifiers

- `member-twice`: `a` is on one member line.
