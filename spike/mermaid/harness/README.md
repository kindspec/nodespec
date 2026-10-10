<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# The harness for `spike/mermaid/PRE-REGISTRATION.md` (role H)

The pre-registration is binding (approved 2026-10-09, merged as `4e56f28`).
This directory is H in its §10.1 sense: the harness parser, the oracle, the
arms, the R wrapper's driver and the aggregator. It does not hold X (the blind
second extractor) or any of F's fixtures, and nothing here reads either.

**Status: not validated.** No arm has run and no corpus has been opened. The V
steps that can run before X and F exist have run on this harness; their
transcripts are in `../results/validation/` (pre-review runs, re-run at the
validation commit as §11.2 requires).

## Threat model

The harness protects the pre-registration against **honest mistakes by its
one operator**, the owner: running an arm twice, running it from a stale or
edited checkout, forgetting to commit a transcript, mistyping or repeating an
option, publishing a private identity by accident. It checks those
mechanically and refuses. It does **not** defend against a deliberate
operator: whoever runs it can edit `ms/binding.py`, forge history, plant
modules or rewrite refs, and no check here would stop that. The guard against
that is the review step, `reverify.sh`, run in a fresh clone by a reviewer
who did not run the arms. (Owner direction, 2026-10-09.)

## Layout

| path | what |
|---|---|
| `mermaid_spike.py` | the CLI: `validation`, `arm0`, `arms` (M, P, S), `repro`, `sealed`, `aggregate`, `fixtures`, `export`, `archive` |
| `ms/hparse.py`, `ms/flowlex.py` | H: Mermaid 12.1.0's preprocessing, its generated flowchart lexer as a table, and its grammar by recursive descent |
| `ms/model.py`, `ms/subset.py` | Appendix A's model from R and from H; "in the subset" means H parses and the two models are equal |
| `ms/rbridge.py`, `../r/` | R: `rmodel.mjs`, mermaid 12.1.0 and jsdom 26.1.0 from `package-lock.json`, run offline under Node v24.20.0 |
| `ms/oracle.py` | §5: decided values, refusal cases, categories, tiers, Appendix C's lints, §5.5's exposure |
| `ms/fence.py` | §3's fences and flowchart test; §7.4's generated-file rules |
| `ms/gitops.py` | F2's hermetic `git merge` |
| `ms/case.py` | one case end to end; §8.3's P filter |
| `ms/history.py` | selection, authors, M-merge, M-PR (patch-id rules), P (predecessor rule) |
| `ms/replay.py`, `ms/sgen.py` | Appendix B.1's replay; B.2's generator and Arm 0's edit mix |
| `ms/arms.py` | Arm 0, M, P, S on one opened corpus; redaction |
| `ms/aggregate.py` | §9's verdicts, as a pure function of a summary |
| `ms/xrun.py` | runs X and compares it with H (§10.5) |
| `ms/blind.py` | the exports for F and X (§10.3), and Appendix E's prompts |
| `ms/binding.py`, `ms/transcript.py` | the validation commit, execution markers, transcripts (§11.1) |
| `ms/corpus.py` | the corpora table, the private mapping, bundles, PR lists, redaction scan |
| `v0.py`, `v3.py`, `v4.py` | V0, V3, V4 |
| `reverify.sh` | the review step, in a fresh clone |

Run everything as `python3 -I -S -B harness/<script>`. The CLI refuses
otherwise, refuses abbreviated and repeated options, and writes a transcript
for every invocation before parsing its arguments.

## Binding, as built (§11.1, §11.3)

- **The validation commit is derived**: the one commit that adds
  `results/VALIDATION`, which holds the sealed fixtures' hash and the
  lockfile's sha256. It must change no bound path; no later commit may. Bound
  paths: `harness/`, `r/` (tracked files), `x/`, `v-fixtures/`,
  `PRE-REGISTRATION.md`.
- **The first execution binds.** `arm0`, `arms` (M, P and S, §11.3's commit
  5), `sealed` and `aggregate` each write `results/executed/<arm>.json` when
  they open their first corpus or input, and refuse if that marker exists in
  the work tree or anywhere in history. A refused or mistyped run leaves its
  transcript and does not use the arm up.
- Before a bound run, nothing under `results/` may be uncommitted but its own
  transcript; the work tree must hold the validation commit's bytes at every
  bound path.
- A bound run takes every path from its fixed place. The owner's private files
  (`--private-map`, `--private-table`), the bundles (`--bundle-dir`) and the
  work directory (`--work-dir`) are arguments, outside the repository, never
  read from a committed path. Every `u:` label and `h:` pin is recomputed
  from them and must match `census/corpora-public.tsv`, whose sha256 is
  checked against §7.1.

## Redaction (§7.3; private individuals)

Committed outputs name corpora only by their public label. For a read-only
corpus, every record object (ids, labels, titles), every path segment and
every free-text reason is replaced by `h:` + 16 hex of its sha256. For an
individually owned corpus the same is done, and its commits are published as
`h:` + 16 hex of `sha256(salt + ":commit:" + sha)`. Authors are never
published for any corpus. V3 plants a read-only label, a private owner's name
and email, and an individual corpus's commits, scans the redacted output for
them (full or 7-character prefixes), and checks the same scan finds them in
the unredacted table.

## Readings

§5, §7 and §8 leave some details unsettled. Each reading below is what the
code does; each is to be checked in review. "Direction" says what the
reading does to a finding: **cannot hide** means it can only add records or
cases, never remove a finding; **narrows** means it can remove records, with
the reason it cannot remove a real defect.

| id | section | reading | reason | direction |
|---|---|---|---|---|
| R-delmod | §5.2 | "changes a unit keyed by it" is an add or a change on the other leg: that leg holds the unit with a value other than the base's. A removal on the other leg is not a change. | A removal agrees with the delete: the decided model drops the unit, so the decided model is consistent and the merge can be right about it. Counting it would call correct merges I3. `census/v4/synth_oracle.py` reads it the same way. | narrows I3; cannot remove a merge that is wrong about the decided model |
| R-ident | §5.3 | Only G1 is excluded for a key that is an identity record's subject ("G1 … outside I1–I4"). G2, G3, G4, C, D and MC records on the same units stand. | The letter excludes G1 only. A hole-#2 case can therefore carry structure records too (bare style: I1 and a G4 on the ghost's label). | cannot hide |
| R-subgraph | §5.3 | A subgraph present or absent against its decided value has no record of its own; it shows as G4 on its title and G3 on its members. | G1 is "Node". A subgraph's title unit always exists with it. | cannot hide (the title unit carries it) |
| R-edge-id | §5.3 | A user-id edge present or absent against its decided value is G2 (lost or extra); a changed end of one is G2. | §4.1 keys such an edge by its id; G2 is "an edge key's count". | cannot hide |
| R-marker | §5.3 | "Holds a conflict marker": a line opening with seven `<`, `>` or `|` that no input already holds. `=======` alone is not a marker. | git writes `<<<<<<<` and `>>>>>>>` with every conflict (and `ls-files -u` is checked too); Markdown's setext headings use `=======`. | narrows E: more cases are judged; E is never a finding |
| R-G0 | §5.3, §7.5 | E is checked first, then G0 (fence count or flowchart test of the merged file), then R's parse. A G0 case is not decided. | §7.5: decided needs E or a merged state in the subset; a G0 merged state is not. G0 is tier B regardless. | cannot hide a FOUND; pushes toward NO VERDICT |
| R-L3 | App. C | "Mentioned inside two different subgraph blocks": mentioned directly (in that block's own statements) in two blocks. | A member of a nested block is not mentioned in the outer block. | narrows lints, so fewer demotions: cannot hide |
| R-L5 | App. C | A duplicate edge's failing object is the edge key, not its ends. | The guidance is to prefer the reading that cannot hide a finding. With this reading L5 never demotes a G2 record (whose objects are ends). **Flagged:** this makes L5 inert for tier B; the other reading (ends) would demote G2 records on duplicated edges. | cannot hide |
| R-L4 | App. C | "An id used as two kinds" includes a node statement Mermaid dropped because an edge already has that id. | The source uses the id as both. | widens lints; only affects I4-adjacent records |
| R-fence | §3 | A closing line holds only the run (no indentation or trailing space, a `\r` aside); an opener never closed runs to the end of the file; the body is the bytes between. | "the next line holding only a run". | neutral |
| R-flowchart | §3 | The first diagram line may have leading whitespace; front matter leads only when `---` is the first non-blank line. | Mermaid's detector allows both. | neutral |
| R-select | §3, §7.4 | A path's stratum test, the declaration rule and the sibling rule read its last version (the census's rule for F). A D path is selected when its last version holds a Mermaid fence that is a flowchart; each case's inputs are then held to the one-fence rule. | "Paths … holding exactly one fence" applied per input, not per path, so a path whose fence count changed over time is still examined. | cannot hide |
| R-undecodable | §8 | A case any of whose input or merged texts is not UTF-8 is excluded and counted (`undecodable`). | R takes text; blockspec LOG §15 rules the same. | narrows; counted, never silent |
| R-attributes | F2 | A corpus that commits `.gitattributes` is merged with every merge-relevant attribute unset in `$GIT_DIR/info/attributes`; the commits are not changed. | "no .gitattributes"; a built-in `merge=union` needs no config. | neutral |
| R-merge-order | F2 | O is checked out and T merged in: M-merge O = first parent; M-PR O = target leg, T = head; P and S O = leg O. | git's output depends on it only through conflict-marker order. | neutral |
| R-p-units | §8.3 | A record is a P record if any unit it lists differs between merged and truth; UNRELIABLE if any unit it lists is untouched by both legs and the truth differs from the decided value. | §8.3 speaks of "that unit". | neutral |
| R-k | §9.1 | `k` counts distinct case keys of exposed M-merge and M-PR cases with all three inputs in the subset, whatever their outcome. | §9.1 as written; P never counts. | neutral |
| R-units | §7.5 | Case key: sha256 of the three diagram texts, each UTF-8 and NUL-terminated. "Identical pairs of model diffs": the sorted (unit, base value, leg value) lists of O and of T. Floors take cases in (P rank, key) order under the caps. | Deterministic. | neutral |
| R-coverage | §8.1 | Coverage per stratum is in-subset distinct blobs at the pins over all distinct blobs at the pins, summed over corpora. | "A stratum with fewer than 90% of its distinct blobs". | neutral |
| R-x | §10.5 | X's output is read as expect.json's shape: `exposed` and `records` of `{category, objects}` (owner, 2026-10-09). Compared categories: I1–I4, G0–G4, MC, C, D, S-LINKSTYLE, S-ORDER. Case outcomes (E, OUT-OF-SUBSET, DUP-TITLE) are not records; H's ineligible MC is reported only. | §10.5 compares (category, objects). | neutral; a mismatch is a disagreement, never an agreement |
| R-sealed | §10.4 | A sealed fixture's group is identity if F's expected records include an I category, else structure. Its A and B lines are read from F's `tiers`; H's and X's from whether they report a record of that group at tier A, or at tier B. | §10.4 states the lines, not the encoding. | neutral |
| R-s | §8.4, B.2 | S's bases are every version of every selected path. B.2's operations have the forms written in `ms/sgen.py`; an op that does not apply is redrawn up to 20 times, then the pair is a generator failure, counted. Arm 0's mix classifies a node removed and added with one label as a rename, and an edge removed and added sharing one end as a retarget. | B.2 names operations, not text. | S never yields FOUND |
| R-redact | §7.3, header | Commits of an individually owned corpus are `h:` + sha256(salt:commit:sha); its paths and record content are hashed like a read-only corpus's; authors are never published. | §7.1 gives the pin rule only. | neutral |
| R-arms | §11.1 | "Each arm" binds as one invocation: `arm0`; `arms` (M, P and S together, §11.3's commit 5); `sealed`; `aggregate`. | §11.3 lands M, P and S in one commit. | neutral |

## What is not built here

- The **archive** (§7.6) has a command (`archive`), tested only on its pull
  request pagination. It has not fetched any corpus. Where the bundles live is
  the owner's call; `harness/bundles.json` (each bundle's and list's sha256,
  committed at validation) does not exist yet, so a bound `arm0` today makes
  every corpus NO VERDICT and exits 3.
- **V1, V2 and V5** need F's V-fixtures and X. V1's refusal half and the H/R
  fuzz run inside V3. `fixtures --dir v-fixtures --extractor x/extract2.py`
  runs H and X over F's fixtures for V1, V3's "each category fires" and V5.
