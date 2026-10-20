# grammar/labels-unquoted

**Expected:** accepted.

## Input

````text
flowchart TD
a[two words]
b[ leading space]
c[semi;colon]
d[café ☕]
e[1 < 2]
f[a=b, c's #1 & 2?]
g[a\b/c]
h[tab⟨TAB⟩here]
````

Shown with markers: ⟨CR⟩ a carriage return, ⟨TAB⟩ a tab, ⟨SP⟩ a trailing space, ⟨BOM⟩ U+FEFF, ⟨U+00A0⟩ and ⟨U+2028⟩ those characters, ⟨xFF⟩ a byte that is not UTF-8. `input.mmd` holds the raw bytes.

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.5:

> An unquoted label has at least one character that is not `WSP`; its first such character is not `-`, `/` or `\`, since `(-`, `[/` and `[\` open other shapes; it holds none of `[ ] ( ) { } | " @`; and it holds no `~~~`.

§4.1:

> label = unquoted / quoted unquoted = *WSP lead *lchar quoted = DQUOTE 1*qchar DQUOTE

§4.1:

> lchar = HTAB / %x20-21 / %x23-27 / %x2A-3F / %x41-5A / %x5C / %x5E-7A / %x7E / nonascii ; a label character: not [ ] ( ) { } | " @

§4.1:

> lead = %x21 / %x23-27 / %x2A-2C / %x2E / %x30-3F / %x41-5A / %x5E-7A / %x7E / nonascii ; an lchar that is not WSP, - / or \

§4.1:

> nonascii = %xA0-2027 / %x202A-D7FF / %xE000-10FFFF ; not U+2028 or U+2029 (§4.2)

§4.3:

> `;` is not admitted anywhere outside a label (the owner, 2026-10-19: refused for now), so a statement line ending in `;`, two statements on one line, and a member line `a;` are `malformed-line`, and a header ending in `;` is `no-header`.

## Reasoning

Each label is `*WSP lead *lchar`: `b`'s leading space is the `*WSP`; every other character is an `lchar` (space, tab, `;`, `<`, `=`, `,`, `'`, `#`, `&`, `?`, `\`, `/`, and the non-ASCII `é` U+00E9 and `☕` U+2615, both inside `nonascii`). No label begins with `-`, `/` or `\`, and none holds `[ ] ( ) { } | " @` or `~~~`. `;` is admitted inside a label, which §4.3 says in so many words. No label holds `direction`, so §4.9 does not apply.
