# applicability/markdown-fence

**Expected:** refused. Identifiers that apply: `no-header`; `malformed-line`.

A report of any one of these passes, with one of its ids where it has them (§9).

**Pins the provisional reading (§12):** A Markdown fence is outside draft 0 (§2).

## Input

````text
```mermaid
flowchart TD
a[A]
```
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§2:

> A Mermaid fence inside a Markdown file is outside draft 0 (provisional).

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place (provisional).

## Reasoning

The fence line is the first statement line and no header; `flowchart TD` and the closing fence then match nothing.

## Other identifiers

- `not-admitted`: A fence is no §4.10 form, and "```mermaid" holds no `"`.
