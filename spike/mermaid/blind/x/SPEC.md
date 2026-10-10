<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Cut byte for byte from spike/mermaid/PRE-REGISTRATION.md by harness/ms/blind.py:
     its sections 4 and 5, Appendices A and C, and Appendix D's extractor contract
     (its heading and its Extractor paragraph), in that order. -->
## 4. The model

### 4.1 Classes

| class | content |
|---|---|
| **identity** | one namespace of keys, each with a kind: `node` (a node id), `subgraph` (an explicit subgraph id, or `title:` plus the title for a subgraph Mermaid numbers itself) or `edge` (an explicit edge id, `e1@-->`, that R marks `isUserDefinedId`) |
| **relation** | edges, as a multiset of `(from key, to key, kind, label)`. An edge with a user-defined id is keyed by that id instead. An edge end that names a subgraph is a reference to that subgraph (Appendix A) |
| **membership** | for each node and subgraph, the subgraph that holds it, or none |
| **text** | each node's label; each subgraph's title; each edge label; `click` targets |
| **shape** | each node's shape, or `none` for a node with no shape statement |
| **style** | `classDef`, `class`, `:::`, `style`, `linkStyle`; direction statements |
| **order** | statement order (layout only) |

Appendix A maps each class from R's output.

### 4.2 Units

The oracle decides each unit separately:

- a key's existence, and its kind;
- a scalar value: `(key, property)`;
- an edge key's count;
- a membership: `(key)` mapped to its holder;
- a class assignment: `(key, class)`.

A unit is **keyed by** `k` if it is `k`'s existence, kind, scalar, membership
or class. A unit **refers to** `k` if it is keyed by `k` or holds `k` as a
value: an edge end, a class or style target, or a click target.

**A membership's holder is not a reference.** Membership is block containment:
a member is a line inside the holder's `subgraph … end` block, and git carries
it with the block. Renaming, retitling or unwrapping the block moves the
member with it. So a membership unit is **undecided**, and not a model
conflict, whenever its decided holder, or any of its holder values in `B`,
`O` or `T`, is a key that is decided absent. An undecided membership yields no
I1, no G3 and no MC, and it does not make a case exposed (§5.5). This covers a
member moved from one box to another on one leg while the other leg renames or
retitles both boxes: git merges it correctly, and no holder value the legs
wrote survives as a key. `census/synth-results.out` shows this on synthetic cases (§11.2, V3).

### 4.3 Three parsers

- **H**, the harness parser. Pure-stdlib Python. It accepts the subset in
  Appendix A and nothing else.
- **R**, the renderer: Mermaid 12.1.0, run as §4.4 pins. A text **parses** if
  R's parse succeeds. R also yields a model, mapped as Appendix A says.
- **X**, the second extractor, written blind (§10).

**A blob is in the subset** only if H parses it and H's model equals R's model.
Where Mermaid's behaviour decides a value, H must agree with R or the blob is
out of the subset. Appendix A lists each such behaviour as observed in
`census/v0-probes.out`. **A value H computes that Appendix A does not map from
R is never compared for tier A.**

### 4.4 R, pinned

- Node v24.20.0 (Mermaid 12.1.0 declares `node >=22.12.0`).
- `mermaid@12.1.0` and `jsdom@26.1.0`, pinned by a committed
  `package-lock.json` with integrity hashes, installed with `--ignore-scripts`.
  The synthetic probes ran on an install that resolved `dompurify@3.4.16`.
- **The wrapper** creates a jsdom window and sets `globalThis.window` and
  `globalThis.document` **before** it imports Mermaid. Without them DOMPurify
  defines no `sanitize`, and any chart with a label throws a `TypeError`
  (`census/v0-probes.out`, probe2 with `NO_JSDOM=1`).
- `mermaid.initialize({startOnLoad: false, securityLevel: "strict",
  maxEdges: 100000, flowchart: {htmlLabels: false}})`. With Mermaid's default,
  a chart of 500 or more edges throws "Edge limit exceeded" (probe2 with
  `DEFAULT_EDGES=1`). A chart over 100,000 edges is out of the subset and
  counted.
- **What "does not parse" means.** The wrapper calls `mermaid.parse(text)`
  and never passes `suppressErrors`, which turns every failure, a broken
  toolchain included, into `false` (probe5).
  - A thrown error that carries jison's `hash` property: the text does not
    parse.
  - **Any other thrown error:** the wrapper re-parses the fixed canary
    `flowchart TD` / `A[Alpha] --> B`. If the canary parses, the text does not
    parse, and the error class and first message line are recorded. If the
    canary fails, the toolchain is broken and the run aborts with a non-zero
    exit.
  - Texts whose errors carry no `hash` include an out-of-range `linkStyle`
    (`TypeError`), an unknown `@{ shape: … }` (`Error`, "No such shape"), a
    mixed-case header (`UnknownDiagramError`) and the edge limit (`Error`,
    "Edge limit exceeded"). Without jsdom, a labelled chart throws a
    `TypeError` and so does the canary, so the run aborts
    (`census/v4-error-texts.out`).
  - "Does not parse" makes a merged file E, and an input out of the subset.
- The model is read with `mermaid.mermaidAPI.getDiagramFromText(text)` and
  its flowchart database.
- No network after install.


## 5. The oracle

### 5.1 Decided values

Three model states: base `B`, legs `O` and `T`. For each unit:

- if `O` and `T` agree, that value is **decided**;
- if only one leg differs from `B`, that leg's value is decided;
- otherwise it is a **model conflict**.

Keys are the identity. A renamed id is a removed key and an added key. The
oracle does not guess renames.

### 5.2 Refusal cases

Some decided models cannot be rendered correctly by any merge. The only
correct outcome is then E. These are:

- **dangling**: a decided-present unit refers to a key that is decided
  absent (a membership's holder is not a reference, §4.2);
- **collision**: a key is absent in `B`, both legs add it, and some unit keyed
  by it differs between `O` and `T`, its kind included;
- **delete/modify**: one leg removes a key, and the other changes a unit keyed
  by it.

### 5.3 Categories

**E (loud).** A path is E if its merged file holds a conflict marker, or `git
ls-files -u -- <path>` is not empty, or R does not parse the merged diagram
(§4.4). For stratum D, a conflict anywhere in the file makes it E. A conflict
on another path in the same merge does not.

Every other category needs a path that is not E and four states in the
subset. A merged state outside the subset is **OUT-OF-SUBSET**: counted and
listed, never decided.

**DUP-TITLE** is its own listed outcome. When both legs add a subgraph without
an explicit id under the same title, git keeps both blocks, and the merged
state has two such subgraphs with one title. Neither leg's inputs are out of
the subset, but the merged state is, because §4.1 keys them by title. It is
counted and listed under its own name, never decided, and it counts toward
`k` when the case is exposed (§9.1).

**A record's objects** are the keys it concerns: for I1, the removed key and
every key of each unit that refers to it; for I2, I3 and I4, the key; for G1,
the node; for G2, the edge's two ends and its edge id if any; for G3, the
member and both holders, decided and merged; for G4, the key of the text unit,
or the edge's two ends; for G0, the path.

**Identity group.**

- **I1 Dangling resolved.** A dangling refusal case merged clean. This is
  hole #2.
- **I2 Collision merged.** A collision merged clean. This is hole #3.
- **I3 Delete/modify merged.** A delete/modify merged clean.
- **I4 Kind clash.** A key that no input gives two kinds, or a kind other than
  its decided kind, has two kinds or a different kind in the merged model. A
  clash already present in an input is not a record. R drops a node statement
  whose id was used earlier as an edge id (probe), so this is an identity
  fault, not a G1. An edge end that names a subgraph is a reference, not a
  clash (Appendix A).

**Structure group.**

- **G0 Diagram.** The merged file no longer holds exactly one Mermaid fence, or
  its diagram is no longer a flowchart.
- **G1 Node.** A decided-present node is absent, or a decided-absent node is
  present, outside I1–I4.
- **G2 Edge.** An edge key's merged count differs from the decided count. Lost
  and extra are reported apart.
- **G3 Membership.** A membership differs from the decided holder.
- **G4 Label.** A text unit differs from the decided value.

**Other.**

- **MC.** A model conflict outside §5.2 merged clean. It is eligible only if
  the merged value is neither leg's value. It then takes the group of its
  class: relation G2, membership G3, text G4, shape C, style D.
- **C, shape.** A shape unit differs from the decided value.
- **D, style.** A style unit differs. A `linkStyle` that lands on a different
  edge, because it addresses edges by position, is **S-LINKSTYLE**, tier D.
- **S-ORDER.** Statement order differs. Layout only. Reported, never eligible.

An edge written to a positional id, such as `X --> subGraph0`, is rare, and it
retargets when a leg inserts an untitled subgraph earlier. The oracle keys the
edge end by the subgraph it names in each state, so this lands in **G2**, as a
lost edge and an extra edge (`census/synth-results.out`, `posRef`).

### 5.4 Tiers, computed

| tier | categories | qualifies |
|---|---|---|
| **A** | I1–I4 (identity group); G1–G4 and eligible MC of relation, membership or text (structure group) | yes, for its group's verdict |
| **B** | any A record one of whose objects newly fails a lint (row 1); every G0 record | no: a lint over existing Mermaid catches it |
| **C** | shape | no: a near miss |
| **D** | style, S-LINKSTYLE | no |
| **E** | E | no: git refused |
| — | S-ORDER, ineligible MC, OUT-OF-SUBSET | reported only |

A lint failure is **new** if the same `(lint, object)` is absent from all
three inputs. Only new failures matter. A chart written in bare `A --> B`
style already fails L1 on every node, so L1 never demotes a record there.

### 5.5 Exposure

A case is **exposed** if its inputs meet a refusal case's precondition, read
from `B`, `O` and `T` only:

- one leg removes a key that a unit added or changed by the other leg refers
  to; or
- both legs add the same key with some differing unit keyed by it.

Exposure is computed before the merge result is read. An exposed case that
comes out E or B is git or a lint working.


## Appendix A — the subset, and R's model

**In the subset:**

- a header `flowchart`, `flowchart-elk` or `graph`, with an optional direction
  (`TB`, `TD`, `BT`, `LR`, `RL`);
- leading front matter and `%%{init: …}%%` directives, read as configuration
  and ignored by the model;
- `%%` comments;
- node statements with the classic shapes: `[ ]`, `( )`, `([ ])`, `[[ ]]`,
  `[( )]`, `(( ))`, `> ]`, `{ }`, `{{ }}`, `[/ /]`, `[\ \]`, `[/ \]`,
  `[\ /]`, `((( )))`; quoted labels; and the `@{ shape: …, label: … }` form;
- edges `-->`, `---`, `-.->`, `-.-`, `==>`, `===`, `~~~`, `--o`, `--x`,
  `<-->`, `o--o`, `x--x`, with extra-length variants; labels as `-->|text|`
  and `-- text -->`; chains `A --> B --> C`; `&` groups; edge ids `e1@-->`;
- `subgraph id [title]`, `subgraph id`, and `subgraph Some Title` or
  `subgraph "Some title"` (no explicit id) … `end`, nested, with `direction`
  inside;
- `classDef`, `class`, `:::`, `style`, `linkStyle`, `click`.

**Out of the subset, each refused and counted:** Markdown-string labels
(`` "`…`" ``), icon and image node forms, `@{ … }` keys other than `shape`
and `label`, two subgraphs without an explicit id that share a title, an
explicit subgraph id of the form `subGraphN` (R merges it with its own
numbering, V0), an edge end that names a user-defined edge id (V0), and any
statement H does not parse. A text that does not parse under §4.4's rule is
not an input in the subset.

**A node statement** is an occurrence of an id followed by a shape bracket, or
by `@{ … }`, whether alone or inside an edge chain. A bare id is not a node
statement. L1 reads this definition.

**R's model, class by class.** Each line cites the probe in
`census/v0-probes.out` that shows the behaviour; V0 repeats each.

- **identity.**
  - Node keys are the vertex map's keys, except a vertex whose id equals a
    subgraph's id and that has no node statement anywhere in the text: that is
    an edge end referring to the subgraph (probe `edgeToSub`).
  - A subgraph's key is its `id` if the text gave one, and `title:` plus its
    title if R assigned `subGraphN` because the header had no explicit id
    (probe3, probe4). H decides which from the header form, and must agree
    with R's `id`.
  - An edge key is the edge's `id` when R reports `isUserDefinedId: true`
    (probe2 `edgeIdUser`). Automatic ids are never keys. A second edge with a
    repeated user-defined id gets an automatic id and `isUserDefinedId: false`
    (probe `dupEdgeId`).
  - A node statement for an id already used as an edge id is dropped by R; a
    node declared first coexists with a later edge id of the same name (probes
    `edgeIdThenNode`, `nodeEqEdgeId`).
  - A node id equal to a subgraph id, with a node statement, gives both a node
    and a subgraph (probes `subEqNode`, `subEqNode2`).
- **relation.** Each edge's `start`, `end`, normalized kind, and `text`.
- **membership.** A node's holder is the first subgraph, in R's subgraph list
  order, whose `nodes` list holds it. The list is in closing order, so a node
  mentioned in two subgraphs belongs to the first to close, and an inner
  subgraph closes before its outer one (probes `twoSub`, `twoSubRev`,
  `twoSubNested`).
- **text.** A vertex's `text`, where a node declared twice keeps its last label
  (probe `twice`); a subgraph's `title`; an edge's `text`, compared exactly as
  R reports it, since R does not decode entities in it (probe `labelEdge`); a
  vertex's `link` and `linkTarget` for `click`, as R normalizes them (probe2
  `click`).
- **shape.** A vertex's `type`, where a node declared twice keeps its last
  shape (probe `twiceShape`). A node with no shape statement has no `type`;
  the model records `none` (probe `bare`).
- **style.** A vertex's `classes`, without the class `clickable` that R adds
  for `click` (probe2 `click`), and its `styles`; the class definitions; each
  edge's `style` from `linkStyle`.
- **order.** The order of R's vertex map and edge list.

**Normalization.** Arrow kinds map to `(line, head)`, where line is `solid`,
`dotted`, `thick` or `invisible`, and head is `none`, `arrow`, `circle` or
`cross`, at each end. Extra length is dropped. Node labels and subgraph titles
are compared after trimming outer whitespace. Nothing else is normalized.


## Appendix C — lints for tier B (row 1)

Each runs on the merged file alone. Only a new failure counts (§5.4).

- **L1. Implicit node.** A node id with no node statement (Appendix A).
- **L2. Redeclared node.** A node id given two different labels or shapes.
- **L3. Multi-held node.** A node mentioned inside two different subgraph
  blocks.
- **L4. Id clash.** An id used as two kinds.
- **L5. Duplicate edge.** Two edge statements with the same key.
- **L6. Fence.** For stratum D, the file does not hold exactly one Mermaid
  fence whose diagram is a flowchart.


## Appendix D — contracts for the blind roles

**Extractor.** `python3 -I extract2.py <stratum> <base> <o> <t> <merged>`
prints one JSON object: the decided values, the exposure, and every record with
its category, objects and tier. Pure stdlib. A non-zero exit or empty output
is recorded as a disagreement.

