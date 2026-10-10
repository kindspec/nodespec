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

## Blind roles

Not yet launched. Each launch is logged here with its export manifest,
prompt, model id and date (§10.3).
