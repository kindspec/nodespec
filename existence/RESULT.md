<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# nodespec's existence: the result

**Verdict: met.** Three of the ten candidates meet every condition of
`CRITERION.md` §1: 08, 09 and 10. Each is an ordinary edit on each leg of a
Mermaid flowchart, which stock git merges with no conflict into a file
Mermaid 12.1.0 parses, and which the Mermaid spike's oracle finds wrong
about which nodes exist, with no lint failing newly on the merged file. With
the product need the owner has set, this meets the owner's bar for nodespec
(2026-10-18): product need plus a constructed silent-wrong case.

`results.jsonl` is `run.py`'s output, one line per candidate, run once each
from nodespec `7b169cb`, under Mermaid 12.1.0, Node v24.20.0 and git 2.47.3
(each line records them). Condition 1 is judged by review; the review of
nodespec#11 read 08 to 10 as one Appendix B.2 operation a leg.

## The three that meet it

Each starts from the same bare chart, `a --> b`, `b --> c`, `c --> d`,
`d --> e`, in which every node is written by its id alone.

| | ours | theirs | merged by git | what is wrong |
| --- | --- | --- | --- | --- |
| 08 | renames `b` to `x` | adds `b --> e` | `x` in both of ours' places, and `b --> e` | an edge names `b`, which ours renamed, and Mermaid makes a new node `b` that nobody added |
| 09 | deletes `c` and its two edges | adds `e --> c` | `a --> b`, `d --> e`, `e --> c` | `c`, which ours deleted, is back, with theirs' edge and none of its old ones |
| 10 | retargets `a --> b` to `a --> e` | deletes `e` and its edge | `a --> e`, `b --> c`, `c --> d` | `e`, which theirs deleted, is back as the target of ours' edge |

The oracle records each as I1, a dangling reference that merged clean
(`spike/mermaid/PRE-REGISTRATION.md` §5.3, the brief's hole #2), at tier A:
in a bare chart every node already fails lint L1 (a node with no node
statement of its own), so the node nobody meant looks like every other
node.

## The other seven

| | what each leg does | outcome | why it does not meet §1 |
| --- | --- | --- | --- |
| 01 | rename `api` / edge from `api` to a new node | I1 at tier B | the new node `api` has no node statement, and L1 flags it newly |
| 02 | delete `auth` / edge to `auth` | I1 at tier B | the same: `auth` comes back with no node statement |
| 03 | add `q[Queue]` / add `q[Quota]` | I2 at tier B | two labels for one node, which L2 flags |
| 04 | retarget to `auth` / rename `auth` | conflict | the edits are on adjacent lines |
| 05 | delete `worker` / restyle `worker` | conflict | the same |
| 06 | subgraph `cache` / node `cache` | I2 and I4 at tier B | one id as node and subgraph, which L4 flags |
| 07 | relabel `db` / rename `db` (the control) | conflict | both change the line that defines `db` |

01 to 07 are on a chart whose every node has a node statement with a
label, so an identity error there leaves a node with no statement, two
labels or two kinds, and a lint over the merged file sees it.
Four of the seven are still identity errors that git merged clean and
Mermaid accepted; they are visible, not silent. 01, 03 and 06 each add a
node inside an edge statement, which `CRITERION.md` §1.1 notes.

## What it shows, and what it does not

- **Named identity is where a silent wrong merge lives** in a flowchart. All
  three are one shape: one branch removes or renames a name and the other
  still uses it, and Mermaid, which creates a node for any name an edge
  uses, turns the stale use into a node nobody wrote. A format with named
  identity has to refuse that merge, or say it happened.
- **No frequency.** The Mermaid spike found real history rarely exposes
  this (`spike/mermaid/LOG.md` §15); constructed cases do not change that.
- **Not a design.** That nodespec refuses these merges, or merges them
  right, is for its specification to show, with 08 to 10 among its
  conformance cases.
- **What was seen first** is in `CRITERION.md` §4: the author's smoke test,
  and the review's own inputs, one of which had 08's shape and met
  conditions 2 to 5 before 08 was written.
