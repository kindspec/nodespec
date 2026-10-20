# Cases left out: where SPEC.md does not decide

An entry here is a file the blind batch wanted to write but could not,
because SPEC.md supports two readings of it with different expected outcomes.

**Open entries at nodespec bc2cf0b: none.** Each question raised so far has
been settled by an amendment and is now a set of cases:

| question | raised at | settled at | by | cases |
| --- | --- | --- | --- | --- |
| `L_` form with consecutive underscores | f34b25c | e7e643e | §4.4: `_` included | `boundary/l-form-underscore-in-part-refused`, `boundary/l-form-underscore-in-part-non-digit-tail-accepted` |
| `stray-direction` on a front-matter line | f34b25c | e7e643e | §4.9: front matter exempt | `boundary/front-matter-holding-direction-phrase-refused` |
| `stray-direction` on a directive line | f34b25c | e7e643e | §4.9: directives not exempt | `applicability/directive-holding-direction-phrase`, `applicability/direction-phrase-before-directive-in-label` |
| case of the direction words | f34b25c | e7e643e | §4.9: compare exactly | `boundary/stray-direction-lower-case-second-letter-accepted`, `boundary/stray-direction-capital-d-accepted`, `boundary/stray-direction-lower-case-direction-word-accepted` |
| more than one `WSP` after `subgraph` | f34b25c | e7e643e | §4.7: the whole run | `boundary/subgraph-two-spaces-before-id-accepted`, `boundary/subgraph-tab-and-space-before-id-accepted`, `boundary/subgraph-two-spaces-before-id-trailing-wsp-refused` |
| a front-matter fence indented by U+00A0 | e7e643e | bc2cf0b | §4.2: not a fence | `boundary/front-matter-no-break-space-fences-refused`, `boundary/front-matter-no-break-space-fences-with-title-refused`, `boundary/front-matter-closed-by-a-no-break-space-fence-refused` |

No new ambiguity was found in re-checking the tree against bc2cf0b, nor in
the rules a later review found without a case: SPEC.md decides each of those,
and each is now a case.
