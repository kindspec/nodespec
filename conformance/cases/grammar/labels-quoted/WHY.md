# grammar/labels-quoted

**Expected:** accepted.

## Input

````text
flowchart TD
a["with [brackets] (parens) {braces} |pipes|"]
b["a@b"]
c[" padded "]
d{"Is it?"}
e(["semi;colon"])
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> A quoted label is `"`, then text without `"`, then `"`, with nothing between the quotes and the delimiters around them. The text holds a character that is not `WSP`, and:

§4.1:

> qchar = HTAB / %x20-21 / %x23-7E / nonascii ; not "

§4.5:

> `@` is left out of unquoted labels because Mermaid reads a run of characters ending in `@` as an edge id, so `n[a@b]` does not parse; quoted, `n["a@b"]` does.

§4.1:

> a `quoted` label holds at least one character that is not `WSP`, does not begin with `` ` ``, and does not end with `=` (§4.5);

## Reasoning

Each label is `DQUOTE 1*qchar DQUOTE` with the quotes directly against the shape's delimiters. `qchar` is every printable ASCII character but `"`, so brackets, parens, braces, pipes and `@` are allowed; `n["a@b"]` is §4.5's own example. Every text holds a non-`WSP` character, none begins with a backtick, and none ends with `=`.
