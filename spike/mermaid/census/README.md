<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Census for the Mermaid pre-registration

The scripts behind every corpus figure in `../PRE-REGISTRATION.md`, the command
behind each figure, and every read of corpus content. No merge was run on any
corpus, and no merge result of a corpus was read.

**Layout.** The scripts ran from a working directory that also held the clones
(`../clones/`, `../md-clones/`) and the raw outputs. They keep their relative
paths here (`v2/`, `v3/`, `v4/`, `v41/`), and the commands below are written
from that directory. The data and outputs the pre-registration cites are at the
top level here; in the working directory they were:

| here | there |
|---|---|
| `corpora-public.tsv` | `v4/corpora-public.tsv` |
| `subgraph-forms-public.tsv` | `v3/subgraph-forms-public.tsv` |
| `v0-probes.out` | `v3/v0-probes.out` |
| `v4-error-texts.out` | `v4/v4-error-texts.out` |
| `synth-results.out`, `synth-results-v3rule-control.out`, `synth-results-v40rule-control.out` | `v4/` |

The raw per-corpus outputs, and every file that names an individually owned
corpus, are not committed.

## 1. Scripts, commands and figures

All repositories were cloned on 2026-10-07/08 as blobless bare clones
(`git clone --bare --filter=blob:none`). Pins are `git rev-parse HEAD` in
those clones. In `corpora-public.tsv`, an individually owned corpus is named
`u:` plus 12 hex digits of `sha256(salt + ":" + owner/name)`, and its pin is
`h:` plus 16 hex digits of `sha256(salt + ":pin:" + pin)`.

### 1.1 Finding candidates (stratum F)

    gh search code "<q>" --extension <mmd|mermaid> --limit 100|300 \
       --json repository,path

- 2,226 distinct (repo, path) pairs in 1,643 repositories.
- `path_commits.py`: commits per path, capped at 3. 388 repositories had a
  path with two or more commits.
- Forks and repositories with no licence were not cloned (82 + 63 with no
  licence). 242 were counted.

### 1.2 Per-corpus counts (stratum F)

    python3 -I v4/mmd_counts_v4.py <bare-repo> <owner/name>

NUL-safe (`core.quotepath=off`, `-z`, `--no-abbrev`). A failed lazy blob fetch
is fatal. It applies §7.4's rules, including the sibling rule: a same-stem
`.dot` or `.json` that is added or modified in at least half of the commits
that add or modify the flowchart.

- **Earlier versions.** `mmd_counts.py` (v1) treated a failed lazy fetch as
  "not a flowchart", which undercounted two corpora, among them
  `seqeralabs/nf-metro` (0 → 1 evaluable merge). `v2/mmd_counts_v2.py` made
  the failure fatal and added the sibling rule. `v3/mmd_counts_v3.py` added
  co-change. `v4/mmd_counts_v4.py` counts only add and modify commits for the
  sibling, not deletes. v4's output equals v3's on every listed corpus (`cmp` of
  the sorted files).
- **The co-change evidence.** `v4/sib_am.py` lists every `.mmd` path with a
  same-stem `.dot` or `.json` sibling in the cloned corpora. Counting add and
  modify commits only, 850 of 866 such paths co-change in at least half of the
  path's commits and 16 do not; counting every commit, 856 and 10. The listing
  names individually owned corpora and is not committed.

### 1.3 Inclusion and licences

    python3 -I v4/build_corpora_v4.py <private-dir>
    sha256sum v4/corpora-public.tsv
    # 2bc5e099c71f231cd5c4c9e3430038660af616e13182082f1e63cfdc9caaf22f

`build_corpora_v4.py` holds no repository names. It reads the classified
`NOASSERTION` licences and the salt from private files, and writes rows in a
fixed order. 19 `NOASSERTION` licences were classified from the first two
non-empty lines of each licence file. Out, with the reason: PolyForm
Noncommercial (3), CC BY-NC-ND (1), Commons Clause (1), evaluation-only (1),
the Open BSV License (1, `bsv-blockchain/teranode`), all rights reserved (4).
Owner types come from `gh api repos/<r> --jq .owner.type`.

### 1.4 Stratum D

Ten large multi-author projects, named before their counts were taken.
`md_counts.py` is path-level: it sees only paths holding a flowchart fence at
the pin, and a version need not change the fence. The census scripts match
the flowchart keyword case-insensitively; Mermaid does not (pre-registration §3).

### 1.5 The real concurrent cases' inputs

    python3 -I v4/fence_cases.py <bare> <owner/name> <checkout> [prs]   # D
    python3 -I v4/f_cases.py <bare> <owner/name>                       # F
    ./v3/run-v3.sh <mpr|unmerged> <stratum> <owner/name>               # v3/d_cases_v3.py

- **D merges:** 144 path-level evaluable; 9 with one flowchart fence in every
  input; 0 of the 9 with the fence changed on both legs; 4 of the 9 in
  generated `docs/` copies.
- **F merges:** 13 cases read, all changing the diagram on both legs; 9 are
  one derived path in `u:c4084f1c59f9`. The 5 remaining after the sibling rule:
  `Cogni-AI-OU/cogni-ai-agents` (2), `CGIC-AI/psfn-framework` (1, read only),
  `u:954608073c97` (1), `seqeralabs/nf-metro` (1, inputs not read).
- **Merged pull requests** (`./v41/run-v41.sh mpr <stratum> <owner/name>`,
  running `v41/d_cases_v41.py`; 31 F corpora with ten or more commits, all 10
  D corpora). The commit list is read across every page; a pull request with
  more than 250 commits is excluded. 433 merged single-parent pull requests
  touching a flowchart path; 128 matched as rebase (one-commit pull requests
  match both rules and are counted here), 291 as squash, 14 excluded (13
  matching neither rule, 1 over 250 commits). 7 evaluable path cases, all in D,
  one in a read-only corpus; **0 with one fence in every input**. In F, 0
  evaluable. 0 API calls failed. The earlier single-page run
  (`v3/d_cases_v3.py`) saw 428 pull requests, with 7 API failures, and the
  same 7 evaluable cases (`diff` of the sorted case lines is empty).

### 1.6 Never-merged concurrent legs

    ./v2/run-unmerged.sh prs   <stratum> <owner/name>   # all 127 v1-listed corpora
    ./v2/run-unmerged.sh forks <stratum> <owner/name>   # 27 corpora with ≥10 forks
    ./v3/run-v3.sh unmerged md <owner/name>             # one-fence filter, D

- **F, closed-unmerged pull requests:** 1,314 candidates, 205 closed unmerged,
  145 both-sides paths (139 add/add, from one individually owned corpus's bot
  pull requests), **0 evaluable**.
- **D, closed-unmerged pull requests:** 621 candidates, 161 closed unmerged, 90
  both-sides paths, 51 evaluable. **The one-fence filter:** 6 of the 51 hold
  exactly one flowchart fence in every input, **5 in
  `open-telemetry/opentelemetry-specification` and 1 in `apache/airflow`**, and
  in none does the fence change on both legs. **9 API calls failed** after
  retries in this run and are counted, not dropped (v2's count of 162 closed
  unmerged differs from 161 by one such failure).
- **Forks:** 27 corpora; 1,539 forks listed, 1,512 fetched, 205 with commits of
  their own, 1 touching a flowchart path, **0 evaluable**. The three result
  files hold 17, 7 and 3 rows, one per corpus, none repeated
  (`cut -f2 v2/unmerged-forks-*.tsv | sort | uniq -d` prints nothing).
- For `apache/airflow`, `backstage/backstage` and `grafana/grafana` the
  candidate search maps each touching commit to one pull request
  (`git log --source`), a lower bound; on `mermaid-js/mermaid` it found 15 of
  the exact method's 16 evaluable pull requests.

### 1.7 Subgraph forms

    python3 -I v3/subgraph_forms.py <mmd|md> <repo-or-checkout> <owner/name> <paths>

Over the flowchart files at the pin of 122 listed corpora (the 123rd, listed
from v3 on, has one path and is not included):

- F: 1,229 blobs; 998 with a subgraph; **35 with a subgraph without an explicit
  id**; 2 of those repeat a title; 3,402 headers, 149 without an id; 15
  corpora.
- D: 75 files; 25 with a subgraph; **8 with a subgraph without an explicit
  id**; 1 repeats a title; 184 headers, 29 without an id; 5 corpora.

### 1.8 The publishable-file checks

- **Names.** Every committed file was checked against the 345 corpus names
  whose owners are not known organisations, matching the full name or the
  owner part. All clean; the same check finds 16 names in the superseded
  `build_corpora.py`. The only hits in the pre-registration and this README
  are a common word equal to an owner's name (`solid`) and two organisation-owned corpora
  absent from the owner table (`Effect-TS/tsgo`, `bsv-blockchain/teranode`).
- **Commit shas.** Every committed file, the pre-registration and this
  README included, was scanned for hex tokens of 7 to 40 characters, each tested as a prefix of any
  of the 63,937 commits in the 71 individually owned corpora (`git rev-list
  --all` in each clone). All clean. The same scan of v3's
  `corpora-public.tsv`, which carried real pins, finds 71.

### 1.9 R and the synthetic checks

    node v4/rwrap/rmodel.mjs < text      # Node v24.20.0, mermaid 12.1.0, jsdom 26.1.0
    python3 -I v4/synth_oracle.py v4/cases [case …]

`rmodel.mjs` is the pre-registration's §4.4 wrapper: jsdom globals before
import, no `suppressErrors`, `hash` means "does not parse", any other error re-parses the
canary `A[Alpha] --> B` and aborts if the canary fails. `synth_oracle.py`
merges each synthetic case with stock git in a fresh repository, builds the
model from R as Appendix A says, and applies §5's rules. Only synthetic texts
were run through R.

- `v4-error-texts.out`: `linkStyle` out of range, unknown shape, `Flowchart`
  and `GRAPH` headers, and 600 edges under a limit of 500 each throw without
  `hash`, and the canary parses, so each text does not parse. Without jsdom, a
  labelled chart throws and so does the canary: exit 3.
- `synth-results.out`, under §4.2's rule (a holder is not a reference; a
  membership is undecided, not a model conflict, when any of its holder values
  is decided absent; MC eligible only when the merged value is neither leg's):
  `retitle`, `wordToTitle`, `renameExplicit`, `unwrap`, `retitleMemberMention`,
  `moveRetitleBoth`, `moveRenameBothExplicit`, `moveBetweenRetitled`,
  `moveIntoRetitled`, `moveIntoRetitledExplicit` clean with no record;
  `deleteBox`, `retitleBoth`, `hole2` E; `dupAdd` DUP-TITLE; `posRef` G2;
  `renameExplicitRef` I1 on `fe`, tier B by a new L1.
- `synth-results-v3rule-control.out` (`OLD_RULE=1`, a holder is a reference):
  a false I1, tier A, and a G3 on each of `retitle`, `renameExplicit`, `unwrap`
  and `wordToTitle`.
- `synth-results-v40rule-control.out` (`V40=1`, without the holder-values
  clause): a false eligible MC, G3, tier A, on `moveRetitleBoth` (legs
  `title:Back Layer` and `title:Front End`, merged `title:Frontend Layer`) and
  `moveRenameBothExplicit` (legs `api` and `fe`, merged `ui`).

## 2. Content reads, disclosed

Nothing from a corpus was printed except where stated.

- **Diagram-type keyword**, per `.mmd`/`.mermaid` path: the last version's blob;
  only whether it is a flowchart was kept.
- **Printed once:** the first line of one `Effect-TS/tsgo` baseline.
- **Fence scan**, stratum D, at the pin: paths and fence counts kept.
- **Generated-marker check**, `mermaid-js/mermaid` only: first ten lines of its
  18 flowchart `.md` files.
- **Licence files** of 19 `NOASSERTION` repositories: first two non-empty lines.
- **Directory listing** of `docs/deps/` in `u:c4084f1c59f9` (tree only).
- **The inputs of real concurrent cases:**
  - every D both-sides merge (144), merged pull request (10 under the first
    rule, 7 under §8.2's) and closed-unmerged pull request (51 paths): base and
    both legs, for fence counts, the flowchart keyword, and whether each leg's
    fence hash differs from the base's. Hashes were not printed;
  - every F both-sides merge read (13): base and both legs, for whether each
    leg changes the diagram. Booleans only;
  - for merged pull requests (433): the diffs of the pull request's commits, of
    `c^..c`, and of its net change, to compute patch-ids. Only match booleans
    were kept.
- **Subgraph headers:** every flowchart blob at the pin of the listed corpora,
  to classify `subgraph` header lines. Counts only.
- **Header case** (`v41/mixed_case.py`): the first diagram line of every
  flowchart at the pin of the listed corpora. 0 of 1,230 F diagrams and 0 of
  520 fenced D diagrams have a mixed-case header. On a planted file with one
  `Flowchart TD` and one `flowchart TD` fence, the script prints `2 1`.
- No merge result of a corpus was read and no corpus merge was run. The
  pre-registration's header says these inputs have been seen.
