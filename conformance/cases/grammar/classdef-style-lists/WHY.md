# grammar/classdef-style-lists

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
classDef hot fill:#f96,stroke:#333,stroke-width:4px,color:#FFF
classDef cool fill: #9cf,font-family:Arial sans-serif,font-size:12px
classDef dim opacity:.5,width:50%,height:100vh,margin:-1.5em
classDef loud color:red !important,stroke-dasharray:5 5⟨SP⟩
class a hot
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> classdef-stmt = *WSP "classDef" 1*WSP id 1*WSP style-list *WSP

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

§4.8:

> The grammar admits CSS-like items: a name, `:`, and words that are a colour (`#f9f`), a number with an optional unit and `%` (`4px`, `.5`, `50%`, `100vh`), or a name (`Arial`, `sans-serif`, `!important`).

§4.8:

> A `class` line ends at its class id: Mermaid refuses `WSP` after it. `classDef` and `style` lines may end in `WSP`, which Mermaid keeps in the last style.

## Reasoning

Each item is `name ":" *SP value`. The words are colours (`#f96`, `#FFF`), numbers with and without a unit or `%` (`4px`, `.5`, `50%`, `100vh`, `-1.5em`, `5`), and names (`Arial`, `sans-serif`, `red`, `!important`). `fill: #9cf` uses `*SP`. Values of two words use `1*SP`. The last `classDef` ends in a space, which `classdef-stmt`'s `*WSP` admits. No name, nor its part before a `-`, is `v` or one of the 17 words, and no unit is `v`. Unused classes are allowed: no rule asks that a class be assigned.
