# refusal/malformed-line-label-leading-hyphen

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[-x]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> An unquoted label has at least one character that is not `WSP`; its first such character is not `-`, `/` or `\`, since `(-`, `[/` and `[\` open other shapes; it holds none of `[ ] ( ) { } | " @`; and it holds no `~~~`.

§4.1:

> lead = %x21 / %x23-27 / %x2A-2C / %x2E / %x30-3F / %x41-5A / %x5E-7A / %x7E / nonascii ; an lchar that is not WSP, - / or \

## Reasoning

An unquoted label's first non-`WSP` character may not be `-`.

## Other identifiers

- `not-admitted`: No `:::`, `@{` or `"` followed by a backtick.
