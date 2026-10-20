# refusal/malformed-line-line-separator-in-label

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[x⟨U+2028⟩y]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> U+2028 and U+2029 are left out of every character class: Mermaid's comment stripper reads each as a line end, so `a[x<U+2028>%% y]` loses the rest of its line. A line holding either matches no production.

## Reasoning

U+2028 is in no character class, so the line matches no production. It does not end a line: only LF and CR LF do.

## Other identifiers

- `bad-encoding`: E2 80 A8 is well-formed UTF-8.
- `lone-cr`: There is no CR.
