# refusal/conflict-marker

**Expected:** refused. Identifiers that apply: `conflict-marker`.

## Input

````text
flowchart TD
a[A]
<<<<<<< ours
b[B]
=======
>>>>>>> theirs
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.2:

> A conflict marker: the line's first seven characters are seven `<`, seven `=`, seven `>` or seven `|`. Refused as `conflict-marker`.

§9:

> A line that §4.2 to §4.10 refuses contributes nothing else. It declares nothing, names nothing, opens and closes no block, and is not a member line, a direction statement, a `style` line, a `class` line or an edge for any later rule.

## Reasoning

Lines 3, 5 and 6 begin with seven `<`, seven `=` and seven `>`. Each is refused as `conflict-marker`. `b[B]` between them is an ordinary node statement, and `a` and `b` are each declared once.

## Other identifiers

- `malformed-line`: A conflict-marker line is classified by §4.2 rule 2 and is never also a statement line.
- `duplicate-declaration`: Only one side of the conflict holds a declaration.
