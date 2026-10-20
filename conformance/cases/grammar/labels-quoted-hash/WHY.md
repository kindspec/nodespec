# grammar/labels-quoted-hash

**Expected:** accepted.

## Input

````text
flowchart TD
a["#1 and #35;"]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A quoted label is `"`, then text without `"`, then `"`, with nothing between the quotes and the delimiters around them. The text holds a character that is not `WSP`, and:

§4.1:

> qchar = HTAB / %x20-21 / %x23-7E / nonascii ; not "

## Reasoning

`#` and `;` are `qchar`s; the label is quoted text.
