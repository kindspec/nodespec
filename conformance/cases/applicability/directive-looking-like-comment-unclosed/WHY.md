# applicability/directive-looking-like-comment-unclosed

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** The exact form of the `stray-direction` rule, including that front matter is exempt, that directive lines are not, and that its words compare exactly (§4.9).

## Input

````text
flowchart TD
a[A]
%% x %%{ direction LR
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> Each line is classified by the first rule below that matches it. A line that is classified is never also read as something else.

§4.2:

> A directive: the line holds `%%{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10).

§4.9:

> A directive line is not exempt (provisional): Mermaid removes only the text its directive pattern matches and lexes the rest.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

## Reasoning

§4.2's rules apply in order and a classified line is never read as anything else. Rule 3 (holds `%%{`) comes before rule 5 (comment), so the line is a directive, not a comment. A directive line is not exempt from `stray-direction`, and it holds `direction`, a space, `LR`.

## Other identifiers

- `malformed-line`: Rule 3 classifies the line before rule 6 could make it a statement line.
