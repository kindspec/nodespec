# applicability/directive-looking-like-comment-unclosed

**Expected:** refused. Identifiers that apply: `not-admitted`; `stray-direction`.

A report of any one of these passes, with one of its ids where it has them (§9).

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

> A directive, class shorthand or shape data: the line holds `%%{`, `:::` or `@{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10; for `:::` and `@{`, the owner, 2026-10-20).

§4.9:

> A directive line is not exempt: Mermaid removes only the text its directive pattern matches and lexes the rest.

§4.9:

> it holds `direction`, then one or more whitespace characters, then `TB`, `BT`, `RL`, `LR` or `TD`; or

## Reasoning

§4.2's rules apply in order and a classified line is never read as anything else. Rule 3 (holds `%%{`) comes before rule 5 (comment), so the line is a directive, not a comment. A directive line is not exempt from `stray-direction`, and it holds `direction`, a space, `LR`.

## Other identifiers

- `malformed-line`: Rule 3 classifies the line before rule 6 could make it a statement line.
