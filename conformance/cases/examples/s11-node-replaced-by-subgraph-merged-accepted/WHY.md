# examples/s11-node-replaced-by-subgraph-merged-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph x
  b
end
a --> x
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§11:

> one branch replaces the node `x` with a subgraph `x`, or the reverse, and the other adds an edge to `x` or a member line naming `x`. The merged file declares `x` once, as the new kind, and the other branch's edge or member line silently lands on it, since an edge may end at either kind and a member line may name either.

§5.2:

> An edge may end at a subgraph (the owner, 2026-10-19).

## Reasoning

§11's cross-kind reuse, merged. This suite's rendering of §11's prose: the base declares `x[X]`; one branch replaces it with the block `subgraph x` holding `b`; the other adds `a --> x`. The merged file declares `x` once, as a subgraph, and an edge may end at a subgraph, so it is in the profile. §11 names this as a merge the profile does not prevent.
