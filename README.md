# nodespec

**Status: not started.** This repository is a stub. It exists so the decisions
already made are not lost, and so the design pass can begin from them rather
than from a blank page.

nodespec is the **node kind** in [kindspec](https://github.com/kindspec) — a
specification and conformance suite for canvases and diagrams that must survive
version control, alongside [rowspec](https://github.com/kindspec/rowspec) (the
row kind).

Each kind is named after its **unit of identity**, because identity is the hard
part of every one of them:

| | unit | identity | status |
|---|---|---|---|
| [rowspec](https://github.com/kindspec/rowspec) | rows | opaque row ids | draft 0, published |
| [blockspec](https://github.com/kindspec/blockspec) | blocks | deliberately no minted ids | not started |
| **nodespec** | nodes | **named, not positional** | not started |

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
