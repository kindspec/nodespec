# boundary/style-words-that-are-reserved-ids-accepted

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
classDef c fill:hasOwnProperty,stroke:L_x_y_0,color:direction-x,font-family:node
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.8:

> Neither a `name` nor its part before its first `-` is `v` or one of the 17 words listed in §4.4; the other reserved ids, such as `hasOwnProperty` and `direction`, parse as style words (`fill:hasOwnProperty`, `fill:direction-x`).

§4.4:

> The `L_…` form is reserved for ids only; a style word of that form, `fill:L_x_y_0`, is an ordinary `name`.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

§4.9:

> with trailing whitespace removed, it ends in `direction`.

## Reasoning

§4.8 names `fill:hasOwnProperty` and `fill:direction-x` as style words and §4.4 `fill:L_x_y_0`; `node` is not one of the 17 words. `direction-x` is followed by `-`, not whitespace, and the line ends in `node`, so §4.9 does not apply.
