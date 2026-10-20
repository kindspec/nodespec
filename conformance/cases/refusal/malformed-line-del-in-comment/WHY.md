# refusal/malformed-line-del-in-comment

**Expected:** refused. Identifiers that apply: `malformed-line`.

## Input

````text
flowchart TD
a[A]
%% xy
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.1:

> comment = *WSP "%%" ( HTAB / %x20-7A / %x7C-7E / nonascii ) *cchar ; next is not "{"

§4.1:

> cchar = HTAB / %x20-7E / nonascii

§4.2:

> Every other line is a statement line. The first statement line of a file is the header's place (§4.3); later statement lines are classified by §4.3's rules.

§4.3:

> Anything else: `malformed-line`.

## Reasoning

DEL (0x7F) is no `cchar` (`%x20-7E` stops at 0x7E), so the line does not match `comment`. §4.2 then makes it a statement line, and after the header it matches no production.

## Other identifiers

- `bad-encoding`: 0x7F is well-formed UTF-8.
- `not-admitted`: No `%%{`.
