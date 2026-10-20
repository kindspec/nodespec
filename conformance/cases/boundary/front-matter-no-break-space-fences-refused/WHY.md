# boundary/front-matter-no-break-space-fences-refused

**Expected:** refused. Identifiers that apply: `no-header`; `malformed-line`; `undeclared-id` (id `a`, `b`).

A report of any one of these passes, with one of its ids where it has them (§9).

## Input

````text
⟨U+00A0⟩---
⟨U+00A0⟩---
flowchart TD
a --> b
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A line indented by anything other than `WSP`, such as U+00A0, is not a fence here: it is the first statement line, so the file is `no-header`, and the lines after it, the closing fence included, are read under §4.3 as after any `no-header` line (§9). With a U+00A0 before each fence, the file `---`, `---`, `flowchart TD`, `a --> b` is `no-header` (the first fence), `malformed-line` (the second fence and the header) and `undeclared-id` for `a` and `b`.

§3:

> `WSP` is a space (U+0020) or a tab (U+0009), and nothing else. Other whitespace characters, such as U+00A0, never match `WSP`.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place.

## Reasoning

§4.2's own example, byte for byte as it describes it. The first U+00A0 fence is the first statement line: `no-header`. The second fence and `flowchart TD` are statement lines matching nothing: `malformed-line`. `a --> b` is an ordinary edge statement naming two ids nothing declares.

## Other identifiers

- `not-admitted`: A line indented by U+00A0 is not a fence, so there is no front matter.
- `stray-direction`: No `direction`.
