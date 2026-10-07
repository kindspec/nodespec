<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# nodespec — design brief

Carried forward from the research and build that produced rowspec 0.1.0. Nothing
here is a specification; it is the state a fresh design pass should start from,
so that pass argues about the open questions rather than rediscovering the
settled ones.

**This is the least-developed of the three kinds.** Treat everything below as
weaker evidence than blockspec's brief, and much weaker than rowspec's.

---

## 0. Settle this before anything else

Every substantive defect found while building rowspec was found by **two
independent implementations disagreeing** — one author who had written the
reference, one forbidden to read it, both measured against the same fixture
tree. A format that does not exist yet has nothing to disagree with, and the
discipline cannot be retrofitted: rowspec's second implementation drifted 117
cases behind the moment nothing ran it.

So the first decision is a *process* decision: **how does this format get an
adversary from day one?**

## 1. The finding that should stop the obvious design

The tempting analogy is that absolute coordinates are to canvases what `A1`
references are to spreadsheets. **The research says that is wrong:**

> Absolute coordinates are **not** the spatial A1. The A1 defect is *silent
> semantic corruption on clean merge*; coordinates do not have it — a clean
> coordinate merge gives exactly both authors' moves.

What actually decides whether spatial data survives git is three
**serialization** properties, none of which is about addressing:

1. one value per line
2. no per-save churning metadata
3. no rewriting of state the author did not touch

Real `.excalidraw`, `.tldr`, `.canvas`, and pretty-printed `.drawio` and OOXML
all merge cleanly under stock git once those hold.

**So the rowspec thesis does not transfer.** rowspec exists because nominal
addressing fixes a defect no merge algorithm can. If canvases do not have that
defect, nodespec needs a different justification or it should not be built.

## 2. Where a real defect does appear

The semantic/override split earns its place for a **different** reason: derived
layout is globally unstable, so an *absolute* override goes stale and silently
degrades the picture. **The override layer must therefore be relational, not
numeric.**

That is the closest thing to a demonstrated silent-wrong-merge in this kind, and
it is where a design pass should start looking.

## 3. Known holes, from the earlier canvas work

`.canvas` had **zero test coverage** and three named referential-integrity holes,
none of which was ever closed:

- an override for a **deleted** node
- an edge to a **renamed** node
- two branches adding **different nodes with the same name**

The third is the one that rhymes with rowspec's duplicate-id refusal, and is the
most likely place a genuine silent-wrong-merge lives.

## 4. Open, and genuinely undecided

**Does this kind justify existing?** See §1. Answer this before designing
anything. A finding that canvases do not need a new format is a legitimate and
valuable outcome — the same standard applied to rowspec, whose own README says
*"if your table is a list of facts, you probably do not need this."*

**What is a node's identity?** "Named, not positional" is the working answer and
is barely more than a slogan at this stage.

**2-D structure has no long-form equivalent.** The earlier work flagged matrix
layouts as *"probably out of scope forever — say so"*, and saying so explicitly
is itself a deliverable.

**Name availability.** `nodespec` is clear on PyPI and crates.io and **taken on
npm**. It binds only if a JavaScript package is ever published under that name.

## 5. The method that must carry over

- The **conformance suite is the deliverable**; the spec exists so the suite has
  something to check.
- **The suite is not written by whoever writes the implementation.**
- **The mutation gate**: a surviving mutant is a failure, and so is a stale one.
- **Measure before deciding**, and remember that corpus cell counts are inflated
  by replication — the unit that matters is a distinct authored artifact.
- **Be willing to conclude "do not build this."** That verdict has already been
  reached once in this project's history, correctly.

## 6. Where the prior work lives

In [kindspec/research](https://github.com/kindspec/research):
`design-findings/D7-spatial.md` (the canvas serialization findings) and
`DESIGN.md` (the overall verdict and the `.canvas` holes). And rowspec's own
`docs/rationale.md`. Cite them by path and commit.
