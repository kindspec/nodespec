# boundary/style-words-tab-separated-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/style-words-space-separated-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c stroke-dasharray:5⟨TAB⟩5
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

§4.1:

> classdef-stmt = *WSP "classDef" 1*WSP id 1*WSP style-list *WSP

## Reasoning

Words are separated by `SP` only, not `WSP`. The tab is not trailing (`5` follows it), so `classdef-stmt`'s final `*WSP` cannot take it either.

## Other identifiers

- No other identifier is a near miss for this file.
