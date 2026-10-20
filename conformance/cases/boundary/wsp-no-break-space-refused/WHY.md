# boundary/wsp-no-break-space-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/wsp-around-link-accepted`, which differs from this file by 2 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a⟨U+00A0⟩--> b
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§3:

> `WSP` is a space (U+0020) or a tab (U+0009), and nothing else. Other whitespace characters, such as U+00A0, never match `WSP`.

## Reasoning

U+00A0 is never `WSP`, so `a` is not followed by the `WSP` a link needs.

## Other identifiers

- `stray-direction`: No `direction`.
