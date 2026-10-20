# grammar/class-statements

**Expected:** accepted.

## Input

````text
flowchart TD
a[A]
b[B]
subgraph s
  a
end
a e1@--> b
classDef hot fill:#f96
class a,b,s hot
class e1 hot
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> class-stmt = *WSP "class" 1*WSP id *( "," id ) 1*WSP id

§4.8:

> `classDef c fill:#f9f,stroke:#333` declares the class `c` with a style list. `class a,b c` gives the class `c` to `a` and `b`. `style a fill:#f9f` styles `a`. Each statement is at the top level (D3); what each may name is §5.2.

§5.2:

> | `class` | each target | node, subgraph or edge (D1) |

§5.2:

> | `class` | its last id, the class | class |

§7:

> Every `class` line comes after every other statement line. That is 0001's "with class lines last", read literally. A `class` line that has, anywhere after it, a statement line that is not a `class` line is refused as `class-not-last`; only blank lines, comments and other `class` lines may follow one.

## Reasoning

`class a,b,s hot` gives one class to a node, another node and a subgraph; `class e1 hot` gives it to an edge. Each target is on one `class` line, each line names one class, and both are the last statement lines.
