# refusal/malformed-line-quoted-label-spaced-from-bracket

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[ "x" ]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A quoted label is `"`, then text without `"`, then `"`, with nothing between the quotes and the delimiters around them. The text holds a character that is not `WSP`, and:

§4.5:

> An unquoted label has at least one character that is not `WSP`; its first such character is not `-`, `/` or `\`, since `(-`, `[/` and `[\` open other shapes; it holds none of `[ ] ( ) { } | " @`; and it holds no `~~~`.

## Reasoning

A quoted label has nothing between its quotes and the shape's delimiters, and an unquoted label holds no `"`.

## Other identifiers

- `not-admitted`: The `"` is followed by `x`, not a backtick.
