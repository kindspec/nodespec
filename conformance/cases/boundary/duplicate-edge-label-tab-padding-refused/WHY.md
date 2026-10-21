# boundary/duplicate-edge-label-tab-padding-refused

**Expected:** refused. Identifiers that apply: `duplicate-edge`.

## Input

````text
flowchart TD
a[A]
b[B]
a -->|x| b
a -->|x⟨TAB⟩| b
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> The same link means the same characters (`-->` and `--->` differ); the same label means both have none, or both have one whose text between the `|`s is the same once leading and trailing `WSP` is removed (provisional). Labels are compared as bytes, not as what they render, so `|x|` and `|"x"|` are different labels and those two edges are not duplicates;

§3:

> `WSP` is a space (U+0020) or a tab (U+0009), and nothing else. Other whitespace characters, such as U+00A0, never match `WSP`.

## Reasoning

A tab is `WSP`, so `x` followed by a tab is `x` once trailing `WSP` is removed.

## Other identifiers

- `malformed-line`: `x` then a tab is an unquoted label (HTAB is an `lchar`).
