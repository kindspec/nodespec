<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Log: the Mermaid flowchart merge spike

The record §10.3 and §11.3 require: what each blind agent was given (export
manifest with each file's sha256, the prompt as sent, the model id and the
date), the shas of H, X and R at the validation commit, and every event that
bears on a verdict. Entries are appended, never edited.

## 2026-10-10 — §1. The harness, before validation

No arm has run and no corpus has been opened, merged or read. This entry
records a harness that is **not validated**: under §11.3 the harness at the
validation commit (commit 3) is the implementation.

- **Built:** `harness/` (H, the oracle, the arms, the aggregator, the X
  runner, the exports, the binding), `r/` (R, pinned by
  `package-lock.json`), `blind/` (what F and X are given),
  `harness/README.md` (threat model, binding, redaction, and the readings
  §5, §7 and §8 left open, each with its direction).
- **V steps run on this harness at `4153d09`**, transcripts in
  `results/validation/` (pre-review runs; §11.2 re-runs them at the
  validation commit):
  - V0: `V0: PASS` (`v0.txt`).
  - V3, its plant half, with V1's refusal half and an H/R fuzz check:
    `180 checks, 0 failed` (`v3.txt`).
  - V4: `89 mutants: 89 killed, 0 survived, 0 BROKEN` (`v4.txt`).
- **What V4 found before that.** The first sweep (90 mutants) left 14 alive,
  and the second 3. Each now has a check that goes red, except three that
  were equivalent and were replaced or removed (the third is named in a
  comment in `v4.py`):
  - the markdown-string refusal is enforced twice, in preprocessing and in
    the lexer table;
  - HOME is moot under GIT_CONFIG_GLOBAL=/dev/null;
  - setdefault versus assignment for the holder is a no-op, because
    Mermaid's makeUniq keeps each node in one subgraph's list.
  The redaction plant had silently produced no individual case. It now has a
  guard check.
- **Red-first for the verdict logic.** V3's verdict checks, run against a
  naive §9 aggregator, give `42 checks, 32 failed`
  (`results/validation/red-first-verdicts.txt`). The 10 that pass are
  checks a naive aggregator also meets, or ones that call the real
  `counted()` directly. The checks were written alongside the code, not
  before it. Per gate, the evidence is V4: every mutant is killed by a
  named check, and never by a crash.
- **Not yet runnable:** V1, V2 and V5, and V3's V-fixture half, need F's
  V-fixtures and X (`harness/vfix.py` runs them once those exist). The
  archive (§7.6) has not fetched any corpus; where bundles live is the
  owner's call.

### Open for the owner, before the validation commit

1. **Appendix D defines no layout for a fixture's history**, so V2 ("on
   every V-fixture with a history") has nothing to read unless F supplies
   one. `vfix.py v2` reads `history/v0.<ext>, v1.<ext>, ...` if present.
2. **Where the sealed hash is committed.** §10.4 says H commits it "in the
   validation commit"; §11.3 lists it in commit 2. The harness reads it from
   `results/VALIDATION` (commit 3) and puts nothing in commit 2's way.
3. **Bundle storage** (§7.6), and running `mermaid_spike.py archive` for
   each corpus, which fetches every corpus and its merged pull-request list
   over the network.
4. **R-L5** (README, Readings): the reading that cannot hide a finding makes
   lint L5 never demote a record. Confirm, or rule the other reading.

## 2026-10-10 — §2. Review of nodespec#3, and implementation readings

An independent review reproduced every V claim in §1, and found six HIGH,
two MEDIUM and six LOW items. Each is fixed in a new commit; nothing was
force-pushed, merged or run against a corpus.

**A correction to §1 and to the first README.** The guidance used for
§1's readings, "prefer the reading that cannot hide a finding", came from
the coordinator. It is not in the frozen text. The frozen text wins wherever
it decides a question; a reading applies only where the text is silent. On
that basis:

- R-L5 was a misreading and is reversed. §5.3 makes G2's objects "the
  edge's two ends and its edge id if any". §5.4 demotes a record "one of
  whose objects newly fails a lint". So L5 fails on those ends and id. Under
  §1's reading, a duplicate edge from both legs was a false tier-A G2.
- R-select is reversed: §3 decides "exactly one Mermaid fence".
- Every other reading was re-checked against the text and restated in the
  README with its words.

**What the review found, and the change for each.**

- **H1, L5.** Fixed as above. V3 now checks that the same edge added on both
  legs is G2 at tier B.
- **H2.** X is compared with H's records before P's truth filter. Appendix
  D gives X no truth, so X can only report the unfiltered set.
- **H3.** The tier-A disagreement check covers every decided real-arm case,
  including one over a cap or with a duplicate diff, not only the counted
  ones.
- **H4.** A bound `aggregate` refuses, listing the case keys, while any
  real-arm tier-A record has no reproduction result. It refuses before it
  marks itself executed.
- **H5.** The encoding of `tiers` and X's tier vocabulary are defined (README
  R-tiers). A malformed sealed tar is refused before the run marks itself
  executed. `vfix.py v3` checks the same lines on the V-fixtures.
- **H6.** `archive` captures every subprocess's output and scrubs the
  corpus's name and URL from failures. Its transcript must be outside the
  repository. Private files inside the repository are refused.
- **M1.** The review's 33 mutants are in V4's list, with V3 checks that kill
  them, plus one mutant per fix. V4 also runs `vfix.py v3` once V-fixtures
  exist.
- **M2.** See "X gets Appendix D whole" below.
- **LOW.**
  - `k` is deduplicated by pair of model diffs.
  - P picks each (path, i)'s case before deduplication.
  - G2 on a user-id edge is no longer suppressed (R-ident).
  - S tier-A records are listed as blocked (F1).
  - Authors are built from every commit before any lookup, and a merge
    commit is never a leg's author.
  - Where the bundles' hashes sit is R-bundles.

**V results after the fixes**, at `8b1e6ec`, transcripts in
`results/validation/`:

- V0: PASS.
- V2: PASS, over 60 histories H builds and 480 replays.
- V3: `228 checks, 0 failed`.
- V4: `138 mutants: 138 killed, 0 survived, 0 BROKEN`. This includes the
  review's 33 mutants, rewritten where the fixes changed the code they
  target, and one mutant per fix.

The review's own `mymut.py`, run unchanged (`review-mymut.txt`), gives 27
killed, 0 survived and 6 BROKEN. The 6 (R2, R6, R8, R9, R28, R33) are BROKEN
because the fixes rewrote the lines their patterns name. V4's rewritten
versions of all six are killed.

The review's probes, run unchanged, are in `review-probes.txt`:

- probe1's duplicate edge is now G2 at tier B.
- `aggprobe` cases 1 and 2 are now NO VERDICT on the tier-A disagreement.
  Its case 3 shows F8 blocking in the pure aggregator; the bound command
  now refuses before that point (H4).
- `archleak` still reports a match. The match is the probe's own source
  line, quoted in its own traceback. The harness's exception message is
  scrubbed (V3 `s_archive_leak`).

**Implementation readings, decided by the coordinator, not owner rows:**

- **X gets Appendix D whole.** §10.3 gives X "Appendix D's extractor
  contract". The export gives the whole of Appendix D: the fixture contract
  as well. This deviates from §10.3's letter. The reason: the fixture
  contract is a format only, and holds no answers. It fixes the shape of X's
  output (`exposed`, `records` of `{category, objects}`), which §10.5's
  comparison needs and the extractor paragraph does not give. The README
  said this was the owner's decision; it was the coordinator's.
- **Bundle storage.** Bundles are held by the owner, with a local copy
  outside the repository, following blockspec's precedent. No committed file
  names the private store. Their sha256s are bound in `results/VALIDATION`
  at the validation commit (R-bundles).
- **The sealed hash.** Commit 2 records it in this LOG, as a line
  `- sealed fixtures sha256: <64 hex>`. `results/VALIDATION` repeats it, and
  the binding refuses unless the two are equal (R-sealed-hash).
- **V2's histories.** F's prompt is frozen verbatim and asks for no history,
  so F is not asked for one. V2 runs over histories H builds (`v2.py`,
  R-v2).

## 2026-10-10 — §3. Plan: the `tiers` encoding follows F's V-fixtures

R-tiers (README) is provisional. Appendix D names `tiers` without an
encoding, and Appendix E's prompt to F is frozen, so F will not see the
encoding the harness reads today. A sealed tar must not be refused for
using a different but consistent encoding. So:

1. F delivers its V-fixtures (visible) and its sealed hash.
2. Before the validation commit, H reads the `tiers` encoding the
   V-fixtures use, rewrites the parser to match it, and logs that encoding
   here as a reading. The parser is a bound path, so this change lands
   before validation. V3 and V4 cover the new parser.
3. `vfix.py v3` checks every V-fixture's A and B lines under that parser.
4. The sealed run, at commit 6, checks the sealed tar against the same
   parser. A sealed fixture that fails it is a fact about F's fixtures, to
   be logged, and not a reason the harness chose after seeing them.

No code change is made yet; this entry is the plan the coordinator set on
2026-10-10.

## 2026-10-10 — §4. Second review of nodespec#3

A second independent review of nodespec#3 at `37e3ed5` reproduced two
HIGH defects. This entry records them and the change for each. It is
appended; §1 to §3 stand as written. §1's open-items subsection is restored
as it was first committed, since this log is append-only. Its four items are
settled in §2 and §3.

- **HIGH, P against X.** The tier-A disagreement check held X to H's
  P records after the truth filter. A P case whose only tier-A record the
  filter removes (a second `A --> B` on one leg, the first dropped in the
  truth) turned 60 agreeing M cases' NOT FOUND into NO VERDICT, even with an
  X that did everything right. X is now held to H's unfiltered set (§9.1,
  §10.5, R-x-filter); the case keeps both sets, and V3 checks this plant.
- **HIGH, privacy.** `archive` named bundle files from sha256 of the
  corpus's owner/name, unsalted, and R-bundles commits those names. A u:
  label could then be linked to its repository by hashing candidate names.
  The files are now named from the public label, and V3 checks a name cannot
  be computed from owner/name.
- **X's export.** §10.3 decides that X gets "Appendix D's extractor
  contract". `blind/x/SPEC.md` now holds Appendix D's heading and its
  Extractor paragraph only, not the Fixtures paragraph. This replaces §2's
  reading that X gets Appendix D whole. The extractor paragraph names what
  X prints but not its JSON keys. So, as §3 plans for F's `tiers`: once X
  delivers, and before validation, H maps the names X's output and
  CHOICES.md use onto the ones `ms/xrun.py` reads (`exposed`; `records` of
  `{category, objects, tier}`), logs the mapping here as a reading, and V5
  runs under it.
- **Sealed fixtures.** §10.4 runs the sealed fixtures through H and X. It
  does not gate the run on their format, and §3 step 4 says a fixture that
  fails the parser is logged. The sealed run therefore no longer refuses on
  a malformed fixture. It logs the fixture in `sealed.json`'s `malformed`
  list, which the verdict lists, gives it no line, and runs the rest. An X
  answer that is missing, or holds a tier outside the vocabulary, gives
  x = None: X then agrees with neither, and a fixture where H differs from
  F is read as disputed. `tiers` is per fixture. A fixture's A and B lines
  are those of its group, identity if F's records hold an I category,
  else structure (R-sealed).
- **Mutants the review showed surviving**, each now killed by a named V3
  check and in V4's list:
  - L5 on a duplicated user edge id;
  - the disagreement check in a stratum below the coverage bar;
  - a missing X answer;
  - archive's scrubbing, and private files anywhere in the repository;
  - authors from a merge commit, and from one ref only;
  - bundles read while the derivation reports a reason;
  - LOG.md recording the sealed hash twice;
  - a D path whose last version holds two fences.

  V4's copies are now git repositories, so "the repository" means the same
  thing in a copy as in the work tree.
- **Outputs.** `results/validation/review-probes.txt` and `review-mymut.txt`
  no longer carry absolute scratch paths or working-directory names.

## 2026-10-10 — §5. V steps after the second review

These are runs before validation, at `8a9b8e7`, with every bound path clean.
Transcripts are in `results/validation/`.

- V0: `V0: PASS`.
- V2: `60 histories, 480 replays, 0 failed`.
- V3: `244 checks, 0 failed`.
- V4: `153 mutants: 153 killed, 0 survived, 0 BROKEN`.

The first V4 run after §4, at `404ebb9`, killed 152 of 153 mutants. The
remaining one dropped Appendix D from X's section list, and was killed only
by a crash in the cut. The cut now takes Appendix D's extractor contract on
its own, and the mutant now drops Appendix C. That run's transcript is kept
as `v4-404ebb9-fail.txt`.

## 2026-10-10 — §6. §2 and §3 restated

This entry restates the decisions in §2 and §3 as the harness's readings.
It leaves §2 and §3 unchanged. Where this entry and §2 or §3 differ in
wording, this entry is the statement of record. Where §4 changed a decision,
§4 stands.

- **The text first.** Where the frozen text decides a question, it decides
  it. A harness reading applies only where the text is silent (README,
  Readings).
- **X's export.** The harness's reading was first that X gets Appendix D
  whole (§2). §4 replaced it: X gets Appendix D's extractor contract, as
  §10.3 decides, and X's output names are mapped after delivery.
- **Bundle storage.** The harness's reading is that bundles are held by the
  owner, with a local copy outside the repository. No committed file names
  the private store. Their sha256s are bound in `results/VALIDATION` at the
  validation commit (R-bundles).
- **The sealed hash.** The harness's reading is that commit 2 records it in
  this log as `- sealed fixtures sha256: <64 hex>`. `results/VALIDATION`
  repeats it, and the binding requires the two to be equal (R-sealed-hash).
- **V2's histories.** The harness's reading is that V2 runs over histories H
  builds, because F's prompt is frozen and asks for none (R-v2).
- **F's `tiers` encoding (§3).** The harness's reading is that, once F
  delivers and before validation, the `tiers` parser is matched to the
  encoding F's V-fixtures use. That encoding is logged here as a reading. The
  sealed run then checks against that parser, and logs any fixture that
  fails it (R-tiers, R-sealed).

## 2026-10-11 — §7. A sealed fixture that cannot be read

Under §4, a sealed fixture the `tiers` parser could not read got no line.
So §10.4's VOID and disputed rules never saw it. A planted case showed the
effect. A fixture F marks tier B, H marks A, and X agrees with F. Read
correctly, it voids the identity group. With `tiers` written `"B"`
instead of `["B"]`, it was logged and the identity FOUND stood clean. A
sealed run of only such fixtures exited 0 having checked nothing.

The harness's reading (README R-sealed) is now:

- An unreadable sealed fixture blocks its group, or both groups if its
  records do not parse either.
- In a blocked group, a non-FOUND verdict is NO VERDICT, and a FOUND is
  reported as found in a group with an unreadable sealed fixture, never as a
  clean FOUND.
- A sealed run that lines no fixture exits non-zero.

V3 checks:

- the parsed case: VOID, with the FOUND reported in a voided group;
- the malformed case: no line, a non-zero exit, and the FOUND reported in a
  blocked group;
- the all-malformed case;
- the block on both groups.

V4 has a mutant for each gate (SU1 to SU7). At `f0da993`:

- V3: `252 checks, 0 failed`.
- The eight new and repointed mutants: 8 killed, 0 survived, 0 BROKEN
  (`v4-sealed-mutants.txt`).

## 2026-10-11 — §8. The blind roles: what each was given

§11.3 commit 2. Each blind role ran with `harness/ms/roles.py`, through
`mermaid_spike.py role`. A run is one fresh `claude -p --model
claude-opus-5-5` session in a bubblewrap sandbox. The environment is
cleared. `/work` is the role's export (`mermaid_spike.py export`, a
`git archive` at `2364767` with no `.git`). The only other things visible
are system libraries, python3, the CLI binary, and the CLI's credential
file, read-only. Nothing else from `/home` is visible. The session has no
MCP server (`--strict-mcp-config`, empty) and built-in tools only (Read,
Write, Edit, Glob, Grep, Bash).

Before each session, the launcher plants a file outside `/work` and checks
that the sandbox can neither read it nor see the repository or
`~/.claude`; every probe held. It also checks the session's init event for
the model, the tools and the MCP servers. The network stays on, as §10.3
allows: the barrier there is honour-system.

The launch records are in `results/roles/` (paths scrubbed). The
launcher's transcripts are in `results/transcripts/`.

| run | date (UTC) | export manifest, sha256 | prompt, sha256 | model reported | session sha256 |
|---|---|---|---|---|---|
| X, 1 | 2026-10-11T04:25:09Z | SPEC.md `a18af470…`, mermaid-12.1.0-flowchart.md `50490edd…` | Appendix E's X prompt, `785fabf0…` | claude-opus-5-5 | `1aec348a…` |
| X, 2 | 2026-10-11T04:52:25Z | as run 1, plus X's own extract2.py and CHOICES.md | `results/roles/x2-prompt.txt`, `9df26071…` | claude-opus-5-5 | `a801bbff…` |
| X, 3 | 2026-10-11T05:25:57Z | as run 2, after X's run-2 edits | `results/roles/x3-prompt.txt`, `bc8e37db…` | claude-opus-5-5 | `04f316b5…` |
| F, 1 | 2026-10-11T04:25:09Z | PRE-REGISTRATION.md `6a6dec6a…`, mermaid-12.1.0-flowchart.md `50490edd…` | Appendix E's F prompt, `d5db5690…` | claude-opus-5-5 | `ad2c7e23…` |
| F, 2 | 2026-10-11T04:52:25Z | as F, 1 | Appendix E's F prompt, `d5db5690…` | claude-opus-5-5 | `b23652e0…` |

The full sha256s are in each launch record. X's three session streams are
committed in `results/roles/`, with absolute paths replaced by
placeholders, so their bytes differ from the hashes above. Those hashes
are of the streams as written. A smoke test of the launcher, with a
one-line prompt and not a role, is in `results/roles/smoke-test/`.

## 2026-10-11 — §9. F: run 1 is void, run 2 is used

- **Run 1 is void, for a mechanical reason.** F's final message names
  `sealed.tar` and `nonce.bin`. A search by file name alone found neither
  under F's work directory. No sealed content was read in that search or
  since. The session's `/tmp` and HOME were tmpfs, so F's tar and nonce
  were discarded when it ended. §10.4 requires the owner to hold them, and
  run 1 cannot meet that. Run 1 printed one sha256, `1eeedc17…`. Its work
  directory, session stream and launch record are kept, unread, in the
  owner's custody.
- **Run 2** is a fresh invocation. It used the same verbatim prompt, an
  export at the same commit, and `--scratch` inside the custody area, so
  its `/tmp` and HOME persist. Its tar and nonce were found, by file name
  only, under that scratch directory. Run 2's work, scratch and session
  stream are in the owner's custody, unread. Its V-fixtures (54 entries,
  copied byte for byte into `v-fixtures/`) and its sealed hash are the ones
  used.
- **The sealed hash** recorded for §11.3 commit 2 is run 2's:

- sealed fixtures sha256: a338d477972ff257d5288a7a8426bfb4ab8a325a8dad55eaa6c893fa97be189a

- **The harness's reading of what F's transcripts commit, and when.**
  F's session streams hold the sealed fixtures as F wrote them, so
  committing them before commit 6 would show the sealed fixtures to H and
  X. Both runs' streams, run 1's included, are committed at commit 6
  alongside the tar and the nonce. §11.1 requires every invocation's
  transcript to be committed, and §10.4 commits the sealed material at
  commit 6. Commit 2 records only the streams' sha256s (§8). F's launch
  records and the launcher's transcripts hold no session output, only what
  F was given, the barrier probe, the init check and the count of 64-hex
  tokens in F's final message. So they are committed now, as §11.1 asks of
  every invocation.

## 2026-10-11 — §10. Matching the harness to F's and X's output

These are the harness's readings, settled once F and X had delivered and
before validation (§3, §4).

- **R-tiers (§3).** F's V-fixtures write `tiers` as a list parallel to
  `records`: one tier per record, `A` to `E`, or `—` for a record reported
  only. A clean case has `[]` for both. The parser now reads exactly that,
  and each group a fixture's records belong to gets its own A and B lines.
  Under §3, the sealed run checks the sealed tar against this parser.
- **X's output names (§4).** X prints its exposure as
  `exposure.exposed`, and its records with `category`, `objects` and
  `tier` (X's CHOICES.md, entry 1). `ms/xrun.py` reads that shape. G0's
  object is the case's one path; X names it by the merged file's path on
  disk, and H reads that as `path`.
- **R-x-compare.** §5.3's "A record's objects" defines objects for I1–I4,
  G0 and G1–G4 only. So MC, C, D, S-LINKSTYLE and S-ORDER are compared by
  category alone.
- **R-order.** Order is not a unit in §4.2. Both F and X decide it pair by
  pair, and so now does H. Each pair of nodes, and each pair of edges in the
  edge list, is a unit. S-ORDER fires when a decided relative order is
  inverted in the merge, and is reported once per sequence.
- **MC outside §5.2.** §5.3's MC is "a model conflict outside §5.2". A
  conflict that is part of a refusal case is no longer also reported as an
  MC.
- **R-v3fix.** §11.2 V3's V-fixture half reads "each category fires on its
  V-fixtures and stays silent on clean ones":
  - each fixture's category, as F's coverage table names it by the
    directory name, fires in H;
  - each clean fixture gives no linable record;
  - H's A and B lines match F's tiers.

  `vfix.py v3` lists every other difference from F's expectation.
- **X invocations 2 and 3** (§10.1, prompts in `results/roles/`). Each
  prompt quotes the frozen text and does not describe H.
  - **Invocation 2** quoted §3's fence pattern (`mermaid(-example)?`),
    §5.3's G1-only "outside I1–I4" clause, and §5.3's E rule. X changed
    choices 5, 6 and 33. A bare `=======` is no longer a marker; X records
    the reason as Markdown's setext headings.
  - **Invocation 3** quoted §4.2's "decides each unit separately", §5.3's
    G3, G4 and C definitions, and §5.3's I4. X changed choices 32 and 31.
  - After invocation 3, V5 agrees on all 53 V-fixtures.
- **Differences from F's expectations that stand.** `vfix.py v3` lists
  them. Where §4.2 decides each unit separately, H reports G3, G4 and C on
  a key that also has a G1 or an I1–I4 record (F's reading 3 does not).
  Where §5.1 makes the deleted key's unit a model conflict, H gives no I1
  in `i3-f-bare-label` (F's reading 1 expects one). F's README says such
  differences are to be logged, not forced.

## 2026-10-11 — §11. Review of nodespec#5: X's independence, and corrections

Entries are appended, never edited, so this entry corrects §8 and §10
where they are wrong; it does not rewrite them.

### X's invocations 2 and 3 carried argument; invocation 4

- **Correction to §10.** §10 says the prompts of X's invocations 2 and 3
  quote the frozen text and do not describe H. They did not describe H,
  but they did not only quote either: each carried argument for a reading.
  - Invocation 2 said "Only G1 carries the clause". It also argued from
    setext headings that a bare `=======` is not a conflict marker.
  - Invocation 3 asked X to "Consider a node that is decided absent and
    present in the merged model", and set out the units that node has.

  X's revisions repeat that argument closely: see the "Revisions" section
  of `results/roles/x3-output/CHOICES.md`.
- **X changed readings after them.** In its first invocation, X read §5.3
  as reporting no more records on a key whose existence or kind is already
  wrong (X1's choices 32 and 33). F's V-fixtures read it the same way.
  After invocations 2 and 3, X took H's reading. So V5's 53 of 53 after
  invocation 3 did not check H independently, and V5 is the check §10.5
  exists for.
- **A deviation in invocation 2.** Invocation 2 quoted §3's definition of
  a Mermaid fence. That is frozen text outside X's §10.3 allotment, which
  is SPEC.md.
- **Invocations 2 and 3 are superseded, and kept.** Their prompts, session
  streams and launch records stay in `results/roles/`. Invocation 3's
  output is moved to `results/roles/x3-output/`.
- **Invocation 4 starts from X1's state.** Invocations 2 and 3 revised
  X's work directory in place. `harness/x1_recover.py` rebuilds X1's files
  from the record:
  - `extract2.py`: invocation 2 copied it to its `/tmp` after one Edit,
    and its scratch was kept. The script undoes that Edit. The result
    matches all 270 lines that invocation 2 read from the file before
    editing it. Invocation 4's own copy of the file it was given, kept in
    its scratch, is byte-identical.
  - `CHOICES.md`: replayed from invocation 1's Write and Edit calls. It
    matches invocation 2's first full Read of the file.

  X1's output is in `results/roles/x1-output/`: `extract2.py` sha256
  `a35dbe684451ae5945e3dc3841585424e3c44df5543a57bf5c0250b9af934529`,
  `CHOICES.md` `9abb46755c2bfe2ffa8314efdd18339a8b828018a3997f9e92beacc81a42a605`.
- **Invocation 4's prompt is fixed and neutral.** It holds a fixed opening
  paragraph, then one block per input. Each block gives the input files
  verbatim, then X1's output, then H's output. It holds no argument, no
  quote from the pre-registration and no section pointer.
  - `harness/x4_prompt.py` chooses the inputs: every V-fixture on which
    V5's comparison, run with X1's extractor, finds X1 and H apart. That
    is 13 of 53.
  - The fixture names are left out of the prompt, because they name F's
    expected category. `results/roles/x4-index.tsv` maps each input to its
    fixture.
- **What invocation 4 was given.** The run was launched as in §8, from an
  export of X at `2364767`:

  | run | date (UTC) | export manifest, sha256 | prompt, sha256 | model reported | session sha256 |
  |---|---|---|---|---|---|
  | X, 4 | 2026-10-11T12:15:03Z | SPEC.md `a18af470…`, mermaid-12.1.0-flowchart.md `50490edd…`, X1's extract2.py `a35dbe68…` and CHOICES.md `9abb4675…` | `results/roles/x4-prompt.txt`, `3e399b60…` | claude-opus-5-5 | `f1a25aff…` |

- **What X did in invocation 4** (its CHOICES.md, "Invocation 4"):
  - **Entry 41.** X now reports every unit on its own, which matches H.
    This replaces X1's choices 32 and 33.
  - **Entry 42.** S-ORDER's objects are now the keys of the inverted
    pairs. S-ORDER is compared by category only, so this changes no
    comparison.
  - **Entry 43.** X kept its I4 reading (choice 31).
- **V5 with invocation 4's extractor: 50 of 53 agree.** The three
  disagreements are all I4. In each, H reports I4 and X does not:

  | V-fixture | H only | X only |
  |---|---|---|
  | `i4-d-node-vs-subgraph` | I4 `billing` | — |
  | `i4-f-move-vs-wrap` | I4 `api` | G1 `api` |
  | `i4-f-subgraph-vs-node` | I4 `auth` | — |

  X's reason: it reads "or a kind other than its decided kind" as a second
  object of "no input gives".
  - In `i4-f-move-vs-wrap`, the base gives `api` a kind other than its
    decided kind, so I4 does not apply and the node's return is a G1.
  - In the other two, the kind is a model conflict, and X counts the
    clash once, as the I2 collision both report.

  Neither side is plainly a bug. This is a reading for the owner to rule
  on. H is unchanged, and X has not been invoked again.
- **What V5 cannot see.** Invocation 4's extractor keeps X1's choices 5
  and 6:
  - an opener of `mermaid-example`, or with `Mermaid` in upper case, is not
    a Mermaid fence;
  - a bare `=======` line is a conflict marker.

  H reads both the other way: §3's pattern for the fence, and R-marker for
  the marker. No V-fixture holds either case, so V5 cannot test them, and
  invocation 4's prompt could not raise them.

### Corrections and additions

- **How X1's disagreements were first found.** The three put to
  invocation 2 (choices 5, 6 and 33) were found by reading X1's final
  message, under "Choices most likely to disagree with the reference
  extractor", and its CHOICES.md. They were not found by V5, which was
  first run with X after invocation 2. The two put to invocation 3
  (choices 32 and 31) came from that V5 run.
- **Correction to §8.** §8 says X's committed session streams differ in
  bytes from the hashes it lists. They do not: no stream held a host path,
  so scrubbing left them unchanged. Each committed stream's sha256 equals
  its launch record's `session_sha256` (X runs 1 to 4).
- **F run 1's hash.** `results/roles/f-launch.json` records
  `sealed_sha256` `1eeedc17…`. That is void run 1's (§9), not the sealed
  hash. The record is kept as written.
- **R-v3fix's history (§10).** Before `f9708f4`, `vfix.py v3` passed a
  V-fixture only on an exact match: H's set of (category, objects) equal
  to `expect.json`'s records, and H's exposure equal to `exposed`.
  - The 12 V-fixtures that `vfix.py v3` lists as differing from F's
    expectation would have failed that criterion.
  - `f9708f4` changed the gate after F's run 2 had delivered its
    V-fixtures. The text it follows is §11.2's V3: "Each category fires on
    its V-fixtures and stays silent on clean ones."
  - V3 now plants a fixture against each of the gate's three tests, and
    V4 has a mutant for each.
- **G0 has no stratum-F V-fixture.** F's three G0 fixtures are all stratum
  D.
- **S-ORDER above the pair cap.** H decides every pair of a sequence up to
  400 items (`ORDER_CAP`). Above that, it decides only the adjacent pairs
  of each state's own sequence. X decides every pair of the merged
  sequence up to 1,500 items, and above that only the adjacent merged
  pairs. So H and X can differ on S-ORDER for a sequence of more than 400
  items. No V-fixture has one. S-ORDER is reported only (tier "—") and is
  compared by category alone, so it cannot move an A or B line.
- **The trailing "Blind roles" placeholder is removed.** Its "Not yet
  launched" stopped being true at §8, and §8 to §11 log each launch.

### Syntax census, taken before Arm 0

Before the owner rules on X's fence and `=======` readings, a census
asks whether either can touch the population. It is
`harness/syntax_census.py`, and its transcript is
`results/census/syntax-census.txt`.
- It reads trees and blobs of the archived corpora, at and before each
  pin, through §7.4's selection.
- It runs no arm, no merge and not R, and it reads no outcome.
- It prints totals only.
- It covers all 123 corpus rows. The population is 47 selected stratum-D
  paths (537 versions) and 1,671 stratum-F paths (5,003 versions).

- **(a) Fence openers that §3 accepts and X's opener does not.**
  - In the 537 versions of selected D paths:
    - `mermaid-example`: 1 fence, in 1 version;
    - a case variant of `mermaid`: 0;
    - counted apart, other text after `mermaid` on the opener line, which
      X's opener also refuses: 7 fences, in 7 versions.
  - Effect on the population: in 8 versions, of 3 selected paths in one
    corpus, the diagram differs under X's opener. Applied to selection, X's
    opener would drop those 3 paths, which §3 selects, and would add 6
    paths that §3 excludes.
  - At the pins, 180 `.md` blobs hold a §3 Mermaid fence. Of these, 90
    hold 1,153 `mermaid-example` fences, 2 hold 5 openers with other text
    after `mermaid`, and none holds a case variant. Almost all of these
    blobs are outside the population: they hold more than one fence.
- **(b) Lines that are exactly `=======`.** There are 0 such lines in any
  blob that holds a Mermaid fence, at the pins (180 blobs) or among the
  population's versions (298 blobs). That holds inside and outside fences,
  with or without a `<<<<<<<` line. No stratum-F version holds one either.
  To check that the pattern finds such lines at all, the same pattern was
  run over `.md` files at each mirror's HEAD (not the pins), outside the
  committed script: it found 8.

So the `=======` reading cannot change any case in the population. The
fence reading can, on at most 3 selected paths of one corpus (8 versions).
X's opener would also change which paths are selected. §3's pattern is
the frozen text and decides selection either way.

### Fence and `=======` readings, declared before Arm 0

- **Fences.** The syntax census found 3 selected stratum-D paths (8
  versions) where X's opener differs from §3's. §3 decides the fence:
  `^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b`, case-insensitively.
  H follows it. X differs only because §3 was not in its §10.3 allotment
  (SPEC.md). No ruling is needed, and neither X nor H changes. An X/H
  disagreement on those paths is a disagreement, handled by §10.5
  unchanged:
  - a FOUND candidate there becomes disputed;
  - a tier-A disagreement there blocks a structure NOT FOUND.

  Such a disagreement is reported with this cause: X's allotment.
- **`=======`.** The census found no `=======` line in any population blob
  that holds a Mermaid fence, so X's marker reading cannot change any case.

### The owner's ruling on I4 (2026-10-11)

On 2026-10-11 the owner ruled that I4 takes Reading H. The sentence at
issue is §5.3's:

> **I4 Kind clash.** A key that no input gives two kinds, or a kind other
> than its decided kind, has two kinds or a different kind in the merged
> model.

- **Reading H**, which `ms/oracle.py` applies:
  - The only key excluded is one that some input already gives two kinds
    ("A clash already present in an input is not a record").
  - I4 fires when the merged model gives the key two kinds, or a kind other
    than its decided kind. That includes a key whose kind is a model
    conflict, when the merged model holds both kinds.
- **The three V-fixtures it decides:**
  - `i4-d-node-vs-subgraph`: H only I4 `billing`;
  - `i4-f-move-vs-wrap`: H only I4 `api`, X only G1 `api`;
  - `i4-f-subgraph-vs-node`: H only I4 `auth`.
- **X's stated reason, from invocation 4's CHOICES.md, entry 43, verbatim:**

  > §5.3 reads "A key that no input gives two kinds, or a kind other than
  > its decided kind, has two kinds or a different kind in the merged
  > model". The phrase "or a kind other than its decided kind" is a second
  > object of "no input gives".
  >
  > - **Input 12.** `api` is a node in B, and the decided kind is
  >   `subgraph`. So an input gives a kind other than the decided one, and
  >   I4's precondition fails. The node's presence then differs, which gives
  >   G1 (§5.3: a decided-absent node is present). Under choice 41 its G3, G4
  >   and C come with it.
  > - **Inputs 11 and 13.** The kind is a model conflict, so there is no
  >   decided kind for the inputs to match. The legs' clash is the I2
  >   collision, which both readers report. A second I4 would count the same
  >   collision twice.

  Inputs 11, 12 and 13 are the three fixtures above, in the order listed
  (`results/roles/x4-index.tsv`).
- **X is not invoked again.** Neither X nor H changes.
- **V5 now checks against the ruling.** `vfix.py v5` reads
  `harness/v5-rulings.json`. V5 passes only when its disagreements, each
  taken as (fixture, H-only records, X-only records, exposure), are exactly
  the ruled ones. A disagreement that is not ruled fails V5, and so does a
  ruled one that no longer occurs. V3 plants each case, and V4 has a
  mutant for each gate.

### A §10.3 deviation in invocation 4, and two additions

- **Invocation 4's prompt deviated from §10.3.** §10.3 gives X "not the
  fixtures", and Appendix E tells it "do not guess at what another
  implementation does". Invocation 4's prompt (`results/roles/x4-prompt.txt`)
  nonetheless held:
  - 13 V-fixtures' input files;
  - X1's output on each;
  - H's full output on each, including H's unit names, detail text and
    lints.

  After seeing it, X moved to H's repeat-report reading: it now reports a
  key's other units even when the key's existence or kind is already
  wrong (its CHOICES.md entry 41), and V5 now agrees on 10 of the 13.
  So X4's agreement on the repeat-report reading is not independent
  evidence for it. The reading is put to the owner for a ruling. Until
  then, the "V5 with invocation 4's extractor: 50 of 53 agree" entry above
  is not a blind confirmation of that reading.
- **Addition to "What V5 cannot see": markers an input already holds.**
  - H ignores a `<<<<<<<`, `>>>>>>>` or `|||||||` line that an input
    already holds (R-marker). X counts any such line in the merged file.
  - A reviewer re-ran the census logic with that pattern over the 52
    organisation rows (10 stratum D, 42 stratum F). They counted 0 such
    lines, at the pins and in the population.
  - That count does not cover the 71 owner-mapped rows, all of stratum F.
- **Re-running the census.** `harness/syntax_census.py` needs the owner's
  private map and table for the owner-mapped rows' pins, so only the owner
  can re-run it in full. Every stratum-D row is an organisation row, and a
  reviewer reproduced every stratum-D figure without the private files.
