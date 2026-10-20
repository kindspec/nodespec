# refusal/declaration-in-edge

**Expected:** refused. Identifiers that apply: `declaration-in-edge`.

## Input

````text
flowchart TD
db[DB]
api[API] --> db
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§5.1:

> A declaration inside an edge, `api[API] --> db`, matches `edge-decl` and not `edge-stmt`, and is refused as `declaration-in-edge`

§4.3:

> Matches `edge-decl`: in a block, `statement-in-block`; at the top level, `declaration-in-edge`.

§4.1:

> edge-decl = *WSP dgroup 1*( 1*WSP [ id "@" ] link [ "|" label "|" ] 1*WSP dgroup ) *WSP dgroup = dend *( 1*WSP "&" 1*WSP dend ) dend = id [ shape ]

## Reasoning

§5.1's own example: `api[API]` is a `dend` with a shape, so the line matches `edge-decl` and not `edge-stmt`.

## Other identifiers

- `undeclared-id`: The refused line names nothing, and nothing else names `api`.
- `malformed-line`: Rule 9 applies.
