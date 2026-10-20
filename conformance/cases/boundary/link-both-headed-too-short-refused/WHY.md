# boundary/link-both-headed-too-short-refused

**Expected:** refused. Identifiers that apply: `malformed-line`.

**Twin:** `boundary/link-both-headed-shortest-accepted`, which differs from this file by 1 byte edit (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
b[B]
a <-> b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> link = 2*"-" ">" / 3*"-" / 2*"-" "o" / 2*"-" "x" / "<" 2*"-" ">" / "o" 2*"-" "o" / "x" 2*"-" "x" / "-" 1*"." "->" / "-" 1*"." "-" / 2*"=" ">" / 3*"=" / 3*"~"

§4.10:

> Other forms Mermaid accepts and this grammar does not, such as `;`, `-- text -->`, the other links, other ids, `classDef c1,c2` and `class a c1,c2`, are `malformed-line`.

## Reasoning

`<->` is no alternative of `link`: `"<" 2*"-" ">"` needs two `-`. No other production matches.

## Other identifiers

- `not-admitted`: Not a §4.10 form.
- `undeclared-id`: The refused line names nothing.
