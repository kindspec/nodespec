# Writing nodespec merge cases

You are writing conformance cases for nodespec that merge real branches with
stock git and check the merged file. Everything you may read is in this
directory. Read `SPEC.md` completely before writing any case; it is the only
authority on whether a file is accepted or refused, and on which identifier and
id a refusal names. `conformance/cases/README.md` explains the existing
single-file cases and `expect.json`; `existence/` holds ten constructed wrong
merges from before the profile existed, each a `base.mmd`, `ours.mmd` and
`theirs.mmd`; `adjudications/0001-mermaid-profile.md` is the decision SPEC.md was
written from.

## Layout

Write each case to `out/merge/<case-name>/`, a kebab-case name saying what the
case is:

    base.mmd      the common ancestor
    ours.mmd      one branch's version
    theirs.mmd    the other branch's version
    merged.mmd    only when the merge is clean: the file stock git produces
    expect.json   what happens
    WHY.md        what each branch does, why git merges it as it does, and the
                  SPEC.md sentences (quoted, with section) that decide the
                  verdict on the merged file

All four `.mmd` files are UTF-8 with LF line endings and end with a newline.

The runner makes a repository holding `base.mmd` under one filename, commits
`ours.mmd` on one branch and `theirs.mmd` on another, merges ours and then
theirs into main with unconfigured git, and compares the result with
`merged.mmd` byte for byte. You may and should run stock git yourself to
confirm what it produces: git is not the checker. Use a throwaway directory
under `out/../git-scratch/`, and run git with no user configuration, for
example `HOME=/nonexistent XDG_CONFIG_HOME=/nonexistent GIT_CONFIG_NOSYSTEM=1`
plus `-c user.name=t -c user.email=t@e`.

## expect.json

Exactly one of:

    {"merge": "clean", "accept": true}
    {"merge": "clean", "refusal": ["<identifier>", ...]}
    {"merge": "clean", "refusal": ["<identifier>", ...], "ids": {"<identifier>": ["<id>", ...]}}
    {"merge": "conflict"}

`refusal` and `ids` mean exactly what they mean for single-file cases
(`conformance/cases/README.md`): list every identifier SPEC.md §9 gives the
merged file, and for each identifier §9 reports with an id, every id it applies
to. A conflicted merge carries no verdict: git stopped, which is loud.

`base.mmd`, `ours.mmd` and `theirs.mmd` must each be in the profile (accepted by
SPEC.md), so that any refusal is one the merge produced. Say so in `WHY.md`.

## What to cover

1. Every shape in `existence/cases/`, rewritten where needed so that all three
   inputs are in the profile, with the verdict SPEC.md now gives the merged file.
   Name the existence case each one comes from in its `WHY.md`.
2. The merges SPEC.md describes as made loud: each rule whose stated purpose is
   a merge (search SPEC.md for "merge" and "branch"), at least one clean merge
   that the rule refuses, and where SPEC.md allows it, an accepted control that
   differs as little as possible.
3. The merges SPEC.md §11 says it does not prevent: clean, accepted.
4. Ordinary merges that must stay accepted: disjoint additions, an edit on each
   side of unrelated lines, the same edit on both sides, `class` and `style`
   lines, subgraphs and member lines.
5. At least a few conflicts, so the suite shows the runner telling a conflict
   from a clean merge.

Aim for 40 to 70 cases. Quality over count: each case should make one point.

## Rules

- Read nothing outside this directory, and do not use the network. In
  particular do not look for, or ask for, any nodespec checker or its tests.
- Derive every verdict from SPEC.md by hand. Where SPEC.md does not decide a
  case, do not write the case; list it in `out/merge/AMBIGUITIES.md` with the
  sentences that leave it open.
- When you finish, write `out/merge/INDEX.md`: one line per case with its
  verdict, and a count by verdict.
