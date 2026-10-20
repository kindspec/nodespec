# refusal/no-header-lower-case-direction

**Expected:** refused. Identifiers that apply: `no-header`.

## Input

````text
flowchart td
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A header in another case (`Flowchart`), with another direction (`td`, `<`, `v`), with `flowchart-elk`, or with a `;` after it does not match. The direction is optional, as in the spike's subset (provisional).

§4.1:

> String literals are case-sensitive, as RFC 7405's `%s` prefix marks them; this document leaves the prefix out for readability.

§4.1:

> dir = "TB" / "TD" / "BT" / "LR" / "RL"

## Reasoning

`td` is not one of the case-sensitive `dir` literals, and the header has no other way to take the text after the keyword, so the line does not match `header`.

## Other identifiers

- `malformed-line`: The first statement line is judged only by the header rule.
