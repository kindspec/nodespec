# nodespec

**Status: earned its existence; its specification is drafted, and
read by a reference checker.**
`docs/adjudications/0001-mermaid-profile.md` fixes the format, a profile
of Mermaid flowchart syntax with declared names, and `SPEC.md` is
draft 0, written from it. `reference/nodespec/` is a checker for it
(`just run FILE...`); the conformance cases, written from `SPEC.md`
alone, come next. `existence/RESULT.md` records that stock git merges a
Mermaid flowchart silently wrong in constructed cases that meet a criterion
fixed before they ran (`existence/CRITERION.md`), which with the product
need meets the bar set for this kind. The first surface is named-node
diagrams. A pre-registered spike, `spike/mermaid/`, asked whether
stock git merges a Mermaid flowchart silently wrong. It has run, and both of
its questions ended NO VERDICT (`spike/mermaid/LOG.md` §15). Real merged
history put identity at risk once, and git refused that merge, so nothing went
wrong silently. Structure decided 9 cases against a floor of 60. The spike is
closed, and identity in real history is parked: public history rarely exposes it, as the
pre-registration predicted (`spike/mermaid/PRE-REGISTRATION.md` §1.5).

nodespec is the **node kind** in [kindspec](https://github.com/kindspec) — a
specification and conformance suite for canvases and diagrams that must survive
version control, alongside [rowspec](https://github.com/kindspec/rowspec) (the
row kind).

Each kind is named after its **unit of identity**, because identity is the hard
part of every one of them:

| | unit | identity | status |
|---|---|---|---|
| [rowspec](https://github.com/kindspec/rowspec) | rows | opaque row ids | draft 0, published |
| [blockspec](https://github.com/kindspec/blockspec) | blocks | deliberately no minted ids | design pass |
| **nodespec** | nodes | **named, not positional** | specification draft 0 and reference checker; cases next |

## The thing that makes this different from rowspec

The prior research reached a conclusion here that runs against the obvious
analogy, and it should be read before anything is designed:

> Absolute coordinates are **not** the spatial A1. The A1 defect is silent
> semantic corruption on clean merge; coordinates do not have it — a clean
> coordinate merge gives exactly both authors' moves.

What actually decides whether spatial data survives git is **serialization**,
not addressing. See `DESIGN-BRIEF.md`.

## Before writing anything

Read `DESIGN-BRIEF.md`. It carries what is already decided and measured, what is
still open, and — most importantly — the one process question that must be
settled first.
