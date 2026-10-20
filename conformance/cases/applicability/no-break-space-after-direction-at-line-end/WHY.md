# applicability/no-break-space-after-direction-at-line-end

**Expected:** refused. Identifiers that apply: `malformed-line`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
flowchart TD
xdirection⟨U+00A0⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> with trailing whitespace removed, it ends in `direction`.

§4.9:

> Here, in both clauses, a whitespace character is any of U+0009 to U+000D, U+0020, U+00A0, U+1680, U+2000 to U+200A, U+2028, U+2029, U+202F, U+205F, U+3000 and U+FEFF, which is what Mermaid's lexer counts; U+00A0 between the words swallows the line as a space does.

§3:

> `WSP` is a space (U+0020) or a tab (U+0009), and nothing else. Other whitespace characters, such as U+00A0, never match `WSP`.

## Reasoning

With trailing whitespace removed, counting U+00A0 as whitespace as §4.9's set does, the line ends in `direction`. U+00A0 is not `WSP` and not an id character, so the line also matches no production and is `malformed-line` at the top level.

## Other identifiers

- `reserved-id`: No reserved word; and the line is refused for other reasons.
