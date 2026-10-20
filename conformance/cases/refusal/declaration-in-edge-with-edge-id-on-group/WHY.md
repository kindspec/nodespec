# refusal/declaration-in-edge-with-edge-id-on-group

**Expected:** refused. Identifiers that apply: `declaration-in-edge`.

## Input

````text
flowchart TD
b[B]
c[C]
a[A] & b e1@--> c
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.6:

> `edge-id-on-group` applies only to a line that §4.3 classifies as an edge statement (rule 8, at the top level). A line refused as `declaration-in-edge` or `statement-in-block` is not also `edge-id-on-group`, since §4.2 reads a classified line as nothing else.

§4.3:

> Matches `edge-decl`: in a block, `statement-in-block`; at the top level, `declaration-in-edge`.

§4.1:

> edge-decl = *WSP dgroup 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP dgroup ) *WSP dgroup = dend *( 1*WSP "&" 1*WSP dend ) dend = id [ shape ]

## Reasoning

`a[A] & b e1@--> c` matches `edge-decl`, so it is `declaration-in-edge`, and it is not also `edge-id-on-group`.

## Other identifiers

- `edge-id-on-group`: Applies only to an edge statement (rule 8 at the top level).
- `undeclared-id`: The refused line names nothing.
