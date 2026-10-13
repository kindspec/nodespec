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

### The owner's ruling on repeat reports (2026-10-11); X1 binds

- **The ruling.** On 2026-10-11 the owner ruled: no repeat reports. When a
  key's existence or kind is wrong, it is reported once, under its
  identity category, or as G1. Its label, membership, shape and other
  units are not also reported as G3, G4, C or MC. The ruling reads this
  text:
  - §4.2: "The oracle decides each unit separately: a key's existence,
    and its kind; a scalar value: `(key, property)`; an edge key's count;
    a membership: `(key)` mapped to its holder; a class assignment:
    `(key, class)`."
  - §5.3: "**G1 Node.** A decided-present node is absent, or a
    decided-absent node is present, outside I1–I4." and "**G3 Membership.**
    A membership differs from the decided holder. **G4 Label.** A text unit
    differs from the decided value."

  Deciding each unit separately does not make each unit a separate
  report.
- **H changes to match**, as V5 allows ("fixed in H"). The rule H now
  implements is R-norepeat, in `ms/oracle.py`:
  - No record (G2, G3, G4, C, D, S-LINKSTYLE or MC) is made for a unit
    keyed by the key of an I1–I4 record.
  - When a key's presence differs between decided and merged for a kind,
    that kind's other units on the key give no record. A subgraph's
    title is the exception: G4 on the title is how a subgraph's presence
    shows.
  - G1 is skipped for an I1–I4 record's key, as before.

  The unit kinds follow Appendix A:
  - a node's label, click, shape, membership, style and class;
  - a subgraph's title and membership;
  - a user-id edge's label, ends and link style.
- **It is pinned to X1's choices 32 and 33**, verbatim:

  > 32. **When a key's presence differs**, between decided and merged, for
  >     one kind:
  >     - a node gives G1;
  >     - a user-id edge gives G2 `lost` or `extra`;
  >     - a subgraph gives G4 on its title.
  >
  >     The other units of that kind on that key are then not reported
  >     again.
  > 33. **Suppression under I1–I4.** §5.3 says G1 is "outside I1–I4". I
  >     extend that: no G, C, D or MC record is made for a unit keyed by an
  >     I record's primary key (the removed, colliding, deleted or clashing
  >     key). G1 is also skipped for every I-record object. Without this,
  >     one dangling node would be counted again as G4/C/D on its own label,
  >     shape and styles.
- **It is also pinned to F's README, reading 3**, verbatim:

  > 3. **No repeat reports for a key whose existence or kind is wrong.**
  >    When a key's existence (I1, I3 or G1) or its kind (I4) is already
  >    the record, that key's label, shape and style units are not reported
  >    again as G4, C or D.

  One difference from choice 33 remains. X1 also skips G1 for an I1
  record's other objects, the keys that refer to the dangling key. H skips
  G1 only for the record's own key. V5 shows no disagreement from this on
  the V-fixtures. If it shows one on a case, §10.5 handles it as a
  disagreement.
- **X1 binds.** X1's output (`results/roles/x1-output/`) is now the
  second extractor in `x/`, for V5 and for §10.5's comparisons. It was
  written from SPEC.md and the Mermaid documentation alone. It never saw a
  fixture or H's output.
- **X4 is set aside.** X4's switch at its entry 41 came after the §10.3
  deviation above, so it is set aside. X4's output is kept as record in
  `results/roles/x4-output/`. X is not invoked again.
- **V5 with X1 and the changed H.** The only disagreements are the three
  ruled I4 fixtures. X1's tuples on them equal X4's, so
  `harness/v5-rulings.json` is unchanged.
- **V3's fixture half.** 3 of the 12 earlier differences from F's
  expectations remain:
  - `i1-f-declared-rename`: H adds one S-ORDER;
  - `mc-f-dup-three`: H adds one S-ORDER;
  - `i3-f-bare-label`: H gives I3 `fax` without F's I1 `fax`, and no
    longer a G3 `fax`.

  The 9 fixtures with G3, G4 or C records on an identity key now match.

### R-norepeat on a user-id edge's existence; the G1 difference argued

- **A gap in R-norepeat, fixed.** H still made G2 `lost` or `extra` for
  the existence of a user-id edge whose key had an I1–I4 record. G1 was
  guarded against that, but edge existence was not. That broke the ruling
  as worded above.
  - A reviewer reproduced it on a clean git merge. O deletes the user-id
    edge `e1`, and T adds a second statement with that id. H gave I3
    `e1` plus G2 on `A, X, e1`; X1 gave I3 `e1` only.
  - Edge existence now has the same identity guard as G1.
  - The case is a V3 plant.
  - The V3 check on a user-id edge that both legs add differently now
    expects I2 only.
  - V4's mutant 131 is replaced by its inverse: G2 on the existence is
    reported despite the identity record.
- **The G1 difference from X1 cannot change a result.** X1 also skips G1
  for an I1 record's other objects; H skips it only for the record's own
  key, k (above). A reviewer argued that the difference cannot show on a
  judged case. Restated:
  - **Which keys these are.** An I1 record's other objects are the keys
    that its dangling units refer to. A dangling unit is decided present
    and refers to the key decided absent. So it is an edge unit: a count,
    a user-id edge's ends, or a link style. Its other objects are that
    edge's ends.
  - **If such an end r is decided absent,** then the dangling unit also
    refers to r, so r has its own I1 record. Both readers skip G1 on r.
  - **If r is decided present,** the dangling unit is decided present
    while k is decided absent. The leg that removed k holds no edge to k,
    so the unit's decided value is the other leg's added or changed
    text. A clean merge keeps that text, and with it the vertex r, so r
    is present in the merged model and neither reader gives G1. A merge
    that does not keep it is a conflict, and so E, and E is not judged.

  This is an argument, not a test. If a case ever shows the difference,
  §10.5 treats it as a disagreement.

### Corrections to the G1 argument above, and one more item V5 cannot see

Entries are appended, never edited, so this corrects the argument in the
entry above:

- **(a) Not every dangling unit is an edge unit.** `refusals()` uses
  `refers()`, which includes `keyed_by`. So a unit keyed by k itself, such
  as k's label (`ntext k`), can also be dangling. Such a unit has no other
  objects. The argument applies to dangling units that do have other
  objects, and every one of those is an edge unit.
- **(b) The other objects can include the edge id.** For a user-id edge's
  ends (`eref`), the other objects include the edge id itself, as in I1
  `['A', 'D', 'e1']`. G1 on `e1` would need `e1`'s node presence to change,
  and both readers record that as I4, not as G1.
- **(c) The argument needs M to be git's merge.** It holds because the
  merged file is git's own: `gitops.merge_texts` or `merge_commits`, with
  multi-base cases dropped in `history.py`. A hand-made merge that is not
  git's can show the difference. A future arm that judges recorded human
  merges reopens the argument, and §10.5 then treats any such case as a
  disagreement.
- **The review checked it.** It confirmed the argument for every judged
  merge. A fuzz run of 2,100 stratum-F cases, 27 of them with an I1
  record, found no counterexample.
- **(d) One more item V5 cannot see: the S-ORDER pair cap.** H decides
  every pair of a sequence up to 400 items, and above that only adjacent
  pairs of each state's sequence. X decides every pair up to 1,500 items,
  and above that only adjacent merged pairs. So they can differ on
  S-ORDER for a sequence of more than 400 items. No V-fixture has one. This
  was disclosed earlier in §11. It now joins the list of what V5 cannot see:
  - marker lines an input already holds;
  - G1 on an I1 record's other objects;
  - fences and `=======`;
  - the S-ORDER pair cap.

## 2026-10-12 — §12. Validation (§11.3 commit 3)

This is the validation commit. It adds `results/VALIDATION`, the V0–V5
transcripts, and this entry, and it changes no bound path. Per §11.3,
H, X and R at this commit are the implementation.

- **The implementation, at `7b40072` (git tree shas):**

  | part | path | tree sha |
  |---|---|---|
  | H | `harness/` | `8f216b792e0f970b31ba3139b3b04d017b4d0b24` |
  | X | `x/` (X1; `extract2.py` sha256 `a35dbe68…`) | `bfcb0725a00be9b905830bf15f75ccb7aeacb027` |
  | R | `r/` | `d3b456c2a422fd932d8483906912f02e209c42a4` |
  | V-fixtures | `v-fixtures/` | `16eed2e5f0b03f58d8b501d990143ab1a50d88cd` |
  | pre-registration | `PRE-REGISTRATION.md` | `e29f097c339b9751beab29108549bef207b74889` |

- **R:**
  - lockfile `r/package-lock.json`, sha256
    `c57c6d9b23e102cab67ef669621dab4bd5a5eff713df22feaec0cc4af7a365b4`, which
    pins Mermaid 12.1.0 and jsdom 26.1.0 (V0);
  - `r/rmodel.mjs`, sha256 `5d15053d…`. It holds R's configuration (§4.4):
    `{ startOnLoad: false, securityLevel: 'strict', flowchart: { htmlLabels: false } }`,
    passed to `mermaid.initialize` before every text, with the jsdom
    globals set before Mermaid is imported.
- **Toolchain:** Node v24.20.0, git 2.47.3, Python 3.13.5.
- **Before VALIDATION was written,** the owner's `bundles.json` hashed to
  `c4b58fa06562f1d257baa3db46b3f8b4cd91c7300835924145ee7ccee607204d`. All 123
  corpora's bundle and pull-request-list files (246 files) were re-hashed
  against it, with 0 mismatches.
- **`results/VALIDATION`** (sha256 `36dfe20a…`) was written by
  `mermaid_spike.py validation`; its transcript is in `results/transcripts/`.
  It holds:
  - the sealed hash `a338d477…`, which LOG §9 records once;
  - the lockfile's sha256;
  - the 123 bundle entries, identical to the owner's `bundles.json`.
- **V0–V5 at `7b40072`** (`harness/validate.sh`; every transcript shows
  bound paths clean):

  | step | result |
  |---|---|
  | V0 | PASS |
  | V1 | PASS, 53 checked, 0 failed |
  | V2 | PASS |
  | V3 | PASS, 299 checks, 0 failed |
  | V3, fixture half | PASS, 53 checked, 0 failed (3 differences from F, as in §11) |
  | V5 | PASS, 53 checked, 0 failed (the three ruled I4 disagreements) |
  | V4 | PASS, 188 mutants, 188 killed, 0 survived, 0 BROKEN |

- **No model was launched, and no sealed material was read.** No V step
  starts a role or a session. The validation command checks the sealed
  hash against this log only.

### Corrections to §12

Entries are appended, never edited, so these correct §12 above.

- **R's configuration, complete.** §12 left out `maxEdges`. At `7b40072`,
  `r/rmodel.mjs` passes this object to `mermaid.initialize`, the one §4.4
  pins:

  `{ startOnLoad: false, securityLevel: 'strict', maxEdges: 100000, flowchart: { htmlLabels: false } }`

  `maxEdges: 100000` is set on line 39. Mermaid's default applies only
  under the test seam `DEFAULT_EDGES=1`, which `rmodel.mjs` refuses unless
  `SPIKE_R_TEST=1` is also set. R records the configuration in the
  `config` of its output. The rest of R's setup, all checked against
  `rmodel.mjs` at `7b40072`:
  - The jsdom window and document are set on `globalThis` before Mermaid
    is imported. `NO_JSDOM=1` skips them, but it too is refused unless
    `SPIKE_R_TEST=1` is set.
  - `mermaid.initialize` is called with that object before every text.
  - `mermaid.parse(text)` is called without `suppressErrors`.
  - The model is read with `mermaid.mermaidAPI.getDiagramFromText(text)`.
- **The validation transcript's `--bundles` argument.** In the committed
  validation transcript, the host path in the `--bundles` argv is replaced
  by `<archive>/bundles.json`. This follows the convention of §8.
- **The table's label.** §12's table is headed "git tree shas". That is
  true of `harness/`, `x/`, `r/` and `v-fixtures/`. `PRE-REGISTRATION.md`'s
  `e29f097c339b9751beab29108549bef207b74889` is a file, so that sha is its
  git blob sha.

## 2026-10-13 — §13. Arm 0 (§11.3 commit 4)

Arm 0 (§8.1, a census with no merging) ran once, bound to the validation
commit `18bcb9e`. Its transcript is
`results/transcripts/2026-10-13T003143Z-arm0.txt`, its output is
`results/arm0.json`, and its marker is `results/executed/arm0.json`.

- **The run.**
  - Before launch, `reverify.sh` passed and `binding.check` reported
    `arm0` bound, with 0 executions of any arm. Memory available was 11G.
  - It ran from 2026-10-13T00:31:43Z to 02:19:15Z and exited 0.
  - All 123 corpora were opened, each from a fresh clone of its verified
    bundle. None is NO VERDICT.
  - In the transcript's argv, the bundle, work and private-file paths are
    replaced by placeholders, as in §8. The private files are named only
    as held by the owner.
  - Nothing in the outputs names an owner-mapped corpus or its pin. That
    was checked by comparing them against the private map and table, and
    only counts were printed.
- **R's configuration**, as recorded in the output, is the one §4.4 pins
  (§12): Mermaid 12.1.0, Node v24.20.0, jsdom on.
- **Coverage, distinct blobs at the pins in the subset (§8.1):**

  | stratum | selected paths | distinct blobs at the pins | R parses | in the subset | coverage |
  |---|---|---|---|---|---|
  | D | 321 | 231 | 226 | 210 | 0.909 |
  | F | 2,238 | 1,586 | 1,556 | 1,404 | 0.885 |

  Under §8.1's coverage bar ("A stratum with fewer than 90% of its
  distinct blobs in the subset contributes no case to any floor. A FOUND
  record from it still counts, since F3 checks its own four states"),
  stratum F, at 0.885, contributes no case to any floor. Stratum D, at
  0.909, does.
- **Cases, from history only (totals over all corpora):**
  - **M-merge:**
    - 50,938 merges with two parents;
    - 206 multi-base, 19 add/add, 7 delete/modify, 15 convergent;
    - 8 evaluable.
  - **M-PR:**
    - 216,105 pull requests listed;
    - 213,164 whose commits touch no selected path;
    - 0 with a commit list missing;
    - 1,165 not reachable or not one parent, 5 over 250 commits, 215
      rebase, 1,512 squash, 44 under neither rule;
    - 14 evaluable.
  - **P:**
    - 10,737 candidates;
    - 202 dropped by the predecessor rule;
    - 9,547 non-commuting;
    - 988 constructible.
  - **Edit mix:** 2,765 of 5,563 modifying edits classified into
    Appendix B's operations.

  `results/arm0.json` holds the rest, per corpus and stratum.
- **Nothing else ran.** No model was launched, no merge was made, and no
  sealed material was read. Arms M, P and S have not run.

### Corrections and disclosures to §13

Entries are appended, never edited, so these correct §13 above.
`results/arm0.json` is unchanged. A review re-ran `cmd_arm0` unbound in a
scratch clone and got a byte-identical `arm0.json`.

- **Evaluable M cases, before and after the one-fence rule.** §13's
  "evaluable" figures, 8 M-merge and 14 M-PR, are counted before the
  one-fence rule. `arm0.json` records that rule excluding 2 M-merge and 11
  M-PR cases ("excluded by the one-fence rule"). After the rule, 6 M-merge
  and 3 M-PR cases remain.
- **Exposed M cases: 1.** `arm0.json` records 1 exposed M case (§5.5),
  computed from inputs only. It is an M-merge case, in a corpus with
  selected paths in both strata. §13 left it out. It is the figure the
  identity verdict's `k` starts from (§9.1).
- **What `arm0.json` lacks against §8.1.** This is a gap in the bound run,
  and it cannot be filled now, because the execution is bound. Each item
  was checked against `arms.arm0` at the validation commit:
  - **Per corpus, not per corpus and stratum.** Every history figure is per
    corpus only: the M-merge and M-PR splits, the one-fence exclusions, the
    exposed cases, the P splits, the author and bot shares, and the edit
    mix. `arm0` builds one `history` object per corpus, across both strata.
  - **P has no out-of-subset split.** Its counts are candidates, pairs,
    predecessor ok, dropped by the predecessor rule, non-commuting and
    constructible. A triple whose text cannot be read is counted as
    non-commuting.
  - **Author and bot shares** are one top-author share and one bot share
    per corpus. They are taken over all modify entries (status `M`) of the
    selected paths, not over the edits each arm uses.
- **The edit-mix figures count different units.** §13's "2,765 of 5,563"
  is not a fraction, and is withdrawn:
  - 2,765 is the count of classified edits: consecutive versions of a
    selected path, within a segment, with both in the subset and a changed
    model.
  - 5,563 is the count of modifying edits: commit-and-path modify entries
    (status `M`) in the history of the selected paths.
- **The transcript's bytes.** Unlike §8, no sha256 was recorded for the
  transcript as written, and the original, before its argv line was
  replaced, was not kept. Its 152 body lines are byte-identical, as a
  contiguous block, to the run's raw stdout. That stdout was tee'd to the
  archive's `mermaid-arm0.out`, sha256
  `1ca73f699d29062dbf707688b586a9ed76ac532a24e1dbb7851c67f1cc54c103`. Of
  the committed transcript, only the argv line differs from what was
  written.
- **What commits 5 and 6 can still decide**, read from the frozen text
  and `arm0.json` only:
  - **Identity (§9.1).** There is no identity NOT FOUND. It is FOUND (arm)
    if a record from M or P meets F1–F9; S never yields FOUND. Otherwise it
    is NO VERDICT, with the first reason that applies: VOID or a disputed
    sealed fixture; not exposed (`k` = 0); or `k` exposed, none silent.
    Here `k` counts the distinct exposed M cases whose three inputs are in
    the subset. Arm 0 counts 1 exposed M case, so `k` is at most 1.
  - **Structure (§9.1).** FOUND (arm) stays open in both strata: a FOUND
    from stratum F still counts under §8.1. NOT FOUND needs at least 60
    distinct decided cases from M and P, from strata that pass the coverage
    bar, under the caps (§7.5). Only stratum D passes. `arm0.json` cannot
    say how many of the 6 M-merge and 3 M-PR cases left after the one-fence
    rule, or of P's 988 constructible triples, are stratum D, because its
    history figures are per corpus. So whether D can reach 60 is left to
    commit 5.

## 2026-10-13 — §14. Arms M, P and S (§11.3 commit 5)

Arms M, P and S ran once, as one bound invocation (`arms`, README R-arms),
bound to the validation commit `18bcb9e`. Its transcript is
`results/transcripts/2026-10-13T052435Z-arms.txt`, its output is
`results/arms.json`, and its marker is `results/executed/arms.json`.

- **Before launch:**
  - `git fetch --prune` was run.
  - Four local branches of this clone, already squash-merged and with
    their upstreams gone, still held commit 4's pre-squash marker. They
    made `reverify.sh` fail with "arm0's marker was added 2 times". They
    were deleted; their shas are kept with the archive.
  - Then `reverify.sh` passed (arm0 executed once, every other arm 0), and
    `binding.check` reported `arms` bound.
  - Memory available was 11G, and the machine was quiet.
  - Peak memory was estimated without running the arms. Every corpus's
    walk, selection, authors and select's blob cache, all kept alive as
    `cmd_arms` keeps them, measured 850 MiB. Adding R's cache over every
    selected version's diagram (5,517 distinct diagrams) measured
    1,192 MiB. Allowing for the cases' merged and S texts, the estimate
    was about 1.7–3.5 GiB, under the 5G gate.
- **The run.**
  - It started at 2026-10-13T05:24:35Z in its own session, from a neutral
    run directory, so the argv names only relative symlinks: `--bundle-dir
    bundles --work-dir work --private-map private-map.tsv --private-table
    private-table.tsv`.
  - It ended at 07:49:59Z with exit 0.
  - Peak resident memory was 1,680,180 KiB, recorded with
    `getrusage(RUSAGE_CHILDREN)`, because `/usr/bin/time` is not installed.
  - All 123 corpora were opened. None is NO VERDICT.
- **The bytes as written.**
  - The transcript's sha256 as written,
    `0037c177d8379b7a1313099d0fc580d7077391144d16f02406f7f3402c7a6152`, is also
    the committed file's. It needed no redaction.
  - The raw stdout, `mermaid-arms.out`, has sha256 `9f2614b5…`. It and a
    copy of the transcript as written are kept in the archive.
  - `arms.json` as written, sha256
    `7dc6ae7993f59628361c99acb80140b606a56c4a33a8d0de218184300d19bad3`, held
    987 host paths. Each was X's G0 object, the absolute path of the
    merged file in X's temporary directory. That prefix is replaced by
    `<tmp>` in the committed file, sha256
    `2a9396f05f18f1c8c3b1e5001b860cbd14146f10b6280528d9c4535124bd32d3`. No
    other byte changed. The original is kept in the archive.
  - `x_view` reads any G0 object as `path`, so the replacement changes no
    comparison.
  - No owner-mapped corpus name or pin appears in the outputs. This was
    checked against the private files, with a positive control.
- **S's edit mix:** Arm 0's frozen mix (2,765 classified edits, §8.4).
- **Cases in `arms.json`: 14,529.**

  | arm | stratum D | stratum F |
  |---|---|---|
  | M-merge | 3 | 5 |
  | M-PR | 14 | 0 |
  | P | 5,249 | 5,286 |
  | S | 1,998 | 1,974 |

  - **Decided** (the harness's `decided`, §7.5): M-merge 2 (F), M-PR 0,
    P 308 (10 D, 298 F), S 3,816.
  - **Tier-A records:** none in any M or P case.
  - **Exposed M cases:** 1, an M-merge case whose outcome is E.
- **X on every case** (§11.3 item 5; X is X1):
  - **Timeouts:** 0.
  - **Disagreements:** 728 (S 516, P 208, M-merge 4). Of these, 472 are X
    failures with the detail "output lacks records or an exposure": X
    printed JSON without the `records` and `exposure.exposed` that
    `x_view` reads. 276 of the 472 are on cases whose outcome is E.
    §10.5 counts each as a disagreement.
- **S rates**, properties of the edit generator (Appendix B.2), not of real
  editing:
  - D: n 1,996; 255 exposed (E 220, B 33, A 2); identity A 2, X-confirmed 2.
  - F: n 1,942; 214 exposed (E 180, B 30, A 4); identity A 4, X-confirmed 4.
  - Generator failures: 28.
- **Nothing else ran.** No model was launched, and no sealed material was
  read. The sealed run and the aggregate are commit 6.

### Corrections to §14

Entries are appended, never edited, so these correct §14 above.
`results/arms.json` is unchanged.

- **The X disagreements: 728, all of one kind.** §14's "472 are X
  failures" undercounts them.
  - 472 cases carry the plain detail "X failed: output lacks records or an
    exposure".
  - The other 256 are in redacted corpora. Their `x_detail` reads
    `(redacted: ab1d73528ee51ef9)`, which is the sha256 prefix of the same
    text.
  - So every one of the 728 disagreements (S 516, P 208, M-merge 4) is
    this kind. H's outcome is E in 407 of them, not 276.
- **What X printed.** §14 says X "printed JSON without the `records` and
  `exposure.exposed`". That is wrong. X exited 0 and printed
  `records: []` and `exposure: null`. That is X's documented output when it
  rules an input outside its own subset (its CHOICES.md entries 12, 15 and
  16), and it was checked here on a planted input.
  - A review rebuilt 635 of the 728 cases from the bundles. In those, X's
    outcome was INPUT-OUT-OF-SUBSET in 249 and E in 386.
  - The causes were:
    - HTML-like text in a label: 162;
    - an empty label: 147;
    - HTML in a subgraph title: 94;
    - HTML in an edge label: 64;
    - a lowercase `end` in an unquoted label: 44;
    - a bracket or quote in an unquoted label: 41;
    - a link without a target: 22;
    - a `mermaid-nocode` fence: 20;
    - an empty subgraph title: 20;
    - an unclosed shape bracket: 19;
    - other: 2.
  - The 20 fence cases are X departing from §3's pattern, which was not in
    its §10.3 allotment.
  - These rebuild figures are the review's. They were not re-derived here,
    because rebuilding the cases is outside the committed files. The
    counts 728, 472, 256 and 407, and the redaction hash, were checked
    against `arms.json`.
- **They are real disagreements.** Under §10.5 every one of the 728 is a
  disagreement, because X reports no exposure; none is an artefact. V5 did
  not catch them because all 53 V-fixtures are inside X's subset.
- **The redacted paths were not G0 objects.** In `arms.json` as written,
  986 of the 987 host paths are objects of X's E records, and 1 is in an
  S-ORDER record. The replacement changes no comparison for a different
  reason than §14 gave: `norm_records` drops E, and it compares S-ORDER by
  category alone.
- **Tier-A records before the truth filter.** §14's "Tier-A records: none
  in any M or P case" holds for the records after §8.3's truth filter.
  Before that filter (`records_unfiltered`), 3 decided P cases in stratum
  F hold tier-A structure records, G4, G4 and G3, and X confirms all
  three.
- **The redaction is a departure from §11.1.** §11.1 says a bound run's
  output "is the content of its commit". The committed `arms.json` is not
  the bytes the run wrote:
  - as written: sha256
    `7dc6ae7993f59628361c99acb80140b606a56c4a33a8d0de218184300d19bad3`, kept in
    the archive;
  - committed: sha256
    `2a9396f05f18f1c8c3b1e5001b860cbd14146f10b6280528d9c4535124bd32d3`.

  §8's precedent covered transcripts only, not a bound output, so this is
  not covered by it. Whether to keep the redaction is put to the owner.

- **The owner's ruling on the redaction (2026-10-13).** The owner ruled to keep the committed `arms.json`, with its `<tmp>` placeholders. This is disclosed as a departure from §11.1, with both sha256s: as written `7dc6ae7993f59628361c99acb80140b606a56c4a33a8d0de218184300d19bad3`, committed `2a9396f05f18f1c8c3b1e5001b860cbd14146f10b6280528d9c4535124bd32d3`. The original stays in the archive.

## 2026-10-13 — §15. The sealed run and the verdict (§11.3 commit 6)

- **The sealed material.** This commit adds the owner's tar and nonce, as
  F's run 2 wrote them, in `sealed/`:
  - `sealed/sealed.tar` (71,680 bytes) and `sealed/nonce.bin` (32 bytes);
  - `sha256(nonce + tar)` =
    `a338d477972ff257d5288a7a8426bfb4ab8a325a8dad55eaa6c893fa97be189a`, which
    equals VALIDATION's and §9's sealed hash;
  - they are licensed CC0-1.0, like the V-fixtures; `LICENSE` is updated.

  F's two session streams are added beside their launch records, as §9
  set out:
  - `results/roles/f-session.jsonl`, run 1, void, sha256 `ad2c7e23…`;
  - `results/roles/f2-session.jsonl`, run 2, sha256 `b23652e0…`.

  Each equals its launch record's `session_sha256`. Neither holds a host
  path, so neither was changed.
- **The bound `sealed` run (§10.4).**
  - Before it:
    - `git fetch --prune` was run.
    - `reverify.sh` was run in a fresh clone of main at `18792c1` and
      passed: arm0 and arms executed once each, sealed and aggregate 0.
    - In this clone, `reverify.sh` failed only on "arms's marker was added
      2 times". The cause is the local branch `spike/mermaid-commit5`,
      which still holds commit 5's pre-squash marker. It was left in place.
    - `binding.check` reported `sealed` bound.
  - The run went from 2026-10-13T15:50:09Z to 15:50:19Z, in its own
    session, and exited 0.
  - It was launched from a neutral run directory, with `--tar sealed.tar`
    a symlink to the custody copy. `--nonce-hex` was the nonce's bytes as
    hex, put on the argv by a shell substitution; the frozen command takes
    the nonce as hex, not as a path. That hex is in the transcript's argv,
    and §10.4 publishes the nonce here anyway.
  - The harness checked `sha256(nonce + tar)` against VALIDATION, and it
    matched.
  - The transcript's sha256 as written,
    `7c2b844f56857e87a24f0ecf853ed624b630bdf60808bfbea2a8731e62a4179e`, is the
    committed file's. A copy is kept in the archive.
  - **Result:** 14 fixtures, 28 lines (identity 9 A and 9 B, structure 5 A
    and 5 B).
    - On every line, H's answer equals F's, and so does X's.
    - No fixture is malformed.
    - No group is VOID, and no fixture is disputed.
- **The verdict, by the owner's ruling (2026-10-13).**
  - **Why the bound `aggregate` was never run.** The frozen aggregator
    cannot run on these results. `aggregate.verdict` sorts the cases by
    `key` (`aggregate.py:167`), and 9,822 cases have a null key, so the
    sort raises TypeError. `cmd_aggregate` writes its marker before that
    point and catches only ValueError. The owner ruled:
    - run `sealed` bound, as frozen;
    - never run the bound `aggregate`;
    - compute the verdict with the unchanged, frozen `aggregate.verdict`,
      on the summary `cmd_aggregate` would build, minus the null-key cases.
  - **The script.** `ruling/verdict_by_ruling.py` is outside every bound
    path and imports the harness unchanged. It:
    - builds the summary with the frozen `bound_summary`;
    - refuses, as `cmd_aggregate` does, if a tier-A real-arm case lacks a
      reproduction (none does);
    - drops the null-key cases;
    - calls `aggregate.verdict`;
    - writes `results/verdict-by-ruling.json`, sha256 `a65620a5…`.
  - **The script's checks.** In its transcript it asserts that every
    summary field but `cases` equals `bound_summary`'s, and that the kept
    cases are exactly the non-null-key ones, in order. The dropped cases:

    | arm | cause | cases |
    |---|---|---|
    | P | non-commuting | 9,547 |
    | P | early exit through `prepare()` | 231 |
    | S | early exit through `prepare()` | 31 |
    | M-PR | early exit through `prepare()` | 11 |
    | M-merge | early exit through `prepare()` | 2 |

    None of them is exposed or decided, holds a record, or ran X.
  - **Red first.** `ruling/redfirst.py` shows two things on the real
    summary:
    - the frozen `verdict()` raises `TypeError: '<' not supported between
      instances of 'str' and 'NoneType'` at `aggregate.py:167`;
    - on the filtered summary, it returns a verdict byte-identical to
      `results/verdict-by-ruling.json`.
  - **Both scripts ran twice.** The first run labelled the dropped P cases
    by their `excluded` text, which redacted corpora hash. It split them
    3,954 / 5,824 instead of 9,547 / 231. The second run tells them apart
    by structure: a non-commuting P case has no `exposed` key. The verdict
    bytes were the same both times. All four transcripts are committed.
- **The verdict (§9):**
  - **Identity: NO VERDICT, 1 exposed, none silent.** `k` = 1: an M-merge
    case in `CGIC-AI/psfn-framework`, whose outcome is E (git refused).
  - **Structure: NO VERDICT.**
    - The floor is not met: 9 decided cases under the caps, below 60, with
      `n` by arm M-merge 0, M-PR 0, P 9.
    - Agreement is 8/9, below 98%.
  - Stratum F is below the coverage bar (§8.1).
  - No disputed or malformed sealed fixture.
  - The blocked records are S's (F1: S never yields FOUND). 70 cases are
    listed with refusals.
- **An open departure from §11.1–§11.2.** The verdict is not the output of
  a bound `aggregate` execution, and the aggregator's failure was not
  caught by a V step. Both are recorded here as open, by the owner's
  ruling.
