# Fixtures: layout, conventions and readings

Written by F, the fixture author (§10.1). Every fixture is synthetic and was
written for this experiment. No text comes from any repository or corpus.
The fixtures are released under CC0-1.0.

## Layout (Appendix D)

One directory per case: `base.<ext>`, `o.<ext>` and `t.<ext>`, plus
`expect.json`. `<ext>` is `mmd` for stratum F and `md` for stratum D. For
each case, `o` is the leg checked out when merging and `t` is the leg merged
in. Every expectation was checked by merging the three files with stock
`git merge` (git 2.47.3) in a fresh repository with an empty `HOME` and no
system config. Whether a merge is clean depends only on the three texts.

`expect.json`:

```json
{"stratum": "F" | "D",
 "exposed": true | false,
 "records": [{"category": "...", "objects": ["...", "..."]}],
 "tiers": ["A" | "B" | "C" | "D" | "E" | "—"],
 "why": "..."}
```

- `tiers[i]` is the tier of `records[i]` (§5.4). `—` marks a record that is
  reported only (S-ORDER).
- A clean case has `"records": []` and `"tiers": []`.
- `objects` is a sorted list of key strings (§4.1). A node key is its id. A
  subgraph with an explicit id is keyed by the id. A subgraph without one is
  keyed by `title:` plus its title, as in `title:Data layer`. An edge with a
  user-defined id is keyed by that id.
- E and G0 concern the path, not a key. Their `objects` is the placeholder
  `["path"]`.

## Objects per category (§5.3, and where §5.3 is silent)

| category | objects |
|---|---|
| I1 | the removed key, plus every key of each decided-present unit that refers to it |
| I2, I3, I4 | the key |
| G1 | the node |
| G2, MC of relation | the edge's two ends (and its edge id, if any) |
| G3 | the member, the decided holder and the merged holder. A holder of "none" is omitted |
| G4 | the key of the text unit |
| C | the node |
| D | the key the style unit is keyed by: the node for `class`, `:::` and `style`; the class name for a `classDef` |
| S-LINKSTYLE | the two ends of one edge whose `linkStyle` differs; one record per such edge |
| S-ORDER | the two nodes whose relative order differs; one record per pair |
| E, G0 | `["path"]` |

## Readings F chose where §5 leaves room

Each reading below decides at least one expectation. H and X may read the
rule differently. If so, V5 should surface the difference, and it should be
logged rather than forced.

1. **I3 implies I1.** §4.2 says a unit keyed by `k` refers to `k`. In a
   delete/modify case, the unit the other leg changed is decided present and
   keyed by a key decided absent. So the §5.2 dangling rule also holds, and
   every I3 fixture lists both I1 and I3 with objects `[k]`. Under §10.4,
   confusing I1 with I3 voids nothing.
2. **S-ORDER is read pairwise.** Order is not a unit in §4.2. F decides
   order per pair of items, with §5.1's rule applied to each pair's relative
   order. The items are nodes in R's vertex map, and edges in R's edge list
   whose key has count 1. Only items decided present, and present in the
   merged model, are compared. S-ORDER fires when a decided relative order is
   inverted in the merge. Under this reading, two legs that each add
   statements do not make an S-ORDER by themselves. The three S-ORDER
   fixtures would also fire under a whole-sequence reading.
3. **No repeat reports for a key whose existence or kind is wrong.** When a
   key's existence (I1, I3 or G1) or its kind (I4) is already the record,
   that key's label, shape and style units are not reported again as G4, C
   or D.
4. **Lint objects.** L1, L2 and L3 fail on a node id, and L4 on an id. L5
   fails on an edge, and its objects are taken to be the edge's two ends. So
   a duplicated edge statement makes its G2 tier B.
5. **No ineligible MC occurs in these fixtures.** Every model conflict here
   is either a §5.2 refusal case or an eligible MC. Ineligible MCs are
   therefore never needed as records.

## Behaviour of Mermaid that the expectations rely on

All of these are taken from Appendix A or from Mermaid's flowchart
documentation:

- a node declared twice keeps its last label and last shape;
- a later `click` for the same node replaces the earlier one;
- `style id …` creates the vertex if it does not exist;
- `class id c` and `click id …` on an id with no vertex do nothing;
- membership goes to the first subgraph to close, and an inner subgraph
  closes before its outer one;
- `subgraph Word` with a single word is an explicit id. Only a header of two
  or more words, or a quoted header, is keyed by title. The title-keyed
  fixtures use titles of two or more words;
- `linkStyle n` with `n` past the last edge throws a `TypeError` with no
  `hash`, so the text does not parse (§4.4).

## Coverage of §10.4

| category | V-fixtures |
|---|---|
| I1 | `i1-f-bare-rename` (A), `i1-d-bare-delete` (A), `i1-f-declared-rename` (B), `i1-d-subgraph-rename` (B); also in each I3 fixture |
| I2 | `i2-f-bare-class` (A), `i2-d-bare-style` (A), `i2-f-labels` (B); also `i4-d-node-vs-subgraph`, `i4-f-subgraph-vs-node` |
| I3 | `i3-f-bare-label`, `i3-d-bare-style`, `i3-f-declared-relabel` (all A) |
| I4 | `i4-f-move-vs-wrap`, `i4-d-node-vs-subgraph`, `i4-f-subgraph-vs-node` (all B, through L4) |
| G0 | `g0-d-both-move`, `g0-d-move-and-edit`, `g0-d-tilde` |
| G1 | `g1-f-bare-two-mentions`, `g1-d-bare-two-mentions`, `g1-f-bare-revive` |
| G2 | `g2-f-move-delete` (extra), `g2-d-dedupe-both` (lost), `g2-f-both-add-dup` (extra, B), `g1-f-bare-revive` (extra) |
| G3 | `g3-f-move-mention`, `g3-d-move-mention`, `g3-f-two-mentions-none` |
| G4 | `g4-f-click` (A), `g4-d-click` (A), `g4-d-relabel-redeclare` (B) |
| MC | `mc-f-chain-restate`, `mc-d-chain-restate`, `mc-f-dup-three` (all relation, group G2, A) |
| C | `c-f-restate`, `c-d-both-move-shape`, `c-f-hexagon` |
| D | `d-f-style-revive`, `d-d-classdef-revive`, `d-f-class-revive` |
| S-LINKSTYLE | `sl-f-both-insert`, `sl-d-both-delete`, `sl-f-comma-list` |
| S-ORDER | `so-f-first-mention`, `so-d-first-mention`, `so-f-cache-shortcut` |
| B (tier) | `i1-f-declared-rename`, `i1-d-subgraph-rename`, `i2-f-labels`, the three I4s, the three G0s, `g2-f-both-add-dup`, `g4-d-relabel-redeclare` |
| E | `e-f-same-line-relabel`, `e-d-prose-conflict` (conflict in prose only), `e-f-linkstyle-range` (does not parse) |
| exposed, git refuses | `x-f-rename-adjacent`, `x-d-collision-same-spot`, `x-f-delete-modify` |
| clean | `clean-f-retitle-member`, `clean-d-rename-explicit-member`, `clean-f-unwrap-member`, `clean-d-independent` |

Every category has at least one fixture in each stratum, except G0. G0 is in
stratum D only. In stratum F, a merged file can stop being a flowchart only
if its header line changes, and two legs changing the header conflict. F
found no clean stratum-F merge that produces a G0.
