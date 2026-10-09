<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration: does stock git merge a Mermaid flowchart silently wrong about named identity?

**Status: approved by the owner on 2026-10-09, with every default in §0.1; committed when merged to `main`.** Its home is kindspec/nodespec
`spike/mermaid/PRE-REGISTRATION.md`. "Committed" means merged to nodespec
`main`. Nothing under this document runs before it merges. It runs before the
canvas census (`spike/canvas/PRE-REGISTRATION.md`).

**Published.** This spike's result is **published** when its result commit
(§11.3, commit 6) is merged to nodespec `main`. The canvas census's Arm 0 does
not start before that.

**What kind of test this is.** For named identity, the premise, this is a
**one-sided existence test**. It can find the defect in real history (FOUND),
or report that real history did not show it (NO VERDICT). It cannot show the
defect absent. **Identity NOT FOUND is unreachable on any public census**
(§1.5), so this document does not define it. The structure group (§5.3) is
two-sided and can end NOT FOUND.

**Inputs already seen.** Before this draft was written, inputs of the real
concurrent cases this spike would evaluate were read, never their merge
results. For every stratum-D both-sides merge, pull request and
closed-unmerged pull request, the base and both legs were read to count fences
and to compare fence-body hashes. For every stratum-F both-sides merge, the
base and both legs were read to see whether each leg changes the diagram. For
pull requests, diffs were read to compute patch-ids. No merge was run.
`census/README.md` lists every read. These facts shaped §1.4–§1.6, §7.4's
sibling rule and §8.2's pull-request rule.

**Citations.** A `research/` path means kindspec/research at `71d97a1e6f36`.
`design-findings/D7-spatial.md`, `design-findings/R1-redteam-formats.md`,
`experiments/R1-canvas/` and `DESIGN.md` are unchanged between `71d97a1e6f36`
and `d02c196bf6ae` (`git diff --stat 71d97a1e6f36 d02c196bf6ae -- <paths>`
prints nothing). A blockspec path means kindspec/blockspec at `f59c109f96b3`.
A nodespec path means kindspec/nodespec at `9beeba422813`. Every corpus figure
comes from a script in `spike/mermaid/census/`, committed with this document.
`census/README.md` gives the command behind each figure. Every statement about
Mermaid 12.1.0's behaviour cites `census/v0-probes.out`, the output of
synthetic probes run under §4.4's toolchain.

**Private individuals.** Corpora owned by an individual GitHub account are
named in every committed output only by a label `u:` plus 12 hex digits of
`sha256(salt + ":" + owner/name)`. The salt, the mapping and every raw output
that names such a corpus stay outside the repository, held by the owner like
the sealed fixtures. Corpora owned by an organisation are named.

---

## 0. What the owner is approving

Approving the draft approves everything in this section.

### 0.1 Decisions only the owner can make

Each row is a value judgement: which question matters, or what risk is
acceptable. Everything a fact, a count or a test can settle is decided in
§0.2, with its evidence.

| # | decision | chosen | alternative |
|---|---|---|---|
| 1 | Does a defect that a lint can catch count? [§5.4] | **No.** A record whose objects newly fail a lint L1–L6 (Appendix C), run on the merged file alone, is tier B. A lint over existing Mermaid would catch it, so it does not argue for a new format. **Consequence:** both canonical holes are tier B by construction in charts that declare labels. Hole #2 with a declared label (`db[(Postgres)]`) leaves a newly implicit node, which L1 sees. Hole #3, both legs declaring the same id with different labels, is a new L2 failure. Both holes are tier A only in bare-id charts, or, for hole #3, where the legs differ only in `class`, style or `click`. | **Yes.** B is empty, and a record is tier A unless Mermaid rejects the file. |
| 2 | The evidence bar [§9.1] | FOUND needs **one** qualifying case. The structure group's NOT FOUND needs **60** cases, so the 95% bound `3/n` is 5% or less. | Two FOUND cases from two corpora, or another bound. |
| 3 | Sealed fixtures [§10.4] | A blind author writes them. **The owner holds them** until commit 6. | Visible fixtures only. |
| 4 | What standard decides named identity [§1.5, §9] | **(a)** A one-sided existence census on real merged history. **Consequence:** it almost surely ends NO VERDICT (§1.5), and named identity stays unmeasured, so no "do not build" verdict is possible from it. | **(c)** V3's bare-style hole plants, with X's agreement in V5, as the demonstration of the mechanism, plus S's generator rates (§9.1). **Consequence:** it answers yes by construction, since those plants build the defect on purpose. Its verdict is labelled "MECHANISM SHOWN, frequency unmeasured", never FOUND: it shows the defect can happen, never that it does. |

Option (b), counting never-merged concurrent work as real history, was
measured and offers nothing: 0 eligible cases (§1.6). It is not offered.

### 0.2 Settled, from evidence, from a recorded decision, or by a V test

These are not offered as a menu.

- **Identity is the premise** (§2). `DESIGN-BRIEF.md` §4 names "what is a
  node's identity?" as the open question, with "named, not positional" as the
  working answer, and §3's holes #2 and #3 are identity holes. The org contract
  names nodespec by its unit of identity. The structure group gets its own
  verdict and does not answer the premise.
- **Never-merged concurrent work is not real history for identity** (§1.6).
  It was measured and adds nothing: of 51 closed-unmerged pull request paths,
  6 hold one flowchart fence in every input (5 in
  `open-telemetry/opentelemetry-specification`, 1 in `apache/airflow`) and none
  changes it on both legs; of 1,512 forks fetched, none changed a flowchart
  path the upstream also changed. Row 4 weighs the two standards that remain.
- **Identity has no NOT FOUND** (§1.5, §9.1). The census holds at most 14 real
  concurrent cases whose flowchart changed on both legs, 5 after derived
  output is excluded, against any floor that could support a bound.
- **The structure bar differs from the canvas census's.** The canvas census
  uses 40 cases (7.5%) because its corpora cannot supply more, and it is
  labelled as not expected to settle its question. Here P supplies thousands
  of replayable triples (§1.4), so the tighter 5% bound costs nothing in
  reachability.
- **Stratum D stays, for the structure group** (§3). It supplies no identity
  case (§1.4). It stays because it is where the multi-author editing is: in
  in-licence corpora, summing each corpus's top author gives 224 of 1,297
  modifying edits in D, against 2,983 of 3,225 in F. Without D, the structure
  group would rest almost entirely on single-author files.
- **Subgraphs without an explicit id are keyed by title** (§4.1). Mermaid
  gives them a positional id `subGraphN`, which renumbers when another such
  subgraph is added or removed (`census/v0-probes.out`, probe4), so it is not an
  identity. 35 of 1,229 stratum-F flowchart blobs at the pin and 8 of 75
  stratum-D flowchart files use one; 2 and 1 of them repeat a title, which puts
  them out of the subset (`census/subgraph-forms-public.tsv`).
- **Copyleft and share-alike corpora are read only** (§7.3). Measuring them
  does not copy them. Their values are hashed in every committed output.
- **A FOUND from an individually owned corpus counts** (§12). The defect is a
  property of the merge, not of who owns the repository.
- **Fixtures are synthetic** unless taken from a CC0-1.0, 0BSD or Unlicense
  corpus (§10.4). MIT, Apache-2.0, BSD, CC-BY-4.0 and W3C text keeps its
  attribution terms and cannot be relicensed CC0-1.0.
- **The cap binds on corpus and on author** (§7.5). No corpus and no author
  supplies more than half of any floor. Most F corpora have one author
  (§1.4), so the two units mostly coincide, and capping both costs little.
- **The renderer is Mermaid 12.1.0** (§4.4), with its configuration, its DOM
  shim and Node pinned. "Parses" must mean what Mermaid does, and only
  Mermaid's own grammar can say that. The toolchain was shown to run headless
  on synthetic charts (`census/v0-probes.out`); V0 repeats this before Arm 0.
- **Bots count** (§7.4). Bot-authored edits are 262 of 4,829 modifying edits
  across the listed corpora (§1.4). The caps already stop any one corpus or
  author carrying a floor. Their share is reported.
- **NO VERDICT is not "do not build"** (§12). The owner decided on 2026-10-08
  that there is no "do not build" verdict while named identity is unmeasured.
- **E is per path** (§5.3). A conflict anywhere in a Markdown file makes that
  path E.
- **One fence per Markdown file** (§3). A case whose inputs do not each hold
  exactly one Mermaid fence is excluded and counted. A merged file whose fence
  count or diagram keyword changed is a record, not an exclusion (G0, §5.3).
- **Generated files** (§7.4): a path-segment rule, a self-declaration rule and
  a co-changing sibling rule.
- **The subset** (Appendix A). A blob is in the subset only if H parses it
  and its model equals R's model under Appendix A's mapping.
- **Arm M-PR** (§8.2): a pull request's target leg is chosen by patch-id, or
  the case is excluded.
- **Arm P** (§8.3): the predecessor rule, ancestry, and judgement against the
  real later version.
- **Arm S** (§8.4): its rates are properties of the edit generator. It never
  yields FOUND and never supports NOT FOUND.
- **The merge** (§6, F2): `git merge` in a hermetic repository.
- **The second extractor** runs on every case (§10.5). A crash or an empty
  output is a disagreement.
- **Harness:** pure-stdlib Python, run with `python3 -I`. R is the one
  non-Python part.

### 0.3 Consequences of the decisions above

- **Squash- and rebase-merged pull requests are part of arm M** (M-PR, §8.2).
- **Tiers are computed.** Every category in §5 is mechanical. There is no
  blind tierer.
- **Every FOUND names its arm**: M-merge (a real merge), M-PR (a real pull
  request replayed against its target), or P (real consecutive edits replayed
  as concurrent). Every NOT FOUND reports its `n` split by arm, and says so
  when P supplies most of it.
- **No transplant check.** "Already solved by an existing format" is not
  tested here. No in-scope comparator has a defined, mechanical transplant, so
  the check is dropped rather than left vague (§1.7).

## 1. Prior evidence

**1.1 D7 recommends delegating diagrams to text languages, untested.**
`D7-spatial.md` §9 says: "Diagrams: delegate to D2 (MPL-2.0) or Graphviz,
rendered via Kroki. Do not build a language." Its first argument for dropping
the leg is that "Structured diagrams are *already solved and already text*.
Mermaid, Graphviz, D2, PlantUML, Structurizr all diff like code." No research
experiment merges a file in any of these languages. The DOT files in
`experiments/D7-semantic-layout/` and `experiments/R1-canvas/c2_graphviz.py`
measure layout stability, not merging. §11 records the same recommendation:
"delegate the languages". This spike tests it for one of them.

**1.2 The brief's hole #2, as research first found it.**
`experiments/R1-canvas/c1_canvas.py` case C1b merges two branches of
research's own canvas syntax. One renames node `db` to `pg`; the other adds
`edge api -> db`. Git merges cleanly, and the layout silently drops the edge
(`R1-redteam-formats.md` §(a5)). That syntax is not used outside research.

**1.3 Mermaid has named identity.** A Mermaid flowchart names each node with
an author-chosen id, and an edge names its ends by id. An edge may name a node
that no statement declares, and the node is then drawn with its id as its
label. So hole #2 in Mermaid is not a dropped edge. It is a **ghost**: a node
named by the old id that nobody declared. Hole #3 (two branches add different
nodes with the same id) becomes one node with both branches' edges. Synthetic
probes under §4.4's toolchain show both behaviours in Mermaid 12.1.0
(`census/v0-probes.out`, probes `implicit` and `twice`); V0 repeats them before
anything else runs.

**1.4 Real history: plenty of single edits, almost no concurrency.** Measured
on 2026-10-07 and 2026-10-08 from blobless clones. No merge was run and no
merge result was read. The table is `census/corpora-public.tsv`.

| stratum | licence status | corpora | flowchart paths | version pairs | not ancestor-related | triples on ancestry chains | two-parent merges | evaluable both-sides merges | evaluable both-sides pull requests (§8.2's rule) |
|---|---|---|---|---|---|---|---|---|---|
| F (`.mmd`, `.mermaid`) | in | 90 | 1,484 | 3,246 | 37 | 2,337 | 5,762 | 4 | 0 |
| F | read only | 23 | 187 | 233 | 1 | 145 | 2,736 | 1 | 0 |
| D (`.md`) | in | 9 | 61 | 1,299 | 142 | 984 | 38,080 | 144 (9 with one fence) | 6 (0 with one fence) |
| D | read only | 1 | 7 | 74 | 0 | 68 | 4,360 | 0 | 1 (0 with one fence) |

Pull requests were counted for the 31 F corpora with at least ten commits
touching a flowchart (as listed under the census's first rules), and for all of
D, under
§8.2's patch-id rule, with the commit list read across every page. Of 433
merged single-parent pull requests touching a flowchart path, 128 matched as
rebase merges, 291 as squash merges, and 14 were excluded: 13 matched neither
rule and 1 had more than 250 commits. A one-commit pull request matches both
ways; it is counted as rebase, and either way its target is `c^`.

- **Stratum F** came from GitHub code search: 2,226 distinct paths in 1,643
  repositories. 388 repositories had a path with two or more commits; 242 were
  not forks, had a licence, and were counted. Listed corpora are those with a
  triple on an ancestry chain or an evaluable both-sides case, after §7.4.
- **Stratum D** is ten large multi-author projects named before counting. Its
  counts are **path-level** and see only paths holding a flowchart fence at the
  pin. They are not an upper bound on fence edits: a path whose flowchart was
  removed before the pin is not seen.
- **"Evaluable"** means a selected path changed on both sides from one merge
  base, not an add/add, not a delete/modify, and not the same blob on both
  sides. Read from trees only.
- **Concentration.** 62 of the 90 in-licence F corpora have one author.
  Summing each corpus's top author gives 2,983 of 3,225 modifying edits in
  in-licence F corpora, and 224 of 1,297 in in-licence D: a sum of per-corpus
  maxima, not one person. One individually owned F corpus, `u:cd318a65ce47`,
  holds 1,219 of the 2,337 in-licence F ancestry triples. Bots hold 262 of
  4,829 modifying edits.

**What the inputs of the real concurrent cases show** (the reads disclosed
above):

- **D merges.** Of 144 path-level evaluable merges, 9 have exactly one
  flowchart fence in every input. In none of the 9 does the fence change on
  both legs. 4 of the 9 are generated `docs/` copies in `mermaid-js/mermaid`.
- **D pull requests.** None of the 7 has exactly one flowchart fence in every
  input. One is in a read-only corpus.
- **F merges.** 14 cases before §7.4's sibling rule. In the 13 whose inputs
  were read, both legs change the diagram. 9 are one file in one single-author
  corpus, `docs/deps/graph.mmd`, beside `graph.dot`, `graph.json` and
  `graph.svg` that change with it in every commit. The sibling rule excludes it
  as derived output. That leaves **5** cases in four corpora:
  `Cogni-AI-OU/cogni-ai-agents` (2), `CGIC-AI/psfn-framework` (1, read only),
  `u:954608073c97` (1), and `seqeralabs/nf-metro` (1, whose inputs were not
  read: an earlier count script missed it).

**1.5 What this means, stated before any merge is run.** The identity group
(§5.3) can be produced only by real concurrency (§8.5). This census holds at
most 14 such cases, and 5 once derived output is excluded. A floor that
supports a bound of 5% needs 60. A wider search would add mostly single-author
history: `kubernetes/enhancements` (3,709 merges) and `backstage/backstage`
(22,111 merges) show no evaluable both-sides merge on a flowchart file at all.
**An estimate, not a measurement:** at the rate this census found, 5 cases in
the 113 stratum-F corpora that code search supplied, 60 cases would need on the
order of 1,400 comparable corpora, each already a corpus with real edit
history. Code search returned 1,643 repositories in all, of which 113
qualified. **So identity NOT FOUND is unreachable on any public census. The
identity group is expected to end NO VERDICT** unless one of the 5 cases is a
FOUND.

The structure group has thousands of replayable triples and can reach its
floor, mostly through P.

**1.6 Never-merged concurrent legs.** Measured to decide whether they could
serve as real history for identity. Counts from trees, then the one-fence
filter over the evaluable cases' inputs (`census/README.md`).

| source | corpora | examined | touching a flowchart path | both sides changed | evaluable | with one flowchart fence in every input | fence changed on both legs |
|---|---|---|---|---|---|---|---|
| closed-unmerged pull requests, F | 117 listed under the first rules | every `refs/pull/*/head` | 1,314 candidates; 205 closed unmerged | 145 (139 add/add) | **0** | — | — |
| closed-unmerged pull requests, D | 10 | every `refs/pull/*/head` | 621 candidates; 161 closed unmerged | 90 | 51 paths | 6 (5 in `open-telemetry/opentelemetry-specification`, 1 in `apache/airflow`) | **0** |
| fork divergence | 27 with ten or more forks | 1,512 forks fetched (100 most-starred each); 205 with commits of their own | 1 | 0 | **0** | — | — |

For `apache/airflow`, `backstage/backstage` and `grafana/grafana` the
candidate search maps each touching commit to one pull request only, so their
counts are lower bounds. On `mermaid-js/mermaid` that method found 15 of the
16 evaluable pull requests the exact method found. **Never-merged work supplies
no identity-eligible case**, so option (b) is not offered (§0.1, row 4).

**1.7 What this spike does not measure.** Each item is listed in every
published outcome:

- the canvas formats and their census (`spike/canvas/`);
- the relational override layer (`DESIGN-BRIEF.md` §2);
- other text diagram languages (Graphviz DOT, D2, PlantUML), which may share
  Mermaid's rule that an edge creates the nodes it names;
- whether a FOUND shape is already avoided by some existing format (§0.3);
- Mermaid diagram types other than flowcharts, and multi-fence Markdown files;
- identity defects in never-merged concurrent work (§1.6 found no eligible
  case).

## 2. The questions

> **Q-I (the premise). In the real editing history of the pinned corpora, does
> stock `git merge` of a Mermaid flowchart ever produce a clean merged file
> that Mermaid parses, and that is wrong about which nodes exist or which node
> an edge, membership or label names (§5.3, identity group) — where "wrong" is
> decided by a model-level three-way merge independent of git (§5), and no lint
> over the merged file alone reveals it (§5.4)?**
>
> **Q-S. How often does the same happen for lost or duplicated edges, lost
> nodes, subgraph membership and labels (§5.3, structure group)?**

Q-I asks whether the defect exists in real history. It has no frequency
answer (§1.5). Q-S asks for a frequency bound.

## 3. Population

**Stratum F (files).** Paths ending in `.mmd` or `.mermaid`, at any commit
reachable from the pin, whose diagram is a flowchart.

**Stratum D (documents).** Paths ending in `.md` holding exactly one Mermaid
fence, whose diagram is a flowchart. The fence's body is the diagram. The rest
of the file is context for git.

**A Mermaid fence** opens on a line matching, case-insensitively,
`^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b` and closes on the next line
holding only a run of the same character at least as long.

**A flowchart** is a diagram whose first line that is not blank, not a `%%`
comment, and not inside a leading `---` front-matter block starts with
`flowchart`, `flowchart-elk` or `graph`, in lower case, followed by whitespace
or the end of the line. This matches Mermaid's detector, which is
case-sensitive: `Flowchart TD` and `GRAPH TD` raise `UnknownDiagramError`
(`census/v4-error-texts.out`). The census scripts matched the keyword
case-insensitively, but no flowchart at the pin of any listed corpus has a
mixed-case header: 0 of 1,230 in stratum F and 0 of 520 fenced diagrams in
stratum D (`census/README.md`). Earlier versions are not counted; Arm 0 counts
them as files that do not parse.

**Why one fence only.** With two or more fences, which fence in one version is
which in another is blockspec's question, not this one. A case whose three
inputs do not each hold exactly one Mermaid fence, all flowcharts, is excluded
and counted. A merged file that does not is a G0 record (§5.3).

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

## 6. FOUND records

A record is a FOUND record only if all nine hold.

- **F1. Real history.** Its inputs come from a pinned corpus through M-merge,
  M-PR or P. **The record names its arm.** S never yields FOUND. Never-merged
  work is not an arm (§0.2).
- **F2. Stock git only.** `git merge` runs in a fresh repository with
  `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, an empty `HOME` and
  `XDG_CONFIG_HOME`, and no `.gitattributes`. git's version is in every
  transcript.
- **F3. Well-formed.** All four states parse under R and are in the subset.
- **F4. Tier A**, as §5.4 computes it.
- **F5. Not the author's own result (P only).** For P, the merged value also
  differs from the real later version (§8.3). For M, F5 holds trivially: the
  refusal and new-failure rules of §5 already require that the inputs did not
  carry the fault.
- **F6. Silent.** No object of the record newly fails a lint.
- **F7. Confirmed.** X reports the same category on the same objects.
- **F8. It reproduces.** The reproduction script, part of the harness at the
  validation commit, regenerates the record byte for byte from the bundles.
- **F9. Its group is not VOID** (§10.4).

**Identity records from P.** §8.5 argues that P cannot produce an identity
record. One that appears anyway is a **P anomaly**: listed in the outcome,
investigated in the log, never FOUND, and it counts toward no verdict. Its case
still counts toward the structure floor if it is otherwise decided, since its
structure records are judged as usual.

**No tier-A record vanishes.** A tier-A record that fails any of F1–F8 is a
**blocked record**, listed in the published outcome with the condition it
failed. A blocked record blocks NOT FOUND only for its own group, and only if
its case is among the decided cases counted toward that group's floor (§9.1).
A record that meets F1–F8 and fails only F9 is reported as "found in a voided
group" (§9.1).

## 7. Corpora

### 7.1 Named and pinned

The corpora are the rows of `census/corpora-public.tsv` whose status is `in`
or `read-only`. Its sha256 is
`2bc5e099c71f231cd5c4c9e3430038660af616e13182082f1e63cfdc9caaf22f`. In rows labelled `u:`, the pin is
published only as `h:` plus 16 hex digits of `sha256(salt + ":pin:" + pin)`,
because a commit search on a pin finds its repository. The real pins are in the
owner's private table. The rule was applied
mechanically to the census: a corpus is listed if it is not a fork, its
licence is acceptable (§7.2), and its selected paths, after §7.4, have a
triple on an ancestry chain or an evaluable both-sides case. Stratum D lists
ten large multi-author projects chosen by name before their counts were taken.
Pins are each repository's default-branch head when cloned. **Pins never
change.**

### 7.2 Licences

Licences come from `gh api repos/<r> --jq .license.spdx_id`, and from the
licence file's first lines where that prints `NOASSERTION`.

- **In:** MIT, Apache-2.0, BSD, ISC, 0BSD, Unlicense, CC0-1.0, CC-BY-4.0, and
  the W3C Software and Document License.
- **Read only:** GPL, LGPL, AGPL, MPL-2.0, CeCILL, CC-BY-SA-4.0.
- **Out:** no licence; non-commercial licences (PolyForm Noncommercial, CC
  BY-NC-ND); Commons Clause; evaluation-only and all-rights-reserved terms; the
  Open BSV License.

A finding quotes corpus text under the corpus's own licence, with attribution.
Fixtures are CC0-1.0 (org contract §6), so corpus text enters a fixture only
from a CC0-1.0, 0BSD or Unlicense corpus.

### 7.3 Read-only corpora

A read-only corpus is measured. No byte of it is quoted. In every committed
output, each id, label, title and path segment from it is replaced by `h:` and
the first 16 hex digits of its sha256. A FOUND from one is reproduced by
corpus, commits and path hash. The reader fetches the files.

### 7.4 Selection

- Paths are read NUL-separated with `core.quotepath=off`.
- **Generated, by path.** A path is excluded if any directory segment,
  case-folded, is one of `testdata`, `test`, `tests`, `__tests__`,
  `__snapshots__`, `snapshots`, `baseline`, `baselines`, `fixture`,
  `fixtures`, `generated`, `gen`, `dist`, `build`, `out`, `node_modules`,
  `vendor`.
- **Generated, by declaration.** A file is excluded if one of its first ten
  lines matches `auto-?generated|do not edit`, case-insensitive.
- **Generated, by sibling.** A stratum-F path is excluded if the directory
  holding it, in the tree of the path's last version, also holds a file with
  the same stem and the extension `.dot` or `.json`, **and** that sibling
  changed in at least half of the commits that added or modified the path. A
  second machine format of the same graph, regenerated with it, marks the
  flowchart as derived output. In a listing of every such pair in the cloned
  corpora (`census/README.md`), counting add and modify commits only, 850 of
  866 co-change in at least half the commits; the other 16, such as 0 of 3,
  look hand-kept. A rendered `.svg` or `.png` alone
  does not count, because people commit renders of diagrams they wrote.
- **Bots.** Commits by bots count. An author whose name or email contains
  `bot`, case-folded, is a bot. Shares are reported per corpus. Commits written
  by an assistant under a person's name cannot be told apart, and that is
  disclosed.

### 7.5 Unit, authors, caps and floors

- A **case** is keyed by the sha256 of its three input texts, in order (for D,
  the fence bodies). Two cases with identical pairs of model diffs are one
  case. Every floor and rate counts distinct cases.
- A case is **decided** if its three inputs are in the subset, each leg
  changes the model, no record in it is UNRELIABLE (§8.3), and its outcome is
  E or a merged state in the subset. **E counts as decided**: git refusing is
  an outcome. OUT-OF-SUBSET does not.
- **An author** is a connected set of commit identities that share a
  case-folded email, or a case-folded name. A GitHub noreply address
  `<id>+<login>@users.noreply.github.com` is read as `<login>`. **A case's
  authors** are the authors of the last commit on each leg that changed the
  path. A case counts toward each of its authors' caps.
- **The principle for floors and caps,** stated before any merge is run: a
  NOT FOUND claims a frequency below a bound, so the floor is the smallest `n`
  whose bound `3/n` is at most 5%, which is 60. No corpus and no author may
  carry a verdict alone, so neither supplies more than half of a floor, which
  is 30.
- P contributes at most one case per `(path, i)` to a floor (§8.3).

### 7.6 Archive

Each corpus is fetched with its `refs/pull/*/head` refs and archived as a git
bundle. Its merged pull-request list (number, head sha, merge-commit sha,
commit count, from `gh api`) is saved as JSON. Each bundle's and list's sha256
is committed at validation. A pin absent from its bundle makes that corpus NO
VERDICT.

## 8. Arms, in order

### 8.1 Arm 0: a census, no merging

At each pin, over the whole selection, per corpus and stratum:

- selected paths, distinct blobs, blobs that R parses, blobs in the subset,
  every refused construct with its count;
- statement kinds by count, including implicit nodes, nodes declared more than
  once, edge ids, `linkStyle`, nested subgraphs, subgraphs without an explicit
  id, and blobs out of the subset for a repeated untitled title;
- M-merge and M-PR cases, split into multi-base, add/add, delete/modify,
  convergent, excluded by the one-fence rule, and evaluable;
- **exposed** M cases (§5.5), from inputs only;
- P triples, split into predecessor chain or not, constructible,
  non-commuting, and out of subset;
- author and bot shares of the edits each arm uses;
- the edit mix: each real modifying edit's model diff, classified into
  Appendix B's operations.

**The coverage bar.** A stratum with fewer than 90% of its distinct blobs in
the subset contributes no case to any floor. A FOUND record from it still
counts, since F3 checks its own four states.

### 8.2 Arm M: real concurrency, a census

- **M-merge.** Every two-parent merge reachable from the pin with one merge
  base, where a selected path changed on both parents. Multi-base, add/add,
  delete/modify and convergent cases are dropped and counted. The rest are
  re-merged under F2, and each selected path is classified.
- **M-PR.** Every pull request in the archived list whose merge commit `c` is
  reachable from the pin and has one parent. Its target leg is decided by
  patch-id (`git patch-id --stable`):
  - **Rebase merge.** Let `k` be the pull request's commit count from the API.
    If `c~0` … `c~(k-1)` are all non-merge commits and their patch-ids, oldest
    first, equal the patch-ids of the pull request's own commits in order, the
    target leg is `c~k`. The commit list is read from the API with pagination
    to its end; GitHub lists at most 250 commits for a pull request, so a pull
    request with `k` above 250 is excluded and counted.
  - **Squash merge.** Otherwise, if the patch-id of `git diff c^ c` equals the
    patch-id of `git diff <merge-base(head, c^)> <head>`, the target leg is
    `c^`.
  - **Otherwise** the case is excluded and counted. That covers a multi-commit
    pull request whose single-parent merge commit sits on top of another pull
    request's commits.
  - A one-commit pull request matches both rules with the same target.

  Base is the merge base of the head and the target leg. A case is kept only
  if a selected path changed on both legs. The same drops apply.
- **Reproduction check.** For each path git merges cleanly, whether its blob
  equals the blob the corpus recorded is reported. A mismatch is labelled, not
  excluded: a person may have repaired the file.

### 8.3 Arm P: real consecutive edits, replayed as concurrent

For each selected path, list its versions: the blob at each non-merge commit
that adds or modifies it, in `git log --topo-order --reverse --no-renames`
order, with consecutive identical blobs merged. A delete ends the list; a
re-add starts a new one.

**The predecessor rule.** `V[j]` is the predecessor of `V[j+1]` only if the
commit of `V[j]` is an ancestor of the commit of `V[j+1]`, and the path's blob
at the first parent of `V[j+1]`'s commit equals `V[j]`. So each step is one
commit's own edit, and no step spans an edit merged in from elsewhere.

For each `i` and each `(a, b)` in `{(1,1), (1,3), (3,1)}`, every consecutive
pair from `V[i]` to `V[i+a+b]` must meet the predecessor rule. Otherwise the
case is dropped and counted.

- **base** is `V[i]`; **leg O** is `V[i+a]`; **truth** is `V[i+a+b]`.
- **leg T** is `V[i]` with the line edits from `V[i+a]` to `V[i+a+b]` replayed
  on it (Appendix B.1). If any edit cannot be placed, the case is
  **non-commuting**, dropped and counted.

**Records are judged against the truth.** A record is a P record only if the
merged model also differs from the truth's model on that unit. If the decided
value differs from the truth on a unit that neither leg touched, the record is
**UNRELIABLE**: reported, excluded from FOUND, not an extractor failure, and
its case does not count toward a floor.

For a floor, a `(path, i)` contributes its `(1,1)` case if decided, else its
`(1,3)`, else its `(3,1)`.

### 8.4 Arm S: scripted edits on real files

S's rates are **properties of the edit generator** (Appendix B.2), not of real
editing. For example, B.2 inserts new statements at the same place on both
legs, which raises its E rate. S never yields FOUND and never supports NOT
FOUND, and every place that reports an S rate says it is the generator's.

- **Bases.** Distinct in-subset texts of selected paths, ranked by
  `sha256("nodespec-mermaid:S:" + stratum + ":" + blob_sha)`; the 100 lowest
  per stratum, or all.
- **Pairs.** Per base, 10 pairs at 1 edit per leg and 10 at 3.
- **Edits.** Drawn from Arm 0's frozen mix, or Appendix B's fixed mix if fewer
  than 100 real edits were classified, and applied as Appendix B.2 says.
- **Randomness.** Each leg uses `random.Random(seed)`, where `seed` is the
  first 16 hex digits of `sha256("nodespec-mermaid:S:" + stratum + ":" +
  blob_sha + ":" + k + ":" + pair + ":" + leg)`, as an integer. There is no
  other randomness. No ranking or seed was computed before this merged.
- S reports, per stratum: the generator's exposed share of pairs, and among
  exposed pairs the share that comes out E, B and tier A.

### 8.5 What each arm can detect

| shape | M | P | S |
|---|---|---|---|
| I1 dangling (hole #2) | **yes** | **no** | generator rate |
| I2 collision (hole #3) | **yes** | **no** | generator rate |
| I3 delete/modify | **yes** | **no** | generator rate |
| I4 kind clash | **yes** | **no** | generator rate |
| G0 diagram | yes | only if merged ≠ truth | generator rate |
| G1 node | yes | only if merged ≠ truth | generator rate |
| G2 edge lost or extra | yes | only if merged ≠ truth | generator rate |
| G3 membership | yes | only if merged ≠ truth | generator rate |
| G4 label | yes | only if merged ≠ truth | generator rate |

**Why P cannot detect the identity group.** Leg T's edits were made by someone
who had already seen leg O. So T never names an id that O removed, unless the
author meant a new node, in which case the truth holds the same node and the
merge equals the truth. T never adds an id that O added, for the same reason.
T never changes a unit O deleted, because that unit is absent from `V[i+a]`,
where T's edits start. The reverse order (an edge added, then its end renamed)
makes T rewrite a line absent from `V[i]`, which is non-commuting. **So the
identity group is measurable only through M**. An identity record that P
produces anyway is a P anomaly (§6).

**What P can never see.** A defect whose merged result equals the later real
version. The author accepted that state, so P cannot call it wrong.

## 9. Verdicts

### 9.1 Per group

**Identity group** (I1–I4):

- **FOUND (arm)** if at least one record meets F1–F9. The arm is named.
- Otherwise **NO VERDICT**, with the first of these reasons that applies:
  - **VOID**, or a disputed sealed identity fixture (§10.4): named as such;
  - **not exposed**: `k = 0`. Only this outcome may say that real history did
    not test the premise;
  - **`k` exposed, none silent**: `k ≥ 1`, where `k` counts the distinct
    exposed M cases (§5.5) whose three inputs are in the subset, **whatever
    their outcome**: E, B, blocked, DUP-TITLE or OUT-OF-SUBSET merged state.
    Each is reported by corpus, arm and outcome. This is data, not a bound.
- There is **no identity NOT FOUND**.

**Under owner row 4 (c)** instead of (a). The real-history census runs as
above, and a real-history record that meets F1–F9 is still **FOUND (arm)**.
Otherwise the identity verdict is the first of these that applies:

- **NO VERDICT (VOID)** or **NO VERDICT (disputed)**, if the identity group is
  VOID or has a disputed sealed fixture (§10.4), exactly as under (a). Either
  takes precedence over the labels below.
- **MECHANISM SHOWN, frequency unmeasured**, if S reports a non-zero generator
  rate of tier-A identity records in at least one stratum. Only S records that
  X confirms count: an S identity record X does not confirm drops out of the
  rate.
- **MECHANISM NOT SHOWN**, if that X-confirmed rate is zero in every stratum.

**Precondition, not a condition.** V3's bare-style hole plants (hole #2 as I1,
hole #3 as I2, both clean under F2's git, parsed by R, tier A from H), with X's
agreement in V5, demonstrate the mechanism. They must pass before the
validation commit, and a failed V step stops the work (§11.2). So by the time
a verdict is computed they have passed, and only the S condition can produce
MECHANISM NOT SHOWN.

Neither label is FOUND, and neither comes from real history. The published
text gives S's rate as a property of the generator and says that how often the
defect happens in real editing is unmeasured. F1 is unchanged: S never yields
FOUND. Under (a), these labels are not computed.

**Structure group** (G0–G4 and eligible MC):

- **FOUND (arm)** if at least one record meets F1–F9.
- **NOT FOUND** if no record meets F1–F9, and all of these hold:
  - **floor:** at least **60** distinct decided cases (§7.5) under the caps,
    from M and P, from strata that pass the coverage bar. These are **the
    group's decided cases**;
  - **agreement:** over the group's decided cases, H and X agree (§10.5) on at
    least 98%. Agreement over zero cases fails;
  - **no tier-A disagreement:** no decided case has a structure tier-A record
    from H that X lacks, or from X that H lacks;
  - **no blocked record** of this group among the decided cases (§6);
  - **no disputed sealed fixture** of this group on the A/not-A or B/not-B line
    (§10.4);
  - the group is not VOID.

  It reports `n` split by arm (M-merge, M-PR, P) and the bound `3/n` at 95%.
  **If P supplies more than half of `n`, the bound is stated as a bound on real
  consecutive edits replayed as concurrent, not on real merges.**
- **NO VERDICT, with its reason,** otherwise. It is never reported as zero.

A disputed sealed fixture blocks only NOT FOUND. A FOUND stands beside it. A
record that meets F1–F8 but fails F9 is reported as "found in a voided group",
and the group stays open.

### 9.2 Overall

The published outcome is the pair (identity verdict, structure verdict). Only
the identity verdict answers the premise.

- **Identity FOUND (arm).** Named identity, as Mermaid has it, merged silently
  wrong at least once in real history.
- **Identity NO VERDICT (not exposed).** Real merged history did not test the
  premise.
- **Identity NO VERDICT (`k` exposed, none silent).** Real merged history put
  the premise at risk `k` times, and each time git refused, a lint saw it, or
  the case could not be judged. It is not a bound and not "do not build".
- **Identity NO VERDICT (other reason).** The reason is named.
- **Identity MECHANISM SHOWN, frequency unmeasured** (row 4 (c) only). The
  defect can be built and git does not refuse it; real editing was not shown
  to produce it.
- **Identity MECHANISM NOT SHOWN** (row 4 (c) only). Named as such, with
  which condition failed.

Every outcome lists §1.7, each corpus and stratum that lacked coverage, every
blocked record with the condition it failed, every P anomaly, and:

- **"… with refusals":** each tier-B record, with its lint;
- **"… with near misses":** each tier-C record;
- **"… generator rates in S":** S's rates, labelled as properties of the
  generator, with `n`.

## 10. Independence

### 10.1 Roles

- **H, the harness author.** Writes H, the oracle, the arms, the R wrapper and
  the aggregator, and runs them. May not write fixtures or X.
- **F, the fixture author.** A fresh agent with no copy of the authoring
  conversation. Writes V-fixtures and sealed fixtures.
- **X, the second-extractor author.** A different fresh agent, also with no
  copy. Writes a second parser, oracle and categorizer, from this document.
  **Only X's author edits X**, and each edit is a new invocation with a logged
  prompt.

### 10.2 The model

F and X run on the pinned model `claude-opus-5-5`. If it is not served on the
day a role starts, the role uses the most recent `claude-opus-*` model the
Models API lists that day, and the choice is logged.

### 10.3 What each blind role gets

Each works in an **exported directory**: a `git archive` of the permitted paths
only, with no `.git`, and no nodespec, blockspec or research checkout. A git
worktree is not a barrier, because it shares the object store.

- **F gets:** this document, Mermaid 12.1.0's `docs/syntax/flowchart.md`, and
  Appendix D's fixture contract. Not the harness.
- **X gets:** §4, §5, Appendices A and C, the same Mermaid document, and
  Appendix D's extractor contract. Not the harness, not R, and not the
  fixtures.

**The stop rule.** An agent that finds it can read the harness, the other
role's work or any repository history stops and says so, and does not continue
carefully. **Network access is honour-system**, because every kindspec
repository is public; Appendix E's prompts forbid fetching them.
`spike/mermaid/LOG.md` records what each agent was given: the export manifest
with each file's sha256, the prompt as sent, the model id and the date.

### 10.4 Fixtures

- **Fixtures are synthetic.** F writes them. Corpus text may enter one only
  from a CC0-1.0, 0BSD or Unlicense corpus (§7.2).
- **V-fixtures** go to H and X for V3 and V5: at least three per category
  (I1–I4, G0–G4, MC, C, D, S-LINKSTYLE, S-ORDER, B, E), at least three exposed
  cases that git refuses, and at least three clean cases, in both strata.
- **Sealed fixtures.** At least twelve: at least three I1 (one of them in bare
  `A --> B` style, so tier A), two I2, one I3, two structure, two B (a ghost
  that L1 sees) and two clean, across both strata. F packs them as a
  deterministic tar, draws a 32-byte nonce from `os.urandom`, and gives H only
  `sha256(nonce + tar)`. H commits it in the validation commit. **The owner
  holds the tar and the nonce** until commit 6. They are then committed and
  run through H and X at their validation shas.
- **VOID.** A group is void if, on any of its sealed fixtures, H's tier falls on
  the wrong side of the A/not-A or B/not-B line **and X agrees with F's
  expectation**.
- **Disputed.** If X agrees with H instead, on either line, the fixture is
  disputed and logged with the three answers. A disputed fixture of the
  structure group makes that group NO VERDICT for NOT FOUND, and leaves FOUND
  alone. A disputed fixture of the identity group makes a non-FOUND identity
  verdict NO VERDICT (disputed), and leaves FOUND alone.
- Confusion inside one tier (I1 with I3, G2 with G4) voids nothing.

### 10.5 The second extractor

X runs on **every decided case** in M and P, every exposed case, every FOUND
candidate and every sealed fixture. For one case, H and X **agree** if they
report equal sets of `(category, objects)` and the same exposure. **A crash, a
timeout or an empty output from X is a disagreement**, never an agreement. A
FOUND candidate they disagree on is **disputed**: a blocked record, not a
finding. A tier-A disagreement in either direction blocks the structure
group's NOT FOUND (§9.1).

## 11. Validation, and the order of work

### 11.1 First execution binds

**The first execution of each arm binds, and its output is the content of its
commit. Every invocation of an arm, the aggregator, a blind role or the
sealed run writes a transcript under `spike/mermaid/results/`, aborted runs
included, and every transcript is committed.**

### 11.2 V steps

A V step fails when its committed transcript shows a non-zero exit, a `cmp` or
sha256 mismatch, or a surviving or BROKEN mutant. V steps run only before the
validation commit, whose harness sha binds. A failed V step stops the work
until it is fixed and re-validated.

- **V0. The renderer.** R installs from the committed lockfile with
  `--ignore-scripts`, then runs with the network off, under Node v24.20.0, with
  §4.4's configuration, the jsdom globals set before Mermaid is imported. On
  planted texts it shows each behaviour Appendix A relies on, as
  `census/v0-probes.out` recorded it:
  - an edge to an undeclared id creates that node, with its id as label and no
    shape;
  - a node declared twice keeps the last label and the last shape;
  - a node mentioned in two subgraphs belongs to the first to close;
  - **node versus edge id, both orders:** an edge id `e1` used before a node
    statement `e1[…]` swallows the node; a node `e1` declared first coexists
    with an edge id `e1`;
  - a duplicate user-defined edge id falls back to an automatic id, with
    `isUserDefinedId` false;
  - an edge to a subgraph's id creates a vertex with that id and no shape;
  - subgraphs without an explicit id get `subGraphN` by position, and
    renumber when one is inserted earlier (probe3, probe4); keyed by title,
    probe4's correct three-way merge yields no I record;
  - edge text is not entity-decoded; a `click` URL is normalized and adds the
    class `clickable`;
  - a chart of 600 edges parses under §4.4's `maxEdges`, and fails under the
    default;
  - a syntax error throws an error with `hash`, and the text does not parse;
  - **four errors without `hash`**, each followed by a canary that parses, so
    each text does not parse: `linkStyle 5 stroke:#f00` with one edge
    (`TypeError`, "Cannot set properties of undefined (setting 'style')");
    `A@{ shape: notashape, label: "x" }` (`Error`, "No such shape:
    notashape."); `Flowchart TD` and `GRAPH TD` headers
    (`UnknownDiagramError`, "No diagram type detected …"); 600 edges under a
    limit of 500 (`Error`, "Edge limit exceeded. 500 edges found, but the
    limit is 500.");
  - **a labelled chart** (`A[Alpha] --> B`) without the jsdom globals throws a
    `TypeError` with no `hash`; the canary fails the same way, and the wrapper
    aborts with a non-zero exit instead of reporting "does not parse";
  - an edge end that names an earlier user-defined edge id (`A e1@--> B`, then
    `e1 --> C`) yields an edge whose start is `e1` with no vertex `e1` (probe3,
    `edgeFromEdgeIdNode`); H refuses it;
  - an explicit `subgraph subGraph0 [T]` after an untitled subgraph merges into
    R's numbered `subGraph0`; H refuses it.

  **If R cannot run this way, that is a gap found before Arm 0 (§11.4): the
  work stops for the owner.**
- **V1. Subset agreement.** H's model equals R's on every V-fixture, under
  Appendix A's mapping, and H refuses each out-of-subset construct listed in
  Appendix A, including a chart with two untitled subgraphs of the same title.
- **V2. Replay.** Appendix B.1's replay reproduces `V[i+a+b]` when applied to
  `V[i+a]`, on every V-fixture with a history.
- **V3. Every component goes red on a planted case, and on empty input.**
  - Each category fires on its V-fixtures and stays silent on clean ones.
  - **Both canonical holes, both styles, both strata:** hole #2 with a
    declared label comes out B through L1, and in bare style I1; hole #3 with
    differing labels comes out B through L2, and with only `class`, style or
    `click` differing I2.
  - **Positional subgraph ids:** probe4's case (one leg deletes an untitled
    subgraph, the other adds a node to another) yields no I record.
  - **Membership is not a reference** (`census/synth-results.out`, each case
    merged with stock git in a fresh repository; each becomes a plant):
    - retitle an untitled subgraph on one leg, add a member on the other:
      clean, no record (`retitle`, `wordToTitle`);
    - rename an explicit subgraph id on one leg, add a member on the other:
      clean, no record (`renameExplicit`);
    - unwrap a subgraph on one leg, add a member on the other: clean, no record
      (`unwrap`);
    - delete a subgraph and its members on one leg, add a member on the other:
      E (`deleteBox`);
    - rename an explicit subgraph id on one leg, add `X --> fe` to the old id on
      the other: clean, **I1** on `fe`, and **tier B** through a new L1
      failure, because `fe` becomes an implicit node (`renameExplicitRef`);
    - both legs add an untitled subgraph titled `Cache Layer`: DUP-TITLE
      (`dupAdd`);
    - `X --> subGraph0` with an untitled subgraph inserted earlier on the
      other leg: G2 (`posRef`);
    - move member `C` from one box to another on one leg, while the other leg
      retitles both untitled boxes: clean, no record, no MC
      (`moveRetitleBoth`);
    - the same with explicit ids, `fe`→`ui` and `be`→`api` on the other leg:
      clean, no record, no MC (`moveRenameBothExplicit`). Under the earlier
      rule, both gave a false eligible MC, G3, at tier A
      (`census/synth-results-v40rule-control.out`).
  - **Edge to a subgraph:** `A --> S`, where `S` is a subgraph id with no node
    statement, is a reference, not an I4.
  - **I4 is relative:** a node-versus-edge-id clash present in the base
    yields no record; one introduced by the merge yields I4.
  - **Blocked records:** a tier-A record that X does not confirm is listed as
    blocked, blocks NOT FOUND of its own group only, and only from a counted
    decided case.
  - **P anomaly:** an identity record planted in a P case is listed, never
    FOUND, and changes no verdict; the same case, otherwise decided, counts
    toward the structure floor.
  - **Exposure** is computed from inputs alone: changing the merged file does
    not change it.
  - **Per-path E.** A D file whose prose conflicts and whose fence merges
    wrong is E.
  - **Fences.** Openers with leading spaces, upper case, `mermaid-example`
    and a header of `flowchart-elk` are recognised. A D input with two fences
    excludes the case; a merged file with two fences is G0.
  - **Generated rules.** A path under `testdata/`, a file declaring
    `auto-generated`, and a `graph.mmd` beside a `graph.dot` that changes with
    it in every commit are excluded. A `graph.mmd` beside a `graph.dot` that
    changes with it in fewer than half its commits, and one beside only
    `graph.svg`, are not.
  - **M-PR.** A planted rebase merge of three commits takes `c~3`. A planted
    ten-commit squash merge whose diff equals the pull request's net diff takes
    `c^`. A planted single-parent commit whose parent is another pull
    request's commit, matching neither rule, is excluded and counted. A
    planted pull request of 251 commits is excluded and counted; one of 120
    commits is read across two pages of the API.
  - **P.** A non-ancestral pair, and a step whose first-parent blob differs
    from its predecessor, each drop the case. A record equal to the truth is
    not a P record. An UNRELIABLE record's case does not count toward the
    floor. A replay that cannot place an edit is non-commuting.
  - **Authors.** Two identities sharing an email, and two sharing a name, are
    one author each; a noreply address maps to its login.
  - **Hermetic merge.** A `~/.gitconfig` and `~/.config/git/attributes`
    setting `merge=union` change no result.
  - **Redaction.** A planted read-only corpus's label, a planted individual
    owner's name, and **any commit sha from a planted individually owned
    corpus** (its pin included, in full or as a 7-character prefix) do not
    appear in any committed output; the same check run on an unredacted table
    finds them.
  - **X failure.** An X that crashes, or prints nothing, makes its case a
    disagreement.
  - Arm 0, M, P and S exit non-zero on an empty corpus and on a pin absent
    from the bundle.
  - **Units and caps.** A duplicated triple counts once; a copied file with the
    same diffs counts once; the cap stops at 30 for a corpus and for an author.
  - **Every verdict path is reachable**, each by its own planted input to the
    aggregator:
    - identity FOUND (M-merge) and FOUND (M-PR); structure FOUND (P);
    - identity with 0 exposed cases gives NO VERDICT (not exposed);
    - identity with one exposed case whose merged state is OUT-OF-SUBSET gives
      NO VERDICT (1 exposed, none silent), never "not exposed";
    - identity with 60 exposed cases, some E and some B, gives NO VERDICT (60
      exposed, none silent), never NOT FOUND;
    - identity with a disputed sealed fixture gives NO VERDICT naming it;
    - identity VOID turns a FOUND into "found in a voided group";
    - structure NOT FOUND at 60 decided cases of which some are E; 59 gives NO
      VERDICT;
    - 60 structure cases with 31 from one corpus, or 31 from one author, gives
      NO VERDICT;
    - P supplying 31 of 60 gives NOT FOUND stated as a bound on replayed
      edits;
    - 97.9% agreement gives NO VERDICT; agreement over zero cases gives NO
      VERDICT;
    - one structure tier-A record from H only gives NO VERDICT; one from X only
      gives NO VERDICT;
    - one blocked structure record among the decided cases gives NO VERDICT;
      one blocked identity record does not touch the structure verdict;
    - a disputed structure fixture on the A/not-A line, and one on the
      B/not-B line, each give NO VERDICT for NOT FOUND and leave a FOUND
      standing;
    - a structure VOID group turns a FOUND into "found in a voided group";
    - a stratum at 89.9% coverage adds nothing to the floor, and its FOUND
      still counts;
    - P cases never count toward identity;
    - one exposed case whose merged state is DUP-TITLE gives NO VERDICT (1
      exposed, none silent);
    - **row 4 (a):** with no real FOUND, the identity verdict is a NO VERDICT
      label and never MECHANISM SHOWN;
    - identity VOID with no FOUND gives NO VERDICT (VOID);
    - **row 4 (c):** with no real FOUND, a non-zero X-confirmed S rate gives
      MECHANISM SHOWN, frequency unmeasured; S identity records that X does
      not confirm, leaving an X-confirmed rate of zero, give MECHANISM NOT
      SHOWN; a zero S rate gives MECHANISM NOT SHOWN; a VOID identity group
      gives NO VERDICT (VOID), and a disputed identity fixture gives NO
      VERDICT (disputed), each in place of MECHANISM SHOWN; a real FOUND gives
      FOUND (arm), not MECHANISM SHOWN. The V3 bare-style hole plants, with
      X's agreement in V5, are a precondition of this run.
  - The aggregator exits non-zero on empty input. The reproduction script
    regenerates a V-fixture's record byte for byte.
- **V4. Mutation sweep** over every gate, in the style of blockspec's
  `armed_check.sh`. Each mutation is hash-checked before and after, and one
  that does not apply is BROKEN. It passes only with every mutant killed and
  none BROKEN.
- **V5.** X agrees with H on every V-fixture. A disagreement is fixed in H by H,
  or in X by a new invocation of X's author, and is logged.

### 11.3 Commit order

Separate commits, in this order:

1. this pre-registration, with `census/` and `corpora-public.tsv`, merged;
2. the blind roles' output: V-fixtures, X, the sealed hash;
3. validation: H's sha, X's sha, the lockfile's sha256, Node's and git's
   versions, R's configuration, V0–V5 transcripts, bundle and pull-request-list
   hashes;
4. Arm 0;
5. arms M, P and S, with X's output on every case;
6. **the result commit:** the sealed fixtures, their run, and the verdict.

**H, X and R at commit 3 are the implementation.** Their shas are in
`spike/mermaid/LOG.md`. The result is published when commit 6 is merged to
`main`.

### 11.4 Gaps

A gap is a definition here that the harness cannot implement as written.

- **Before commit 4:** shown by a committed red test, it stops the work, and
  the owner may supersede this document.
- **Between commits 4 and 5:** shown by a committed red test, it makes the
  affected group or stratum NO VERDICT. It is not grounds to supersede.
- **After commit 5:** no gap claim, code change or later supersession alters
  any verdict.

## 12. What each outcome publishes

All are deliverables. A result that would stop a kind goes to the owner first
(org contract §7).

- **FOUND.** The reproduction: corpus, arm, commits, the four texts (hashed for
  a read-only corpus), the `git merge` command line, the decided values, the
  record, and H's and X's output.
- **FOUND from an individually owned corpus.** It counts like any other
  FOUND. The published record names the corpus by its `u:` label, with commits
  and texts hashed. The owner reproduces it from the private mapping. Naming
  the repository publicly would name a private individual, so it needs the
  escalation org contract §7 requires, decided at that time.
- **Structure NOT FOUND.** What was measured, `n` by arm, the bound and what it
  bounds, what was not measured (§1.7), and what would change it.
- **Identity NO VERDICT (not exposed).** The exposure census: per corpus and
  stratum, M cases and their outcomes. It says plainly that real merged
  history did not test the premise.
- **Identity NO VERDICT (`k` exposed, none silent).** The same census, with
  each exposed case's corpus, arm and outcome. It says the premise was put at
  risk `k` times and never failed silently, and that this is not a bound.
- **NO VERDICT (other).** The reason and the census.
- **Identity MECHANISM SHOWN, frequency unmeasured** (row 4 (c) only). The
  label, S's X-confirmed generator rate by stratum with its `n`, and beside
  them the real-history census's own NO VERDICT reason and `k`. It says the
  defect can be built and git does not refuse it, and that how often real
  editing produces it is unmeasured.
- **Identity MECHANISM NOT SHOWN** (row 4 (c) only). The label, S's rates
  (zero after X confirmation) with `n` and the count of S records X did not
  confirm, and beside them the census's NO VERDICT reason and `k`.
- S's rates may appear beside any outcome only as properties of the generator.

## 13. Amendment rules

**Frozen when this merges:** §0, §2–§12, and the appendices.

- **A frozen section that is wrong.** Before commit 4, it may be replaced by a
  further pre-registration that says why. After commit 4, no later
  pre-registration may change a verdict computed here, and that verdict is
  published first.
- **§1** records prior evidence. It may be corrected only where it is wrong
  about a fact, with the original wording kept in the log below.
- **Pins never change.**

Edits made while this is a draft pull request are not amendments.

| date | section | change, with the original wording | reason |
|---|---|---|---|

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

## Appendix B — replay and scripted edits

**B.1 Line replay (arm P).** Compute `difflib.SequenceMatcher(None, A, C,
autojunk=False)` over the lines of `A = V[i+a]` and `C = V[i+a+b]`. For each
opcode other than `equal`, its anchor is the nearest unchanged line before it
in `A`, or the start of the text. Place the edit in `V[i]` after the unique
line equal to the anchor, provided the lines it replaces follow there exactly.
If the anchor is not unique, is absent, or the replaced lines differ, the case
is non-commuting.

**B.2 Scripted edits (arm S).** Operations: relabel a node, rename an id
(every occurrence, as an editor's rename does), add a node, add an edge,
delete a node (and every statement naming it), delete an edge, retarget an
edge end, move a node into or out of a subgraph, add a subgraph, change a
shape, restyle. New statements go after the last statement of their kind, or
inside the target subgraph's block. Because both legs insert at the same
place, S's E rate is higher than real editing would give.

**Fixed fallback mix:** relabel 20%, add edge 18%, add node 15%, delete edge
8%, rename id 8%, delete node 7%, retarget 6%, change membership 6%, restyle
5%, change shape 4%, add subgraph 3%.

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

**Fixtures.** One directory per case: `base.<ext>`, `o.<ext>`, `t.<ext>`, and
`expect.json` holding `{"stratum", "exposed", "records": [{"category",
"objects"}], "tiers", "why"}`. `<ext>` is `mmd` or `md`. Files are exact
bytes, synthetic, under CC0-1.0, as org contract §6 sets for fixtures.

**Extractor.** `python3 -I extract2.py <stratum> <base> <o> <t> <merged>`
prints one JSON object: the decided values, the exposure, and every record with
its category, objects and tier. Pure stdlib. A non-zero exit or empty output
is recorded as a disagreement.

## Appendix E — prompts for the blind roles, verbatim

**F:**

> You are writing test cases for an experiment. Work only with the files in this
> directory. Do not open, search for, or fetch any kindspec repository, issue or
> pull request, locally or over the network. If you find you can read harness
> code or repository history, stop and say so.
>
> Read the pre-registration's §3–§5 and §10.4, and Appendices A, C and D. Write
> the V-fixtures into `v-fixtures/` and the sealed fixtures into `sealed/`, in
> the counts §10.4 sets. Write every fixture yourself; do not copy text from
> any repository. Each fixture must be a three-way case a real author of a
> Mermaid flowchart could produce. For each, state in `why` which rule of §5
> decides each record.
>
> Then pack `sealed/` as a tar with sorted names and zeroed times, owner and
> mode, draw a 32-byte nonce from `os.urandom`, and print only
> `sha256(nonce + tar)`. Give the tar and the nonce to the owner, and to no one
> else.

**X:**

> You are writing a program from a specification. Work only with the files in
> this directory. Do not open, search for, or fetch any kindspec repository,
> issue or pull request, locally or over the network. If you find you can read
> another implementation or repository history, stop and say so.
>
> Implement Appendix D's extractor from §4, §5, Appendices A and C, and the
> Mermaid document given. Where a rule is ambiguous, choose, and write the
> choice and the rule's section into `CHOICES.md`. Do not guess at what another
> implementation does.
