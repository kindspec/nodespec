# grammar/member-lines

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s
a
⟨TAB⟩b ⟨TAB⟩
 end⟨SP⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> member-line = *WSP id *WSP

§4.3:

> Matches `member-line`: in a block, a member line (§6); at the top level, `malformed-line`.

§6:

> A member line names one declared node or subgraph, and makes the block's subgraph its holder. A member line naming a subgraph nests that subgraph in the block's subgraph. Mermaid nests a subgraph named on a member line as it nests a block written inside another, whichever of the two blocks comes first in the file.

§4.1:

> end-line = *WSP "end" *WSP

## Reasoning

In a block, `a` with no indentation and `\tb \t` with a leading tab and trailing space and tab each match `member-line` and name a declared node. ` end ` matches `end-line`, whose `*WSP` admits the spaces, and closes the block.
