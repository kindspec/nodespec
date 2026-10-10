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

### Open items at the time

§1's four open items are settled in §2.

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

## Blind roles

Not yet launched. Each launch is logged here with its export manifest,
prompt, model id and date (§10.3).
