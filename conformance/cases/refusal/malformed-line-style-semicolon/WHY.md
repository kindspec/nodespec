# refusal/malformed-line-style-semicolon

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
classDef c fill:#f9f;stroke:#333
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> `;` is not admitted anywhere outside a label (the owner, 2026-10-19: refused for now), so a statement line ending in `;`, two statements on one line, and a member line `a;` are `malformed-line`, and a header ending in `;` is `no-header`.

§4.3:

> in a `classDef` or a `style`, after a `#` colour, `fill:#f9f;stroke:#333` joins two styles into one, and after a name word, `fill:red;stroke:blue` ends the statement and makes a node named `stroke:blue`.

§4.1:

> style-list = style-item *( "," style-item ) ; §4.8 style-item = name ":" *SP value value = word *( 1*SP word ) word = colour / number / [ "!" ] name colour = "#" 1*HEXDIG number = ( [ "-" ] 1*DIGIT [ "." 1*DIGIT ] / "." 1*DIGIT ) [ unit ] [ "%" ] unit = 1*%x61-7A name = ALPHA *( ALPHA / DIGIT / "_" ) *( "-" 1*( ALPHA / DIGIT / "_" ) )

## Reasoning

`;` is not admitted outside a label, and no `style-list` production holds it.

## Other identifiers

- `not-admitted`: `;` is a `malformed-line` form (§4.10).
