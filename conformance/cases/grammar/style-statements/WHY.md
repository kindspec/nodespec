# grammar/style-statements

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
style a fill:#f9f,stroke:#333,stroke-width:4px
subgraph s
  a
end
style s fill:#eee ⟨TAB⟩
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> style-stmt = *WSP "style" 1*WSP id 1*WSP style-list *WSP

§5.2:

> | `style` | its target | node or subgraph (D1) |

§4.8:

> A `class` line ends at its class id: Mermaid refuses `WSP` after it. `classDef` and `style` lines may end in `WSP`, which Mermaid keeps in the last style.

§7:

> Apart from `class` lines, D4 orders nothing. Declarations, edges, blocks and `style` lines may come in any order

## Reasoning

`style` targets a node and a subgraph, one `style` line each. The second ends in a space and a tab, which `style-stmt` admits. A `style` line may stand anywhere; here one stands before the block that names its target.
