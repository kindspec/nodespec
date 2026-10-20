# grammar/ids-ascii-forms

**Expected:** accepted.

## Input

````text
flowchart TD
_[U]
9[N]
a_B9[M]
constructor[C]
__proto__[P]
toString[T]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> id = 1*( ALPHA / DIGIT / "_" )

§4.4:

> An id is one or more ASCII letters, digits and underscores. Mermaid accepts more, including `-`, `.` and non-ASCII letters; the profile does not.

§4.4:

> The other names of JavaScript's `Object.prototype` (`constructor`, `toString`, `__proto__` and the rest) parse in every position, in that one included.

§4.4:

> end graph flowchart subgraph style class classDef click linkStyle interpolate call href default _self _blank _parent _top

## Reasoning

An id is one or more ASCII letters, digits and underscores, so `_`, `9` and `a_B9` are ids. None is a listed reserved word, `hasOwnProperty`, `direction` or of the `L_…_…_N` form. §4.4 names `constructor`, `toString` and `__proto__` as parsing in every position, and they are not reserved.
