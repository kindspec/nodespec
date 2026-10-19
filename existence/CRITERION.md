<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# nodespec's existence: the constructed case, criterion fixed before it is built

**Status: approved by the owner on 2026-10-19, then revised the same day
after review, in the form the owner approved:** condition 5 worded as the
spike's tier A, what one edit is (§1.1), candidates 08 to 10, and the
disclosures in §4. No candidate below has been run.

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
   B.2's generator puts them. One edit is one statement-level operation.
   An edge statement whose end is a new node, `api --> cache[Cache]`, adds
   a node and an edge at once; candidates 01, 03 and 06 have that shape
   and are reported as written, with this noted. Candidates 08 to 10 add
   edges only between existing nodes. Read as one statement-level
   operation, as Mermaid writes it, 01, 03 and 06 meet this condition;
   read as one node or one edge, they do not, and a result on them is
   reported with that noted. This condition is a property of the case
   files: review judges it, and `run.py` records it so.
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
5. **Nothing in the merged file shows it newly.** That record is tier A
   (§5.4): no lint of Appendix C fails on the merged file, for one of the
   record's objects, where it did not already fail in an input. In a chart written in bare
   `a --> b` style, every node already fails L1, so a node nobody meant
   looks like every other node; in a fully labelled chart the same node
   has no label and L1 flags it, which makes the record tier B.

One case meeting all five meets the bar. Cases are synthetic, written for
this document, released CC0-1.0 as org contract §6 sets for fixtures.

## 2. What is built, and how it is reported

- **Candidates are written from the operations in §1.1**, each a base
  under 30 lines and one edit per leg. 01 to 07 were written first, all on
  one fully labelled chart. 08 to 10 were added after review of the
  driver, before any candidate ran, on one chart in bare `a --> b` style
  (§4). There are ten, the cap; no more are added.
- **Each is run once**, in name order, by `run.py`, which calls the spike's
  harness functions at nodespec `main`, unchanged: `ms/case.py`'s
  `prepare` and `outcome`, which merge, parse under R and judge. R is
  installed from the committed `package-lock.json`. `run.py` writes only
  `existence/results.jsonl`, with the R and git each candidate ran under;
  the file only grows, and `run.py` never runs a candidate already in it.
- **Every candidate is reported**, whether or not it meets §1, with every
  condition of 2 to 5 that failed; 1 is judged by review. A candidate the
  harness cannot judge at all, its inputs outside the spike's subset, is
  reported as not judgeable, failing 4 and 5, with 2 and 3 not tested. No candidate is edited after it has run.
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

## 4. What was seen before any candidate ran

- **The author's smoke test of `run.py`**, after the owner's first
  approval and before review, on three inputs that are not candidates, in
  a scratch tree: two relabels on adjacent lines (git conflicts), two
  relabels three lines apart (clean, no record), and a rename against a
  new edge in a fully labelled chart, which merged clean with an I1 record
  at tier B because the edge's dangling end becomes a node with no label,
  which L1 flags. The first was not kept.
- **The review of `run.py`** ran the harness on inputs of its own, none a
  candidate. Two met conditions 2 to 5: a rename against a new edge in a
  bare `a --> b` chart, a clean merge that Mermaid parses with an I1
  record at tier A; and an input that fails condition 1, one leg making
  three edits. It is not a candidate and is not part of the verdict.
  Candidate 08 has its shape and was written after it, as were 09 and 10.
- The review also found that the first approved text had been edited
  after approval (the smoke-test paragraph), that `run.py` numbered three
  outcomes wrongly and could re-run a candidate under a new output path
  (it now writes one fixed file),
  and that the labelled chart of 01 to 07 makes most identity errors
  lint-visible. The revision above answers each.
