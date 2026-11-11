# nodespec merge cases

Each case is `base.mmd`, `ours.mmd`, `theirs.mmd`, `expect.json`, `WHY.md`, and `merged.mmd` when stock git merges clean. Every verdict was derived by hand from SPEC.md; git was run only to produce `merged.mmd` and to confirm clean or conflict.

## Count by verdict

| verdict | cases |
| --- | --- |
| clean, accepted | 29 |
| clean, refused | 36 |
| conflict | 6 |
| total | 71 |

Refusal identifiers among the refused cases:

- `class-not-last`: 1
- `direction-twice`: 2
- `duplicate-declaration`: 5
- `duplicate-edge`: 4
- `kind-clash`: 3
- `malformed-line`: 1
- `member-twice`: 2
- `membership-cycle`: 1
- `statement-in-block`: 1
- `styled-twice`: 2
- `too-many-edges`: 1
- `undeclared-id`: 12
- `wrong-kind`: 1

## Existence cases rewritten into the profile (`BRIEF.md` item 1)

- `existence-01-rename-vs-new-edge`: clean, refused: `undeclared-id` (`undeclared-id`: `api`)
- `existence-02-delete-vs-new-edge`: clean, refused: `undeclared-id` (`undeclared-id`: `auth`)
- `existence-03-same-id-added-twice`: clean, refused: `duplicate-declaration` (`duplicate-declaration`: `q`)
- `existence-04-retarget-vs-rename-adjacent-conflict`: conflict
- `existence-04-retarget-vs-rename-spaced`: clean, refused: `undeclared-id` (`undeclared-id`: `auth`)
- `existence-05-delete-vs-restyle-adjacent-conflict`: conflict
- `existence-05-delete-vs-restyle-spaced`: clean, refused: `undeclared-id` (`undeclared-id`: `worker`)
- `existence-06-subgraph-vs-node-same-id`: clean, refused: `kind-clash` (`kind-clash`: `cache`)
- `existence-07-relabel-vs-rename-conflict`: conflict
- `existence-08-bare-rename-vs-new-edge`: clean, refused: `undeclared-id` (`undeclared-id`: `b`)
- `existence-09-bare-delete-vs-new-edge`: clean, refused: `undeclared-id` (`undeclared-id`: `c`)
- `existence-10-bare-retarget-vs-delete`: clean, refused: `undeclared-id` (`undeclared-id`: `e`)
- `existence-10-bare-retarget-vs-delete-adjacent-conflict`: conflict

## Rules whose purpose is a merge, with controls (item 2)

- `delete-subgraph-vs-new-edge-to-it`: clean, refused: `undeclared-id` (`undeclared-id`: `backend`)
- `delete-node-vs-member-line`: clean, refused: `undeclared-id` (`undeclared-id`: `c`)
- `delete-subgraph-vs-nesting-it`: clean, refused: `undeclared-id` (`undeclared-id`: `inner`)
- `rename-class-vs-new-class-line`: clean, refused: `undeclared-id` (`undeclared-id`: `hot`)
- `delete-edge-id-vs-class-on-it`: clean, refused: `undeclared-id` (`undeclared-id`: `e1`)
- `delete-node-vs-new-edge-between-others-accepted`: clean, accepted
- `subgraph-added-twice`: clean, refused: `duplicate-declaration` (`duplicate-declaration`: `tier`)
- `subgraph-added-twice-same-place-accepted`: clean, accepted
- `edge-id-added-twice`: clean, refused: `duplicate-declaration` (`duplicate-declaration`: `e1`)
- `same-edge-with-id-added-in-two-places`: clean, refused: `duplicate-declaration` (`duplicate-declaration`: `e1`)
- `classdef-added-twice`: clean, refused: `duplicate-declaration` (`duplicate-declaration`: `warm`)
- `classdef-added-twice-same-place-accepted`: clean, accepted
- `node-vs-edge-id-same-id`: clean, refused: `kind-clash` (`kind-clash`: `link1`)
- `node-vs-class-same-id`: clean, refused: `kind-clash` (`kind-clash`: `cache`)
- `node-replaced-by-class-vs-new-edge`: clean, refused: `wrong-kind` (`wrong-kind`: `cache`)
- `unnamed-edge-added-twice-in-two-places`: clean, refused: `duplicate-edge`
- `unnamed-edge-moved-on-both-branches`: clean, refused: `duplicate-edge`
- `unnamed-edge-moved-on-one-branch-accepted`: clean, accepted
- `edge-group-vs-single-edge`: clean, refused: `duplicate-edge`
- `edge-label-padding-added-twice`: clean, refused: `duplicate-edge`
- `edge-label-quoted-vs-unquoted-accepted`: clean, accepted
- `direction-added-on-both-branches`: clean, refused: `direction-twice`
- `same-direction-added-in-two-places`: clean, refused: `direction-twice`
- `same-direction-added-same-place-accepted`: clean, accepted
- `node-moved-into-two-blocks`: clean, refused: `member-twice` (`member-twice`: `a`)
- `member-added-twice-in-one-block`: clean, refused: `member-twice` (`member-twice`: `a`)
- `member-added-twice-same-place-accepted`: clean, accepted
- `subgraphs-nested-each-in-the-other`: clean, refused: `membership-cycle` (`membership-cycle`: `s`, `t`)
- `subgraph-nested-on-one-branch-accepted`: clean, accepted
- `style-added-on-both-branches`: clean, refused: `styled-twice` (`styled-twice`: `api`)
- `class-added-on-both-branches`: clean, refused: `styled-twice` (`styled-twice`: `a`)
- `same-style-added-same-place-accepted`: clean, accepted
- `statement-added-above-new-class-line`: clean, refused: `class-not-last`
- `class-line-added-after-class-lines-accepted`: clean, accepted
- `edges-added-past-500`: clean, refused: `too-many-edges`
- `edges-added-up-to-500-accepted`: clean, accepted
- `block-end-moved-over-new-edge`: clean, refused: `statement-in-block`

## What SPEC.md §11 does not prevent (item 3)

- `node-id-reused-for-new-node-accepted`: clean, accepted
- `node-replaced-by-subgraph-vs-new-edge-accepted`: clean, accepted
- `subgraph-replaced-by-node-vs-member-line-accepted`: clean, accepted
- `same-node-added-same-place-accepted`: clean, accepted
- `same-unnamed-edge-added-same-place-accepted`: clean, accepted
- `delete-node-vs-move-declaration-accepted`: clean, accepted
- `delete-edge-with-id-vs-move-accepted`: clean, accepted
- `delete-subgraph-vs-move-block-accepted`: clean, accepted
- `delete-member-line-vs-move-accepted`: clean, accepted
- `class-redefined-vs-assigned-accepted`: clean, accepted

## Ordinary merges that stay accepted (item 4)

- `disjoint-additions-accepted`: clean, accepted
- `unrelated-edits-on-each-side-accepted`: clean, accepted
- `same-edit-on-both-sides-accepted`: clean, accepted
- `style-lines-on-different-nodes-accepted`: clean, accepted
- `class-lines-on-different-nodes-accepted`: clean, accepted
- `subgraphs-added-on-both-sides-accepted`: clean, accepted
- `member-lines-added-to-different-blocks-accepted`: clean, accepted
- `relabel-vs-new-edge-accepted`: clean, accepted

## Added in review

- `member-line-left-outside-block`: clean, refused: `malformed-line`

## Further conflicts (item 5)

- `different-styles-same-place-conflict`: conflict
- `different-nodes-added-same-place-conflict`: conflict

## Rules no clean merge of in-profile inputs can reach

A clean merge keeps whole lines from its inputs, so a refusal that depends on one line alone cannot appear in a clean merge of three in-profile files: `bad-encoding`, `leading-bom`, `lone-cr`, `conflict-marker`, `no-header`, `not-admitted`, `reserved-id`, `stray-direction`, `subgraph-without-id`, `declaration-in-edge`, `edge-id-on-group` and `link-style`. Some of these state a merge as their purpose (`lone-cr` in §3, `declaration-in-edge` in §5.1, `link-style` in §7); the rule acts on the inputs, and there is no clean refused merge to write for it. `no-header` is here too: a statement line above the header would have to come from one side, which would then be `no-header` itself. A conflicted merge leaves `conflict-marker` lines, but carries no verdict here. The line refusals that depend on block context (`statement-in-block`, and in the same way `declaration-in-block`, `nested-block`, `unbalanced-block`, `direction-outside-block` and `direction-twice`) can be reached, and `block-end-moved-over-new-edge` shows one.

`malformed-line` was listed here when the batch was written, and is not one of these: §4.3 rule 10 makes a member line at the top level `malformed-line`, so it depends on block context too. `member-line-left-outside-block`, added in review, is a clean merge refused that way.
