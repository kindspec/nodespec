# grammar/comments

**Expected:** accepted.

## Input

````text
%% a comment before the header
flowchart TD
%% a comment
   %% an indented comment
%%no space after the marks
%%⟨TAB⟩tab after the marks
a[A]
%% braces later are fine: {x}, a quote " and ;
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment matches `comment`. It is allowed anywhere, inside a block included (provisional, as are blank lines in a block), and is otherwise ignored.

§4.1:

> comment = *WSP "%%" ( HTAB / %x20-7A / %x7C-7E / nonascii ) *cchar ; next is not "{"

§4.1:

> a `comment` does not hold `="` (§4.2);

§4.2:

> A directive: the line holds `%%{` anywhere, in a comment or a label included. Refused as `not-admitted` (§4.10).

## Reasoning

Each comment line is `*WSP "%%"`, then a character that is not `{`, then `cchar`s. None holds `%%{` or `="`. The last holds `{` later in the line, a lone `"` and `;`; only `%%{` makes a directive and only `="` stops a comment being one.
