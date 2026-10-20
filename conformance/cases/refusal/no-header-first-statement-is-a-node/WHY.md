# refusal/no-header-first-statement-is-a-node

**Expected:** refused. Identifiers that apply: `no-header`.

## Input

````text
a[A]
````

## What SPEC.md says

Quoted verbatim, with SPEC.md's line breaks folded into spaces and its bold markers dropped.

§4.3:

> A file with no statement line is refused as `no-header`. A first statement line that does not match `header` is refused as `no-header`, and the lines after it are classified as if a header stood in its place.

§4.3:

> The first statement line is the header: `flowchart` or `graph`, then optionally a direction. Blank lines and comments may come before it.

## Reasoning

The first statement line, `a[A]`, does not match `header`. It is refused as `no-header`, and there are no lines after it.

## Other identifiers

- `undeclared-id`: Nothing names an id.
- `reserved-id`: Applies only to a line nothing else refuses; and `a` is not reserved.
