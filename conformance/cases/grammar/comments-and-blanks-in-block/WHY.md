# grammar/comments-and-blanks-in-block

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
subgraph s
  %% a comment in a block

  a
⟨TAB⟩
end
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A comment matches `comment`. It is allowed anywhere, inside a block included (provisional, as are blank lines in a block), and is otherwise ignored.

§6:

> A block holds only member lines, direction statements, comments and blank lines (§4.3; the comments and blank lines are (provisional)):

§4.2:

> A blank line matches `blank`. It is allowed anywhere.

## Reasoning

Inside `s` stand an indented comment, an empty line and a line holding a tab. The comment matches `comment`, and the other two match `blank`. §4.2 classifies them before any statement rule, and §6 lets a block hold comments and blank lines, provisionally. The member line `a` names a declared node.
