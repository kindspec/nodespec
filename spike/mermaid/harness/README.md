<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# The harness for `spike/mermaid/PRE-REGISTRATION.md` (role H)

The pre-registration is binding (approved 2026-10-09, merged as `4e56f28`).
This directory is H in its §10.1 sense: the harness parser, the oracle, the
arms, the R wrapper's driver and the aggregator. It does not hold X (the blind
second extractor) or any of F's fixtures, and nothing here reads either.

**Status: not validated.** No arm has run and no corpus has been opened. The V
steps that can run before X and F exist have run on this harness; their
transcripts are in `../results/validation/`. They are runs before
validation; §11.2 re-runs every V step at the validation commit.

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
| `v0.py`, `v2.py`, `v3.py`, `v4.py` | V0, V2 (over histories H builds), V3, V4 |
| `vfix.py` | V1, V3's V-fixture half and V5, once F's fixtures and X are committed |
| `validate.sh` | runs V0, V2, V3 and V4 into `results/validation/` |
| `reverify.sh` | the review step, in a fresh clone |

Run everything as `python3 -I -S -B harness/<script>`. The CLI refuses
otherwise, refuses abbreviated and repeated options, and writes a transcript
for every invocation before parsing its arguments.

## Binding, as built (§11.1, §11.3)

- **The validation commit is derived**: the one commit that adds
  `results/VALIDATION`, which holds the sealed fixtures' hash, the lockfile's
  sha256 and every bundle's and pull-request list's sha256. The sealed hash
  must equal the one LOG.md records (commit 2). The validation commit must
  change no bound path, and no later commit may. Bound
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
  work directory (`--work-dir`) are arguments. They must be outside the
  repository; the harness refuses otherwise and never reads them from a
  committed path. Every `u:` label and `h:` pin is recomputed
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

**The frozen text wins wherever it decides a question.** A reading below is
recorded only where the text is silent, or to show which words decide it.
Each is to be checked in review. "Effect" says what the reading does to
records and cases. It is a description, not a reason: the reason column
carries the reason.

| id | section | reading | reason | effect |
|---|---|---|---|---|
| R-L5 | App. C, §5.3, §5.4 | A duplicate edge's failing objects are its two ends, and its id when it has one. | §5.3: G2's objects are "the edge's two ends and its edge id if any"; §5.4: a record is tier B if "one of whose objects newly fails a lint". The text decides it. (The earlier reading, the edge key as the object, made L5 match nothing.) | a duplicate edge from both legs is G2 at tier B |
| R-delmod | §5.2 | "Changes a unit keyed by it": the other leg holds the unit with a value other than the base's (an add or a change). A removal there is not a change. | §5.2 introduces its refusal cases as "decided models [that] cannot be rendered correctly by any merge". When the other leg also removes the unit, the decided model drops it and is consistent. `census/v4/synth_oracle.py` reads it the same way. | fewer I3 records than the wider reading |
| R-ident | §5.3 | Only G1 is excluded for a key that is an identity record's subject. G2 (a user-id edge included), G3, G4, C, D and MC records on the same units stand. | §5.3: "G1 Node … outside I1–I4"; no other category carries the clause. The text decides it. | a hole-#2 case can also carry structure records |
| R-subgraph | §5.3 | A subgraph present or absent against its decided value has no record of its own. It shows as G4 on its title and G3 on its members. | G1 is "Node"; no category names a subgraph's existence. | none lost: the title unit always exists with it |
| R-edge-id | §4.1, §5.3 | A user-id edge present or absent against its decided value is G2 (lost or extra); a changed end of one is G2. | §4.1 keys such an edge by its id; G2 is "an edge key's count". | — |
| R-marker | §5.3 | "Holds a conflict marker": a line opening with seven `<`, `>` or `|` that no input already holds. `=======` alone is not one. | The text does not define the marker. git writes `<<<<<<<` and `>>>>>>>` with every conflict (and `ls-files -u` is checked as well); Markdown's setext headings use `=======`. | fewer E outcomes than counting `=======` |
| R-G0 | §5.3, §7.5 | E is checked first, then G0, then R's parse. A G0 case is not decided. | §7.5: decided needs "E or a merged state in the subset"; a G0 merged state is not. | G0 adds nothing to the floor; it is tier B anyway |
| R-L3 | App. C | "Mentioned inside two different subgraph blocks": mentioned in the block's own statements, in two blocks. | Otherwise every member of a nested block would be inside two blocks and fail L3. | — |
| R-L4 | App. C | "An id used as two kinds" includes a node statement Mermaid dropped because an edge already has that id. | The source uses the id as both kinds. | — |
| R-fence | §3 | A closing line holds only the run (a `\r` aside); an opener never closed runs to the end of the file; the body is the bytes between. | "the next line holding only a run of the same character". | — |
| R-flowchart | §3 | The first diagram line may have leading whitespace; front matter leads only when `---` is the first non-blank line. | Mermaid's detector allows both; the text names the line, not its indentation. | — |
| R-select | §3, §7.4 | The stratum test (F: a flowchart; D: exactly one Mermaid fence, a flowchart), the declaration rule and the sibling rule read the path's last version. | §3 decides the test itself. It is silent on which version; the census read the last. | — |
| R-undecodable | §8 | A case any of whose input or merged texts is not UTF-8 is excluded and counted (`undecodable`). | R takes text. blockspec LOG §15 rules the same. | counted, never silent |
| R-attributes | F2 | A corpus that commits `.gitattributes` is merged with every merge-relevant attribute unset in `$GIT_DIR/info/attributes`; the commits are not changed. | "no .gitattributes"; a built-in `merge=union` needs no configuration. | — |
| R-merge-order | F2 | O is checked out and T merged in: M-merge O = first parent; M-PR O = target leg, T = head; P and S O = leg O. | Not stated. git's output depends on it only through conflict-marker order. | — |
| R-p-units | §8.3 | A record is a P record if any unit it lists differs between merged and truth. It is UNRELIABLE if any unit it lists is untouched by all three of B, O and T and the truth differs from the decided value. | §8.3 says "that unit"; "neither leg touched" means equal in B, O and T. | — |
| R-x-filter | §8.3, §10.5, App. D | X is compared with H's records before P's truth filter; the filter is then applied to H's P records. | Appendix D gives X no truth, so X can only report the unfiltered set. | — |
| R-k | §9.1, §7.5 | `k` counts exposed M-merge and M-PR cases with all three inputs in the subset, whatever their outcome: one per key and one per pair of model diffs. | §9.1 counts "distinct exposed M cases"; §7.5 makes identical pairs of model diffs one case. | — |
| R-units | §7.5, §8.3 | Case key: sha256 of the three diagram texts, each UTF-8 and NUL-terminated. Model diffs: the sorted (unit, base value, leg value) lists of O and of T. Each P (path, i) first picks its (1,1) case if decided, else (1,3), else (3,1); deduplication and caps then apply, in key order. | §8.3: "a (path, i) contributes its (1,1) case if decided, else …". | — |
| R-coverage | §8.1 | Coverage per stratum: in-subset distinct blobs at the pins over all distinct blobs at the pins, summed over corpora. | "A stratum with fewer than 90% of its distinct blobs in the subset". | — |
| R-x | §10.3, §10.5, App. D | X gets Appendix D's extractor contract only: its heading and its Extractor paragraph. X's output is read with the keys `exposed` and `records` of `{category, objects, tier}`. Once X delivers, the names X's output uses are mapped onto these and logged before validation (LOG §4). Compared: (category, objects) for I1–I4, G0–G4, MC, C, D, S-LINKSTYLE, S-ORDER, and exposure. Case outcomes are not records; H's ineligible MC is reported only. | §10.3 decides what X gets ("Appendix D's extractor contract"). §10.5 compares "(category, objects)" and exposure. The extractor contract names what X prints, not its JSON keys. | a mismatch is a disagreement, never an agreement |
| R-tiers | §10.4, App. D | **Provisional** (LOG §3). Today the parser reads `tiers` as a JSON list of §5.4's tier letters, "A" to "E", `[]` for a clean fixture; X's tier vocabulary is "A" to "E", "-" or "—". **Planned:** F never sees this encoding, since Appendix E's prompt is frozen. So once F delivers, and before validation, H rewrites the `tiers` parser to match the encoding F's visible V-fixtures use, and logs the result as a reading. The sealed run then checks the sealed tar against that parser. The parser is matched to F's format, not used to refuse it. | Appendix D names `tiers` but not its encoding. F's V-fixtures and sealed fixtures come from one author under one contract. | — |
| R-sealed | §10.4 | A sealed fixture's group is identity if F's records include an I category, else structure. Its `tiers` are per fixture and give that group's A and B lines; H's and X's lines say whether they report a record of that group at tier A, and at tier B. A fixture the `tiers` parser cannot read is logged as malformed in `sealed.json` and the verdict, gets no line, and does not stop the run. When X's answer is missing or holds a tier outside the vocabulary, X agrees with neither, and a fixture where H differs from F is **disputed**. | §10.4 defines VOID (X agrees with F) and disputed (X agrees with H), and runs the sealed fixtures through H and X without gating the run on them. LOG §3 step 4. | a broken X can block NOT FOUND, never void a group |
| R-v2 | §11.2 | V2 runs over histories H builds (`v2.py`). | F's prompt (Appendix E) is frozen and asks for no history, and Appendix D defines none (LOG §2). | — |
| R-bundles | §7.6, §11.3 | The bundles' and pull-request lists' sha256s are in `results/VALIDATION`, added by the validation commit. | §7.6: "committed at validation". `harness/` is bound, and the validation commit may not change a bound path. | — |
| R-sealed-hash | §10.4, §11.3 | The sealed hash is recorded in LOG.md in commit 2; VALIDATION repeats it, and the binding requires the two equal. | §11.3 lists it in commit 2; §10.4 says H commits it in the validation commit (LOG §2). | — |
| R-authors | §7.5 | Authors are built from every commit identity before any lookup. A leg's author is its last non-merge commit that changed the path, else its last non-merge commit. | §7.5: "the last commit on each leg that changed the path"; a merge commit has no author of the edit. | — |
| R-s | §8.4, B.2 | S's bases are every version of every selected path. B.2's operations have the forms in `ms/sgen.py`; an op that does not apply is redrawn up to 20 times, then the pair is a counted generator failure. S tier-A records are listed as blocked (F1). | B.2 names operations, not text; §6: "S never yields FOUND". | S never qualifies |
| R-redact | §7.3, header | Commits of an individually owned corpus are `h:` + sha256(salt:commit:sha); its paths and record content are hashed like a read-only corpus's; authors are never published. | §7.1 gives the pin rule only. | — |
| R-arms | §11.1 | "Each arm" binds as one invocation: `arm0`; `arms` (M, P and S together, §11.3's commit 5); `sealed`; `aggregate`. | §11.3 lands M, P and S in one commit. | — |

## What is not built here

- The **archive** (§7.6) is the `archive` command: fetch, bundle, and the
  merged pull-request list. Its failures never name the corpus, and its
  transcript and outputs live outside the repository. It has not fetched any
  corpus. The bundles are held by the owner (LOG §2). Their sha256s enter
  `results/VALIDATION` at the validation commit (R-bundles), so until then a
  bound `arm0` makes every corpus NO VERDICT and exits 3.
- **V1, V3's V-fixture half and V5** need F's V-fixtures and X:
  `vfix.py v1|v3|v5` runs them, and V4 runs `vfix.py v3` on every mutant
  once `v-fixtures/` holds fixtures. **V2** runs now, over histories H builds
  (R-v2).
