# refusal/malformed-line-at-in-unquoted-label

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
n[a@b]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> `@` is left out of unquoted labels because Mermaid reads a run of characters ending in `@` as an edge id, so `n[a@b]` does not parse; quoted, `n["a@b"]` does.

§4.5:

> An unquoted label has at least one character that is not `WSP`; its first such character is not `-`, `/` or `\`, since `(-`, `[/` and `[\` open other shapes; it holds none of `[ ] ( ) { } | " @`; and it holds no `~~~`.

## Reasoning

`@` is left out of unquoted labels; the line holds no `@{`, so §4.2 rule 3 does not apply, and no `"` then a backtick, so §4.3 rule 11 does not.

## Other identifiers

- `not-admitted`: There is no `@{`.
