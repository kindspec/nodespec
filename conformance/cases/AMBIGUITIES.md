# Cases left out: where SPEC.md does not decide

An entry here is a file the blind batch wanted to write but could not,
because SPEC.md supports two readings of it with different expected outcomes.

**Open entries at nodespec 055509e: none.** Every question raised so far has
been settled by an amendment and is now a set of cases:

| question | raised at | settled at | by | cases |
| --- | --- | --- | --- | --- |
| `L_` form with consecutive underscores | f34b25c | e7e643e | §4.4: `_` included | `boundary/l-form-underscore-in-part-refused`, `boundary/l-form-underscore-in-part-non-digit-tail-accepted` |
| `stray-direction` on a front-matter line | f34b25c | e7e643e | §4.9: front matter exempt | `boundary/front-matter-holding-direction-phrase-refused` |
| `stray-direction` on a directive line | f34b25c | e7e643e | §4.9: directives not exempt | `applicability/directive-holding-direction-phrase`, `applicability/direction-phrase-before-directive-in-label` |
| case of the direction words | f34b25c | e7e643e | §4.9: compare exactly | `boundary/stray-direction-lower-case-second-letter-accepted`, `boundary/stray-direction-capital-d-accepted`, `boundary/stray-direction-lower-case-direction-word-accepted` |
| more than one `WSP` after `subgraph` | f34b25c | e7e643e | §4.7: the whole run | `boundary/subgraph-two-spaces-before-id-accepted`, `boundary/subgraph-tab-and-space-before-id-accepted`, `boundary/subgraph-two-spaces-before-id-trailing-wsp-refused` |
| a front-matter fence indented by U+00A0 | e7e643e | bc2cf0b | §4.2: not a fence | `boundary/front-matter-no-break-space-fences-refused`, `boundary/front-matter-no-break-space-fences-with-title-refused`, `boundary/front-matter-closed-by-a-no-break-space-fence-refused` |
| a comment line holding `:::` or `@{` and a direction phrase | 374b8a9 | 055509e | §4.9: such a comment is exempt | `applicability/triple-colon-comment-with-direction-phrase`, `boundary/comment-triple-colon-with-direction-phrase-refused`, `boundary/comment-at-brace-ending-in-direction-refused`, `boundary/single-percent-triple-colon-with-direction-phrase-refused` |

No ambiguity is open after re-checking the tree against 055509e. The rules a
later review found without a case were each decided by SPEC.md, and are cases.
