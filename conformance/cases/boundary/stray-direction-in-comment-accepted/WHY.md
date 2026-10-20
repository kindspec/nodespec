# boundary/stray-direction-in-comment-accepted

**Expected:** accepted.

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

**Twin:** `boundary/stray-direction-in-label-refused`, which differs from this file by 7 byte edits (Levenshtein distance over bytes).

## Input

````text
flowchart TD
a[A]
%% go direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.9:

> So a line other than a comment, a front matter line or a line that matches `direction-stmt` is refused as `stray-direction` when (provisional, in this exact form):

§4.9:

> The text may stand anywhere in the line: in a label, a title, a style, an id (`xdirection LRX` matches). `stray-direction` applies whatever else applies to the line. Comment lines are exempt because Mermaid removes them before it lexes.

## Reasoning

Comment lines are exempt.
