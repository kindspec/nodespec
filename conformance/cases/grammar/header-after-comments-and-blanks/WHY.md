# grammar/header-after-comments-and-blanks

**Expected:** accepted.

## Input

````text

%% a comment before the header
 ⟨TAB⟩
  graph BT ⟨TAB⟩
a[A]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

§4.1:

> header = *WSP ( "flowchart" / "graph" ) [ 1*WSP dir ] *WSP

§4.2:

> A blank line matches `blank`. It is allowed anywhere.

§4.2:

> A comment matches `comment`. It is allowed anywhere, inside a block included (provisional, as are blank lines in a block), and is otherwise ignored.

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

## Reasoning

Line 1 is empty and line 3 holds only `WSP`; both match `blank`. Line 2 matches `comment`. None is a statement line, so line 4 is the first statement line, and `*WSP "graph" 1*WSP "BT" *WSP` matches it with its leading spaces and trailing space and tab.
