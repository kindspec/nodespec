<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0001: a Mermaid flowchart profile with declared names

**Status: approved by the owner, 2026-10-19.** Revised twice after review
found counterexamples (§4).

The question:

> What must a Mermaid flowchart hold, beyond what Mermaid accepts, so that
> a stock git merge which gets node identity wrong cannot pass as a
> diagram someone wrote?

## What is decided already

- nodespec exists for named-node diagrams (`existence/RESULT.md`): stock
  git merges a flowchart cleanly and wrongly when one branch renames or
  deletes a node and the other still names it (candidates 08 to 10), and
  Mermaid, which makes a node of any name an edge uses, shows nothing.
- Its format is a **profile of Mermaid flowchart syntax** (owner,
  2026-10-19): every nodespec file is a Mermaid flowchart that renders
  wherever Mermaid does. nodespec adds rules; it adds no syntax.
- Its adversary is blockspec's (owner, 2026-10-19): this text, then
  conformance cases written blind from the specification it becomes, then
  a reference checker run against them unchanged, under a mutation gate.

## Decision (proposed)

**D1. Every id is declared exactly once, and everything else only names
it.**

- A **node** is declared by a node statement on its own line, outside
  every subgraph block: `api[API]`.
- A **subgraph** is declared by its `subgraph` line, which must carry an
  explicit id: `subgraph cache [Cache tier]`.
- An **edge id** is declared by the one edge that carries it: `a e1@--> b`.
- A **class** is declared by its `classDef` line.

An edge, a `style` or `class` statement, or a member line names declared
ids and declares none: `api --> db` is an edge between two declared nodes,
and `api[API] --> db` is refused. `style` names a node or a subgraph;
`class` names nodes, subgraphs or edge ids. A file in which an id is named
but not declared, or declared twice, is outside the profile.

**D2. One id, one kind.** An id names a node, a subgraph, an edge or a
class, never two of them.

**D3. Membership is a member line.** Every subgraph block stands at the
top level: no `subgraph` line inside another block. A block holds only
member lines, each a declared node id or a declared subgraph id, and
`direction` statements: no declaration, no edge, no style. A member line
naming a subgraph nests it. A node or a subgraph is a member of at most one
subgraph, and nesting has no cycle.

**D4. Nothing depends on position.** `linkStyle`, which styles edges by
their index in file order, is refused: an edge added above it on another
branch silently restyles a different edge. A `class` statement comes
after the declaration of every id it names, since Mermaid 12.1.0 drops a
class given to a node, subgraph or edge not yet declared; with class lines
last, moving a declaration cannot strip its class.

**D5. The profile is checked, and refused, on the file alone.** A checker
reads one file and says either that it is in the profile or which rule
and which id it breaks. It repairs nothing. A merge is checked by checking
its result.

## Why

**D1** is the defect, made loud. In 08 to 10 a merged file names a node no
statement declares: `b` after `b` was renamed, `c` and `e` after they were
deleted. Under D1 the base declares each, the rename or delete removes that
declaration, the other branch only names it, and the merged file is outside
the profile. A name added on two branches in two places is two
declarations (03); so is a subgraph id (two branches adding `subgraph tier`,
which Mermaid would fuse into one subgraph) and an edge id. Declarations
stand on their own lines because an edge that could declare its end would
let the other branch quietly redeclare a node it renamed. Every class used
must be declared, so renaming a `classDef` against a new use of the old
name is refused, not rendered unstyled. `style` cannot name an edge id
because Mermaid drops it without a word.

**D2** refuses a merge where one branch's subgraph and the other's node
share an id (06, the spike's I4).

**D3** applies D1 to membership. Where a block's position or contents
decide membership, moving a node or a subgraph into a block deletes its
line in one place and adds it in another; against a delete on the other
branch, git keeps the added line and the deleted thing comes back inside
the block, in the profile. That happened twice: a node moved into a
subgraph against its delete, then a subgraph block moved inside another
against its delete (§4). With membership as a member line, the move adds
a name to the block and leaves the declaration where it was; the delete
removes the declaration; the merged file names an undeclared id, and D1
refuses it. Mermaid 12.1.0 nests a subgraph named on a member line as it
nests a block written inside another, in its model and when rendered
(§4); a `direction` inside a nested subgraph, and edges into one, were
not rendered. Mermaid does not refuse a membership cycle; D3 does.

**D4** is rowspec's rule that nothing is addressed by coordinate (rowspec
`AGENTS.md`), applied to edges.

**D5** keeps the rules useful under stock git: no driver, filter or hook,
which do not travel (rowspec `SPEC.md` §11).

**Why author-chosen names, when rowspec chose opaque ids.** rowspec §6
records that natural keys "lose an edit on rename and overwrite a row on
duplication"; there both happened silently. Here D1 makes both loud: a
rename against a use, and a name added twice in two places, are refused
files. The same name added identically at the same place on both branches
is still one node ("Not prevented"). Mermaid ids are what authors already
write and read, and an opaque id in every statement would make the source
unreadable, which is the one thing a text diagram has over a binary one.

## What it costs

The profile refuses most flowcharts as they are written today. Figures are
over the Mermaid spike's census population: the distinct in-subset blobs
at each corpus's pin, `.mmd` files (1,404 blobs in 94 corpora) and, where
given, Markdown fences (210 blobs in 35); the counts and the commands that
produced them are with the review's working files.

- **Declarations inside subgraph blocks are refused (D3).** 10,477 of the
  15,749 declared nodes in `.mmd` files, in 65 corpora, are declared only
  inside a block; 605 more in fences, in 22. Of 3,241 subgraph blocks in
  71 corpora, 2,646, in 67, hold directly something D3 refuses, 2,643 of
them a declaration or an edge; 203 in fences, in 22. This is
  the profile's largest cost: the ordinary way to write a subgraph is to
  write its nodes in it.
- **Nested blocks are refused (D3).** 468 subgraph blocks opened inside
  another, in 32 corpora; 52 in fences, in 6. Each becomes a top-level
  block and a member line; this one is mechanical.
- **Implicit nodes are refused (D1).** 4,236 vertices that no node
  statement declares, in 43 corpora, and 58 in fences of 15. 522 of the
  `.mmd` ones, in 30 corpora, are subgraph ids an edge, member line or
  `style` names, not nodes. The count is concentrated: 2,605 come from one
  corpus, which writes them as member lines only, and 811 from
  `mermaid-js/mermaid`.
- **Declarations inside edges are refused (D1).** 3,367 nodes, in 58
  corpora, are declared inside an edge (`api[API] --> db`); 1,339 in
  fences, in 21.
- **Smaller counts:** 319 nodes declared more than once, in 12 corpora
  (4 in fences, in 3); 100 subgraphs without an explicit id, in 11 (93 in
  fences, in 10); 71 edges styled by `linkStyle`, in 7 (9 in fences, in 2).
- **The rewrite is not purely mechanical.** Moving declarations out of
  blocks and edges is; but a bare node has Mermaid's default shape, and a
  declaration must name one, so converting a bare chart chooses one,
  such as `a[a]`, a rectangle labelled with its id. An editor writes declarations for
  new nodes; an existing chart needs that one-time rewrite, and a profile
  file reads differently from the Mermaid most authors write: declarations
  first, then edges, then blocks of names.

## Not prevented

These merge clean and stay in the profile, and no rule over one file can
tell them from a deliberate edit; they are named here as blockspec names
its residuals.

- **An id reused for a new meaning.** One branch deletes `cache` and, in
  the same change, declares a different node named `cache`; the other
  branch's new edge to `cache` lands on the new node. The id is the node's
  identity, by this profile's own rule, so reusing it is the author's
  statement that it is the same node.
- **The same declaration added on both branches at the same place.** Git
  keeps one line, so two authors' identical `cache[Cache]` become one node,
  with both branches' edges.
- **A delete against a move of the same declaration.** One branch deletes
  a node, an edge carrying an id, or a subgraph; the other moves that
  declaration's line elsewhere in the file. Git keeps the moved line, and
  the deleted thing comes back: a node with none of its edges, an edge
  without its `class` line, a subgraph with its member lines. Requiring a
  canonical order would refuse the move instead; this draft does not.
- **A class redefined** on one branch while the other assigns it: the
  assignment gets the new style, which is what a class is for.

## Open, for the specification and its cases

- Whether some identity error passes D1 to D5 with one ordinary edit per
  leg beyond those named above. Every review so far has found at least
  one; the blind cases are where more would be found.
- Which Mermaid statements beyond the spike's subset the profile admits
  (`click`, front matter, directives), each with its reason.
- Whether the profile should require a canonical statement order, which
  would close the delete-against-move residual at a further cost to how
  files are written.
- The spike's oracle records some correct merges as identity errors (I3):
  a delete against a move out of a subgraph, where the merged file is just
  the delete, and merges involving a subgraph rename. The cases must judge
  those by the text, not by the oracle's record. The oracle also cannot
  see a `class` on an edge, since the spike's model carries no edge
  classes, nor a leg that only moves lines, which leaves the model
  unchanged.

## What would reverse it

- A merge with one ordinary edit per leg that passes D1 to D5 and is wrong
  about identity, beyond what "Not prevented" names.
- The cost above proving too high in the product.

## 4. How it was reached

A first draft put declarations inside subgraph blocks and named only nodes
in D1. Its review built a checker for it and ran 20,000 seeded random
profile-form bases with one operation per leg, from Appendix B.2 and a few
further edits, through stock git, Mermaid 12.1.0 and the spike's oracle.
The fuzz found a delete against a move into a subgraph that merged clean,
in the profile, with the deleted node back (I3 at tier A); the same edge
id added on two branches; and a delete against a reorder of a node's
declaration. By hand the review built the same subgraph id added on two
branches, an edge written inside a block, and the reuse and
identical-addition cases. It found the census figures wrong and a claim,
that declarations inside edges are the commonest way Mermaid is written,
unsupported; the draft corrected the one and withdrew the other.

A second draft moved declarations out of blocks and extended D1 to every
id. Its review found that subgraph nesting was still a block's position:
deleting a subgraph against moving its block inside another merged clean
with the subgraph back, by hand and 19 times in the fuzz; that a delete
against a move of an edge carrying an id brings the edge back without its
class; and that `style` on an edge id does nothing.

This version nests by member line. Probed in Mermaid 12.1.0's model and
rendered in headless Chrome with the network off, a member line naming a
subgraph nests it as a nested block does. A third review, against a
checker for D3 as written here, re-ran every earlier counterexample and
the fuzz with nest and un-nest added: each counterexample is refused or
named in "Not prevented", nest and un-nest produced none, and the one new
one, a delete against a move of a subgraph block, is in that residual with
the node and edge cases of the same shape. A fourth, with D1's `style` rule
and an edge-only D4 class rule added to its checker, found that Mermaid drops a `class` placed before any
target's declaration, not only an edge's, and that a class could then be
lost by a move on the other branch; D4 now covers every target. The cost
figures were measured over the census population for this version.
