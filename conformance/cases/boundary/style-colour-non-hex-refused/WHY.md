# boundary/style-colour-non-hex-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/style-colour-hex-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
classDef c fill:#xbc
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> colour = "#" 1*HEXDIG

§4.1:

> `HEXDIG` is `DIGIT` or `A` to `F` in either case.

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

## Reasoning

`x` is not a `HEXDIG`, and a `word` beginning with `#` can only be a colour.

## Other identifiers

- No other identifier is a near miss for this file.
