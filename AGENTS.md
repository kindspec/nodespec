# AGENTS.md

Instructions for AI coding agents working in this repository.

**Read the org contract first:**
[kindspec/.github/AGENTS.md](https://github.com/kindspec/.github/blob/main/AGENTS.md)
— the two standing rules, the worktree information barrier, the review gate, and
the conventions that travel between kinds. This file carries only what is
specific to nodespec, and wins where the two conflict.

## Status

**The kind has earned its existence** (`existence/RESULT.md`), and its
format is decided: `docs/adjudications/0001-mermaid-profile.md`.
`SPEC.md` is draft 0, written from it. nodespec is the **nodes kind** — identity is
named, not positional — alongside [rowspec](https://github.com/kindspec/rowspec) and [blockspec](https://github.com/kindspec/blockspec).

`reference/nodespec/` is a reference checker written from `SPEC.md`.
`conformance/cases/` holds its conformance cases, written from
`SPEC.md` alone by an author who read no checker, and the checker passes
them unchanged.

## Commands

```sh
just setup    just check    just test    just mutants
just conform [ROOT]       # a case tree, conformance/cases by default
just conform-exact [ROOT] # the same, requiring exactly the listed refusals
just run FILE...          # nodespec check FILE...
```

`reference/` is standard library only, which `tests/test_boundary.py`
enforces. `just mutants` breaks the checker one token at a time, and a
test under `tests/` must fail on each mutant.

## Before writing anything

**Read `DESIGN-BRIEF.md` completely.** It carries what is already decided *with
the measurement that decided it*, what is genuinely open, and the one process
question that must be settled first. It exists so this design pass argues about
the open questions rather than rediscovering the settled ones.

The evidence it cites lives in
[kindspec/research](https://github.com/kindspec/research) —
`design-findings/` and `experiments/`. Cite it by path and commit. The corpora
themselves are not redistributed; `CORPORA.md` names each one and its source.

## The constraint specific to this kind

**This kind must earn its existence before it is built.** The brief says so
explicitly, and a finding that it does not is a legitimate and valuable outcome —
the same standard rowspec applies to itself in its own README: *"if your table is
a list of facts, you probably do not need this."*

An experiment that decides whether a format should exist has its criterion
**pre-registered**: written down and committed before the experiment runs, so the
bar cannot move once the results are in.

## Do not

- **Do not reuse rowspec's syntax.** One syntax for documents and tables is a
  trap; one MODEL, several grammars is the sound version. JATS learned this in
  2003 and encoded the lesson architecturally.
- **Do not port rowspec's identity design.** It does not transfer, and the brief
  explains why with the measurement.
- **Conformance cases are written from `SPEC.md` by an author who has not seen
  any implementation, and they run in CI against the reference checker,
  unchanged.** The adversarial discipline cannot be retrofitted, and a suite
  nothing runs stops checking anything — rowspec's second implementation
  drifted 117 cases behind the moment nothing ran it. The first instance is
  #15: its cases were written from `SPEC.md` alone, the checker never saw them,
  and it passed them unchanged.
