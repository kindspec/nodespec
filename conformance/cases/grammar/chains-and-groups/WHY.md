# grammar/chains-and-groups

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
c[C]
d[D]
e[E]
a & b --> c & d
c --> e --> a
d & e -.- b
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> An edge statement is a group of ids, then one or more links, each followed by a group. A link may carry an edge id directly before it, `a e1@--> b`, and a label directly after it, `a -->|yes| b`.

§4.1:

> group = id *( 1*WSP "&" 1*WSP id )

§4.6:

> Each link makes one edge from every id of the group before it to every id of the group after it, in that order: `a & b --> c & d` makes four edges, and `a --> b --> c` makes two. The edges of a file are a list, not a set: `a & a --> b` makes two edges from `a` to `b`, and Mermaid keeps both.

§4.6:

> Two edges without edge ids that have the same start, the same end, the same link and the same label are refused as `duplicate-edge` (the owner, 2026-10-19).

## Reasoning

`a & b --> c & d` makes four edges (a→c, a→d, b→c, b→d); `c --> e --> a` makes c→e and e→a; `d & e -.- b` makes d→b and e→b. Those eight differ in start, end or link, so none is a duplicate, and eight is far below 500.
