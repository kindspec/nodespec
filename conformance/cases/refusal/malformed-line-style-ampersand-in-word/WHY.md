# refusal/malformed-line-style-ampersand-in-word

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Pins the provisional reading (§12):** Style lists are narrower than Mermaid's (§4.8).

## Input

````text
flowchart TD
a[A]
classDef c fill:a&b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> `&`, `*` and `::` inside a word do parse, and are still not admitted. `;` is not admitted (§4.3).

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

## Reasoning

`&` inside a word is not admitted, and `name` holds no `&`.

## Other identifiers

- `not-admitted`: §4.8's "not admitted" is prose; the line is refused by rule 4 because `classdef-stmt` does not match. Rule 11 looks for `:::`, `@{` and `"` then a backtick; none is here.
