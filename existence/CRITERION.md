<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# nodespec's existence: the constructed case, criterion fixed before it is built

**Status: approved by the owner on 2026-10-19, as it reads.** No
candidate below has been run.

## 0. What is decided already

- **The bar** (owner, 2026-10-18): nodespec earns its existence by product
  need plus a constructed silent-wrong case, the bar rowspec met. It
  replaces, for nodespec only, the rule that a failure must be observed in
  real history, which public diagram history cannot meet
  (`spike/mermaid/LOG.md` §15: one identity exposure in real merged
  history, refused by git).
- **Product need** (owner, 2026-10-18 and 2026-10-19): diagrams are in the
  first product, and nodespec's first surface is named-node diagrams:
  flowcharts and architecture diagrams whose nodes carry author-chosen
  names and whose edges refer to them.
- **The adversary** (owner, 2026-10-19): as blockspec's. This document
  does not depend on it.

What is left is the constructed case. This document fixes, before any case
is built, what counts as one.

## 1. What counts

A **constructed silent-wrong case** is a base Mermaid flowchart and two
edits of it, *ours* and *theirs*, such that all of these hold:

1. **Each edit is one a person makes.** Each leg applies one operation
   from the spike's scripted-edit list (`spike/mermaid/PRE-REGISTRATION.md`
   Appendix B.2): relabel a node, rename an id (every occurrence, as an
   editor's rename does), add a node, add an edge, delete a node (and every
   statement naming it), delete an edge, retarget an edge end, move a node
   into or out of a subgraph, add a subgraph, change a shape, or restyle.
   New statements may go anywhere a person would put them, not only where
   B.2's generator puts them.
2. **Git merges it cleanly.** Stock `git merge` of the three texts as
   commits, through the spike's hermetic wrapper
   (`harness/ms/gitops.py` `merge_texts`: no user or system config, no
   drivers), leaves no unmerged path and no conflict marker.
3. **Mermaid accepts the result.** The merged text parses under the
   spike's pinned R (`r/rmodel.mjs`: Mermaid 12.1.0, jsdom 26.1.0, Node
   v24.20.0), with no error.
4. **It is wrong about identity.** The spike's oracle
   (`harness/ms/oracle.py`, as validated at the spike's validation
   commit), judging the three input models and the merged model, records
   at least one identity-group category (§5.3: I1, I2, I3 or I4): a node
   exists that neither leg meant, an edge, membership or label names a
   different node than its author wrote, or two authors' distinct nodes
   are one.
5. **Nothing in the merged file shows it.** That record is tier A
   (§5.4): no lint of Appendix C over the merged file alone reveals it.
   The merged file is a diagram someone could have written on purpose.

One case meeting all five meets the bar. Cases are synthetic, written for
this document, released CC0-1.0 as org contract §6 sets for fixtures.

## 2. What is built, and how it is reported

- **Candidates are written from the edit classes in §1.1**, at most ten,
  each a base under 30 lines and one edit per leg, before any is run. They
  are committed with this document's approval, in the order written.
- **Each is run once**, in that order, by a driver committed with them
  that calls the spike's harness functions at nodespec `main`, unchanged:
  `ms/case.py`'s `prepare` and `outcome`, which merge, parse under R and
  judge. R is installed from the committed `package-lock.json`. The
  driver's transcript is committed.
- **Every candidate is reported**, whether or not it meets §1, with which
  of 1 to 5 failed. No candidate is edited after it has run; a new one is a
  new candidate, numbered after the others, and stays within the cap.
- **Before any candidate ran**, `run.py` was tested on three inputs that
  are not candidates, in a scratch tree: two disjoint relabels on adjacent
  lines (git conflicts), the same five lines apart (clean, no record), and
  a rename against a new edge in a fully labelled chart. That last merged
  clean with an I1 record at tier B: the edge's dangling end becomes a node
  with no label, which lint L1 flags. Candidate 01 has the same shape and
  is left as written.
- **Verdict:** **met** if any candidate meets all five; **not met** if
  none of the ten does. "Not met" sends the question back to the owner;
  it does not by itself decide that nodespec is not built.

## 3. What it does not claim

- No frequency. A constructed case shows the defect exists; the spike
  showed real history rarely exposes it, and nothing here changes that.
- Not that nodespec's design fixes it. That is the spec's to show, with
  this case among its conformance cases: the design must refuse it or
  merge it right.
- Not that every diagram format has it. Formats whose nodes carry minted
  ids, such as JSON Canvas, are out of this document's scope.
