# refusal/no-header-flowchart-elk

**Expected:** refused. Identifiers that apply: `no-header`.

**Pins the provisional reading (§12):** After a `no-header` line, the lines that follow are read as if a header stood there; the header's direction is optional; and `flowchart-elk` is not admitted (§4.3).

## Input

````text
flowchart-elk TD
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A header in another case (`Flowchart`), with another direction (`td`, `<`, `v`), with `flowchart-elk`, or with a `;` after it does not match. The direction is optional, as in the spike's subset (provisional).

§4.3:

> `flowchart-elk` is not admitted (provisional).

## Reasoning

`flowchart-elk` is not `flowchart` or `graph` followed by `WSP` or the end of the line, so the line does not match `header`.

## Other identifiers

- `not-admitted`: Not one of §4.10's forms; §4.3 names this a header that does not match.
