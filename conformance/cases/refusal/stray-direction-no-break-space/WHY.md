# refusal/stray-direction-no-break-space

**Expected:** refused. Identifiers that apply: `stray-direction`.

## Input

````text
flowchart TD
a[go direction⟨U+00A0⟩LR]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> Here, in both clauses, a whitespace character is any of U+0009 to U+000D, U+0020, U+00A0, U+1680, U+2000 to U+200A, U+2028, U+2029, U+202F, U+205F, U+3000 and U+FEFF, which is what Mermaid's lexer counts; U+00A0 between the words swallows the line as a space does.

## Reasoning

U+00A0 is a whitespace character for this rule, so the line holds `direction`, whitespace, `LR`. The line also matches `node-stmt` (U+00A0 is an `lchar`), but it is refused, so it declares nothing; and nothing names `a`.

## Other identifiers

- `malformed-line`: The line matches `node-stmt`.
- `reserved-id`: `a` is not reserved.
