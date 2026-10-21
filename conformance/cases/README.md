# nodespec conformance cases: the blind batch

322 cases: 105 accepted, 217 refused. Each expected outcome was derived
by hand from SPEC.md and is argued in the case's `WHY.md`. No case was run
through Mermaid or through any checker.

## Layout

    cases/<group>/<case-name>/
        input.mmd      the file under test, as exact bytes
        expect.json    what a checker must report
        WHY.md         the SPEC.md sentences that decide it, and the reasoning; ignored by a runner

A directory is a case if and only if it holds `expect.json`. The group name is
a filing convention, not an input.

| group | cases |
| --- | --- |
| `grammar` | 51 |
| `refusal` | 97 |
| `boundary` | 130 |
| `applicability` | 37 |
| `examples` | 7 |

- `grammar`: one accepted file per grammar construct (header forms, each of the
  fourteen shapes, each row of the link table, labels, edge labels, edge ids,
  chains and `&` groups, subgraph lines, member lines, nesting by member line,
  `direction`, `classDef`, `class`, `style`, comments, blank lines, line endings).
- `refusal`: files in which one §9 identifier applies and nothing else.
- `boundary`: twin files on either side of a sharp rule, each named
  `…-accepted` or `…-refused` for its own outcome (since §4.2 rule 3
  refuses any line holding `:::` or `@{`, both twins of some pairs are
  refused). Where a case has a twin, its `WHY.md` names it with the
  measured byte distance; most twins differ by one byte. The pairs that
  cannot are explained below. The group also holds lone boundary cases
  around front matter, conflict markers, edge ids and `styled-twice`.
- `applicability`: §9's rule for which refusals apply: a refused line
  contributes nothing, and checking goes on.
- `examples`: the files of SPEC.md's own worked examples (§4.2, §4.9, §5.4,
  §7, §11), each checked as a single file.

`input.mmd` files are exact bytes. CR, a byte-order mark, invalid UTF-8,
U+00A0 and U+2028 occur only where a case means them, as the structure
script checked. A copy of this tree must not
normalise line endings (`* -text` in `.gitattributes`).

## expect.json

Exactly one of these forms:

    {"accept": true}

    {"refusal": ["<identifier>", ...]}

    {"refusal": ["<identifier>", ...], "ids": {"<identifier>": ["<id>", ...]}}

Either form may also carry `"provisional": "<§12 item>"`: the text of the
§12 bullet whose provisional reading the case pins, verbatim (SPEC.md's line
breaks folded to spaces). Search for it to find every case that a change to
that reading would touch.

- `refusal` lists **every** §9 identifier that applies to the file under
  SPEC.md §9's applicability rule. It is never empty.
- `ids` is present exactly when `refusal` holds an identifier that §9 says is
  reported with an id: `reserved-id`, `duplicate-declaration`,
  `undeclared-id`, `wrong-kind`, `kind-clash`, `edge-id-on-group`,
  `member-twice`, `membership-cycle`, `styled-twice`. For each such
  identifier it lists every id the entry applies to. Other identifiers carry
  no id (§9) and have no `ids` key.

## How a case passes

SPEC.md §9: "a report passes if its identifier, and its id where the entry has
one, are among them", and "which one is reported is not specified".

- An `accept` case passes when the checker accepts the file.
- A `refusal` case passes when the checker refuses the file and reports an
  identifier in `refusal`; and, if that identifier is in `ids`, reports an
  id in `ids[identifier]`. Reporting any one listed identifier is enough.
  Reporting several is allowed only if each would pass on its own.
- A checker that accepts a `refusal` case, refuses an `accept` case, reports
  an identifier not in the list, reports an id not in the list, or reports
  no id for an id-bearing identifier, fails the case.
- Messages are never compared. A checker must be deterministic (§9); running
  a case twice must give the same report.
- `provisional` changes nothing about how a case is judged.

## Provenance

Written from SPEC.md at nodespec 055509e alone, by an author who has not
written a checker and did not read one. Every expected outcome and every
quoted sentence follows SPEC.md at 055509e.

The batch was first written from SPEC.md at nodespec f34b25c, with these three
files and nothing else. 0001 was read for context and rowspec's README for
layout:

| file | sha256 |
| --- | --- |
| `SPEC.md` at f34b25c (nodespec draft 0, approved) | `d2083d5832021a6978b2ea4bb44abf6a2da81bd084d3151fe2c4e7dae64c94b6` |
| `0001-mermaid-profile.md` | `d36989c622cebf87d7491505a5980d2ae64fde28da3ab2ae3651167999ec8a55` |
| `rowspec-cases-README.md` | `45cfe0b46e181acbb2c2320b6e6be75c05f8ae3881e532435ababf9961553c5c` |

It was then re-checked and extended against the amendment, from these two
further files and nothing else:

| file | sha256 |
| --- | --- |
| `SPEC.md` at e7e643e | `4ce5dcd7a19019ad5ce3b5d844a8eb7fac2f02b3e6c3a8ddd4d8fb120f5cc01a` |
| `SPEC-f34b25c-to-e7e643e.diff` | `29cc967826b410a960164e7b4fe972fbf131ccefa4883a85a3c1e02fe6fe618d` |

The amendment changed no expected outcome of a case written from f34b25c. It
changed quoted sentences and §12 tags, and it settled all five questions the
first `AMBIGUITIES.md` listed, which are now cases.

It was re-checked and extended a second time against the next amendment, from
these two further files and nothing else:

| file | sha256 |
| --- | --- |
| `SPEC.md` at bc2cf0b | `677ee943a93cd4fb46784235b973772b78e4762b16c1d9c6732a8c815745d942` |
| `SPEC-e7e643e-to-bc2cf0b.diff` | `5828e58f317e9da3b4d5640a9fabd8921993a18a7a12a892b1897a53c7c74501` |

That amendment changed no expected outcome either. It changed quoted
sentences and one §12 tag. It settled the one ambiguity left at e7e643e (a fence
indented by U+00A0), which is now a set of cases.

A review of the tree then listed rules of SPEC.md at bc2cf0b with no case.
Cases for each were added from the same text. They are additions only, and no
existing case changed.

Last, the tree as committed on main (where the owner's settling of 23
readings had removed their tags) was re-derived against SPEC.md at
374b8a9, the head of nodespec #20, from these two further files and that
tree, and nothing else:

| file | sha256 |
| --- | --- |
| `SPEC.md` at 374b8a9 | `ede423209168994976f194e25e8e34db226d47e230f91646fcaa2f21476cfe73` |
| `SPEC-bc2cf0b-to-374b8a9.diff` | `619939dcd93c3ce23475826677fe10ef7b09b2307ec776b0e412804a0f5b093e` |

The owner's ruling of 2026-10-20 makes any line holding `:::` or `@{`
`not-admitted` (§4.2 rule 3), label text and comments included. Every case
whose input holds either was re-derived: some accepted cases are now
refused and some refusals changed identifiers, each saying so in its
`WHY.md` ("Changed at 374b8a9 from …"), and no input byte changed. Case
names written under the earlier label-text reading kept their names at
first; the `label-text-…-accepted` cases now refused have since been
renamed `…-refused`, and each `WHY.md` says it changed from accepted. Cases
for the ruling itself were added, and every other quote was brought up to
374b8a9's text. Only the three readings still provisional at 374b8a9 tag a
case.

Then the ruling that settled the one question left open at 374b8a9 was
read from these two further files and nothing else:

| file | sha256 |
| --- | --- |
| `SPEC.md` at 055509e | `0ae457bcb6c92c38c0f48e77d3f9999e4415ade5e6b5906a27f47859a348b758` |
| `SPEC-374b8a9-to-055509e.diff` | `c3729377372214dc029d679a864a7e2139df4d624c4edec6bf4337e0603dd6be` |

A comment refused by §4.2 rule 3 for `:::` or `@{` is still exempt from
`stray-direction` (§4.9). No existing outcome changed; four quoted sentences
were brought up to 055509e's text, and cases for the ruling were added.

When the owner then settled the last three provisional readings (nodespec
#22), the last seven `provisional` tags and their seven "Pins the
provisional reading" lines in `WHY.md` were removed, as #19 had removed the
tags of the other 23; no input, outcome or quote changed.

No Mermaid was run, no checker was run or written, and no other file of the
nodespec repository, its reviews or its probes was read. The tree was written
by a generator in which every outcome is hand-written data, and checked by a
structure script; neither is committed here. That script checks only shape: that the
JSON parses and follows this schema, that each `WHY.md` quote is a verbatim
passage of SPEC.md, that provisional tags are §12 bullets, and that special
bytes are where intended. It decides no outcome.

Where SPEC.md was ambiguous or silent on a case the author wanted, the case was
left out and listed in `AMBIGUITIES.md`, beside this file.

## Identifier → cases

"Sole" cases are those in which the identifier is the only refusal.

| identifier | number of sole cases | sole cases | cases with other refusals |
| --- | --- | --- | --- |
| `bad-encoding` | 3 | `refusal/bad-encoding-invalid-byte`<br>`refusal/bad-encoding-encoded-surrogate`<br>`applicability/bad-encoding-stops-leading-bom` | `applicability/leading-bom-bad-encoding-and-lone-cr`<br>`applicability/bad-encoding-and-lone-cr` |
| `leading-bom` | 1 | `refusal/leading-bom` | `applicability/leading-bom-and-front-matter` |
| `lone-cr` | 4 | `refusal/lone-cr`<br>`boundary/lone-cr-at-end-refused`<br>`applicability/lone-cr-stops-checking`<br>`applicability/lone-cr-stops-leading-bom` | `applicability/leading-bom-bad-encoding-and-lone-cr`<br>`applicability/bad-encoding-and-lone-cr` |
| `conflict-marker` | 4 | `refusal/conflict-marker`<br>`applicability/conflict-marker-before-header`<br>`refusal/conflict-marker-pipes`<br>`applicability/conflict-marker-holding-triple-colon` | none |
| `no-header` | 7 | `refusal/no-header-empty-file`<br>`refusal/no-header-first-statement-is-a-node`<br>`refusal/no-header-semicolon`<br>`refusal/no-header-flowchart-elk`<br>`refusal/no-header-lower-case-direction`<br>`boundary/header-unspaced-refused`<br>`boundary/header-capitalised-refused` | `boundary/front-matter-unclosed-refused`<br>`boundary/front-matter-four-dashes-refused`<br>`applicability/no-header-then-lines-read-as-usual`<br>`applicability/comment-with-quote-before-header`<br>`applicability/markdown-fence`<br>`boundary/front-matter-closing-fence-two-dashes-refused`<br>`boundary/front-matter-no-break-space-fences-refused`<br>`boundary/front-matter-no-break-space-fences-with-title-refused`<br>`boundary/front-matter-closed-by-a-no-break-space-fence-refused`<br>`applicability/header-holding-triple-colon` |
| `malformed-line` | 55 | `refusal/malformed-line-inline-edge-label`<br>`refusal/malformed-line-semicolon-after-edge`<br>`refusal/malformed-line-bare-id-at-top-level`<br>`refusal/malformed-line-link-not-admitted`<br>`refusal/malformed-line-head-at-start-only`<br>`refusal/malformed-line-id-with-hyphen`<br>`refusal/malformed-line-id-non-ascii`<br>`refusal/malformed-line-classdef-two-classes`<br>`refusal/malformed-line-class-two-classes`<br>`refusal/malformed-line-style-two-targets`<br>`refusal/malformed-line-style-semicolon`<br>`refusal/malformed-line-style-property-acctitle`<br>`refusal/malformed-line-style-ampersand-in-word`<br>`refusal/malformed-line-end-with-a-word`<br>`refusal/malformed-line-quoted-label-spaced-from-bracket`<br>`refusal/malformed-line-line-separator-in-label`<br>`refusal/malformed-line-whitespace-only-quoted-label`<br>`refusal/malformed-line-label-leading-hyphen`<br>`refusal/malformed-line-at-in-unquoted-label`<br>`refusal/malformed-line-direction-unknown-word`<br>`refusal/malformed-line-second-header`<br>`refusal/malformed-line-member-line-with-ampersand`<br>`boundary/style-word-keyword-hyphen-refused`<br>`boundary/style-unit-v-refused`<br>`boundary/style-name-v-refused`<br>`boundary/style-name-swimlane-beta-refused`<br>`boundary/wsp-missing-after-link-refused`<br>`boundary/wsp-missing-after-ampersand-refused`<br>`boundary/wsp-no-break-space-refused`<br>`boundary/class-line-with-trailing-wsp-refused`<br>`boundary/node-shape-spaced-refused`<br>`boundary/percent-pair-alone-refused`<br>`boundary/comment-equals-quote-refused`<br>`boundary/quoted-label-ending-in-equals-refused`<br>`boundary/unquoted-label-tilde-refused`<br>`boundary/conflict-marker-indented-refused`<br>`boundary/front-matter-not-on-first-line-refused`<br>`applicability/reserved-word-in-malformed-line`<br>`applicability/refused-redeclaration-is-not-duplicate`<br>`applicability/refused-class-line-is-not-styled-twice`<br>`applicability/refused-edge-is-not-duplicate`<br>`applicability/refused-line-after-class-is-not-class-not-last`<br>`applicability/refused-member-line-is-not-member-twice`<br>`refusal/malformed-line-markdown-subgraph-title`<br>`boundary/link-both-headed-too-short-refused`<br>`boundary/link-invisible-too-short-refused`<br>`boundary/link-thick-too-short-refused`<br>`boundary/wsp-missing-before-ampersand-refused`<br>`refusal/malformed-line-subgraph-glued-to-quote`<br>`refusal/malformed-line-style-property-accdescr`<br>`boundary/style-name-v-hyphen-refused`<br>`boundary/style-name-swimlane-beta-hyphen-refused`<br>`boundary/style-words-tab-separated-refused`<br>`boundary/style-colour-non-hex-refused`<br>`refusal/malformed-line-del-in-comment` | `boundary/subgraph-id-with-trailing-wsp-refused`<br>`boundary/subgraph-title-with-trailing-wsp-refused`<br>`boundary/front-matter-four-dashes-refused`<br>`applicability/refused-subgraph-line-opens-no-block`<br>`applicability/stray-direction-inside-an-id`<br>`applicability/reserved-subgraph-id-opens-no-block`<br>`applicability/comment-with-quote-before-header`<br>`applicability/accdescr-block-lines-read-one-by-one`<br>`applicability/markdown-fence`<br>`applicability/no-break-space-after-direction-at-line-end`<br>`boundary/subgraph-two-spaces-before-id-trailing-wsp-refused`<br>`boundary/front-matter-no-break-space-fences-refused`<br>`boundary/front-matter-no-break-space-fences-with-title-refused`<br>`boundary/label-text-triple-colon-in-unquoted-title-refused`<br>`boundary/label-text-triple-colon-title-with-trailing-wsp-refused`<br>`boundary/label-text-at-brace-in-quoted-title-refused`<br>`boundary/label-text-at-brace-in-unquoted-title-refused` |
| `not-admitted` | 40 | `refusal/not-admitted-directive`<br>`refusal/not-admitted-click`<br>`refusal/not-admitted-acctitle`<br>`refusal/not-admitted-accdescr`<br>`refusal/not-admitted-triple-colon`<br>`refusal/not-admitted-at-brace`<br>`boundary/markdown-string-refused`<br>`boundary/front-matter-closed-refused`<br>`boundary/front-matter-indented-with-trailing-wsp-refused`<br>`examples/s4-2-directive-in-comment-refused`<br>`boundary/front-matter-holding-direction-phrase-refused`<br>`refusal/malformed-line-triple-colon-in-style`<br>`refusal/malformed-line-triple-colon-in-class`<br>`refusal/link-style-holding-triple-colon`<br>`refusal/not-admitted-triple-colon-in-block`<br>`boundary/front-matter-one-fence-indented-refused`<br>`boundary/front-matter-both-fences-tab-indented-refused`<br>`boundary/label-text-triple-colon-in-unquoted-node-label-refused`<br>`boundary/label-text-triple-colon-node-with-trailing-text-refused`<br>`boundary/label-text-triple-colon-node-then-word-refused`<br>`boundary/label-text-triple-colon-in-quoted-node-label-refused`<br>`boundary/label-text-at-brace-in-quoted-node-label-refused`<br>`boundary/label-text-at-brace-in-quoted-node-label-unclosed-refused`<br>`boundary/label-text-at-brace-in-unquoted-node-label-refused`<br>`boundary/label-text-triple-colon-in-unquoted-edge-label-refused`<br>`boundary/label-text-triple-colon-edge-label-unspaced-refused`<br>`boundary/label-text-at-brace-in-quoted-edge-label-refused`<br>`boundary/label-text-at-brace-in-unquoted-edge-label-refused`<br>`boundary/markdown-string-in-edge-label-refused`<br>`refusal/not-admitted-acctitle-spaced-colon`<br>`boundary/comment-holding-triple-colon-refused`<br>`boundary/comment-before-header-holding-at-brace-refused`<br>`boundary/style-holding-triple-colon-refused`<br>`applicability/front-matter-holding-triple-colon`<br>`applicability/triple-colon-comment-after-class-line`<br>`applicability/triple-colon-comment-with-direction-phrase`<br>`boundary/comment-triple-colon-with-direction-phrase-refused`<br>`boundary/comment-at-brace-ending-in-direction-refused`<br>`boundary/comment-triple-colon-and-percent-brace-gap-with-direction-phrase-refused`<br>`boundary/comment-equals-space-quote-triple-colon-with-direction-phrase-refused` | `boundary/front-matter-unclosed-refused`<br>`applicability/leading-bom-and-front-matter`<br>`applicability/accdescr-block-lines-read-one-by-one`<br>`applicability/directive-holding-direction-phrase`<br>`applicability/direction-phrase-before-directive-in-label`<br>`boundary/front-matter-closing-fence-two-dashes-refused`<br>`boundary/front-matter-closed-by-a-no-break-space-fence-refused`<br>`boundary/label-text-triple-colon-in-unquoted-title-refused`<br>`boundary/label-text-triple-colon-title-with-trailing-wsp-refused`<br>`boundary/label-text-at-brace-in-quoted-title-refused`<br>`boundary/label-text-at-brace-in-unquoted-title-refused`<br>`applicability/directive-looking-like-comment-unclosed`<br>`applicability/directive-looking-like-comment-ending-in-direction`<br>`applicability/header-holding-triple-colon`<br>`applicability/stray-direction-with-triple-colon-in-label`<br>`boundary/single-percent-triple-colon-with-direction-phrase-refused`<br>`boundary/comment-triple-colon-and-percent-brace-with-direction-phrase-refused`<br>`boundary/comment-equals-quote-triple-colon-with-direction-phrase-refused` |
| `reserved-id` | 9 | `refusal/reserved-id-named-in-edge`<br>`refusal/reserved-id-default-class`<br>`refusal/reserved-id-hasownproperty`<br>`refusal/reserved-id-direction`<br>`boundary/reserved-word-end-as-node-refused`<br>`boundary/l-form-digit-tail-refused`<br>`boundary/class-named-node-refused`<br>`boundary/l-form-underscore-in-part-refused`<br>`refusal/reserved-id-underscore-top` | `applicability/reserved-subgraph-id-opens-no-block` |
| `stray-direction` | 5 | `refusal/stray-direction-no-break-space`<br>`boundary/stray-direction-in-label-refused`<br>`boundary/stray-direction-line-ends-in-direction-refused`<br>`applicability/stray-direction-suppresses-reserved-id`<br>`refusal/stray-direction-td` | `applicability/stray-direction-with-declaration-in-edge`<br>`applicability/stray-direction-inside-an-id`<br>`examples/s4-9-member-line-ending-in-direction-refused`<br>`applicability/directive-holding-direction-phrase`<br>`applicability/direction-phrase-before-directive-in-label`<br>`applicability/no-break-space-after-direction-at-line-end`<br>`applicability/directive-looking-like-comment-unclosed`<br>`applicability/directive-looking-like-comment-ending-in-direction`<br>`applicability/stray-direction-with-triple-colon-in-label`<br>`boundary/single-percent-triple-colon-with-direction-phrase-refused`<br>`boundary/comment-triple-colon-and-percent-brace-with-direction-phrase-refused`<br>`boundary/comment-equals-quote-triple-colon-with-direction-phrase-refused` |
| `subgraph-without-id` | 4 | `refusal/subgraph-without-id-title-words`<br>`refusal/subgraph-without-id-alone`<br>`refusal/subgraph-without-id-quoted-title`<br>`refusal/subgraph-without-id-id-holding-a-space` | `boundary/subgraph-id-with-trailing-wsp-refused`<br>`applicability/refused-subgraph-line-opens-no-block`<br>`boundary/subgraph-two-spaces-before-id-trailing-wsp-refused` |
| `declaration-in-edge` | 2 | `refusal/declaration-in-edge`<br>`refusal/declaration-in-edge-with-edge-id-on-group` | `applicability/declaration-in-edge-declares-nothing`<br>`applicability/stray-direction-with-declaration-in-edge` |
| `duplicate-declaration` | 4 | `refusal/duplicate-declaration-node`<br>`refusal/duplicate-declaration-subgraph`<br>`refusal/duplicate-declaration-edge-id`<br>`refusal/duplicate-declaration-class` | none |
| `undeclared-id` | 2 | `refusal/undeclared-id-edge-end`<br>`examples/s5-4-merged-refused` | `applicability/declaration-in-edge-declares-nothing`<br>`applicability/declaration-in-block-declares-nothing`<br>`applicability/no-header-then-lines-read-as-usual`<br>`applicability/edge-id-on-group-declares-nothing`<br>`examples/s4-9-member-line-ending-in-direction-refused`<br>`boundary/front-matter-no-break-space-fences-refused` |
| `wrong-kind` | 6 | `refusal/wrong-kind-style-on-edge-id`<br>`refusal/wrong-kind-class-names-a-node`<br>`refusal/wrong-kind-edge-to-class`<br>`refusal/wrong-kind-member-line-names-edge-id`<br>`refusal/wrong-kind-edge-to-edge-id`<br>`refusal/wrong-kind-style-on-class` | none |
| `kind-clash` | 3 | `refusal/kind-clash-node-and-subgraph`<br>`refusal/kind-clash-node-and-class`<br>`refusal/kind-clash-node-and-edge-id` | none |
| `edge-id-on-group` | 2 | `refusal/edge-id-on-group`<br>`refusal/edge-id-on-group-after-the-link` | `applicability/edge-id-on-group-declares-nothing` |
| `duplicate-edge` | 5 | `refusal/duplicate-edge-repeated-id-in-group`<br>`boundary/duplicate-edge-same-link-refused`<br>`boundary/duplicate-edge-label-padding-refused`<br>`examples/s11-unnamed-edge-added-twice-merged-refused`<br>`boundary/duplicate-edge-label-tab-padding-refused` | none |
| `too-many-edges` | 1 | `boundary/too-many-edges-501-refused` | none |
| `declaration-in-block` | 1 | `refusal/declaration-in-block` | `applicability/declaration-in-block-declares-nothing` |
| `statement-in-block` | 5 | `refusal/statement-in-block-edge`<br>`refusal/statement-in-block-style`<br>`refusal/statement-in-block-bare-classdef`<br>`refusal/statement-in-block-edge-decl`<br>`refusal/statement-in-block-with-edge-id-on-group` | none |
| `nested-block` | 1 | `refusal/nested-block` | `applicability/nested-block-opens-no-block` |
| `unbalanced-block` | 2 | `refusal/unbalanced-block-end-at-top-level`<br>`refusal/unbalanced-block-unclosed-at-end-of-file` | `boundary/subgraph-id-with-trailing-wsp-refused`<br>`boundary/subgraph-title-with-trailing-wsp-refused`<br>`applicability/refused-subgraph-line-opens-no-block`<br>`applicability/nested-block-opens-no-block`<br>`applicability/reserved-subgraph-id-opens-no-block`<br>`boundary/subgraph-two-spaces-before-id-trailing-wsp-refused`<br>`boundary/label-text-triple-colon-in-unquoted-title-refused`<br>`boundary/label-text-triple-colon-title-with-trailing-wsp-refused`<br>`boundary/label-text-at-brace-in-quoted-title-refused`<br>`boundary/label-text-at-brace-in-unquoted-title-refused` |
| `member-twice` | 2 | `refusal/member-twice-two-blocks`<br>`refusal/member-twice-one-block` | none |
| `membership-cycle` | 2 | `refusal/membership-cycle-two-subgraphs`<br>`refusal/membership-cycle-of-one` | none |
| `direction-outside-block` | 1 | `refusal/direction-outside-block` | none |
| `direction-twice` | 2 | `refusal/direction-twice`<br>`refusal/direction-twice-three-statements` | none |
| `link-style` | 1 | `refusal/link-style` | none |
| `class-not-last` | 2 | `boundary/class-not-last-refused`<br>`examples/s7-class-before-style-refused` | none |
| `styled-twice` | 2 | `refusal/styled-twice-style`<br>`refusal/styled-twice-class` | none |

Identifiers without a sole case: none. Every identifier has at least one case in which it is the only refusal.

## Boundary pairs that cannot differ by one byte

- **Front matter.** Front matter is a first line of `---`, with optional
  `WSP` (§4.2 rule 1). An accepted file one byte away would need a first line
  that becomes blank, a comment or a header with one byte changed. A comment
  needs `%%`, a header needs `flowchart` or `graph`, and `---` cannot become
  blank in one byte. Prefixing an LF moves `---` to line 2, where it is the
  first statement line and `no-header`. So the front-matter cases in
  `boundary/` contrast refusals (`not-admitted` against `no-header` and
  `malformed-line`), and none of them has an accepted twin.
- **`class-not-last`.** The accepted and refused twins hold the same lines,
  with one edge statement moved past the `class` line. A one-byte edit that
  turns a blank line, a comment or a `class` line into a statement line that
  is not refused does not exist. A comment loses its `%%` only with two
  bytes, `%%` alone is `malformed-line`, and a comment holding `="` is
  `malformed-line`. Refused lines do not count (§9).
- **`too-many-edges`.** 500 against 501 edges differ by one edge statement
  line, `n500 --> n0`. Adding an edge takes at least a link, `WSP` and an id,
  and a comment cannot become an edge statement in one byte.
- **Other pairs that are not one byte apart.** The label pair for
  `duplicate-edge` is two bytes apart, because the accepted side pins the
  quoted label `|"x"|`. The `~~~` pair is two, because it adds the quotes. The
  U+00A0 case is one character, two bytes, from its spaced twin. Each
  `WHY.md` gives the measured distance.

## Provisional readings pinned

None. The owner settled every provisional reading on 2026-10-20 (SPEC.md
§12, *Settled by the owner*), and no case carries a tag. The label-text
reading was replaced by the owner's ruling on `:::` and `@{`.
