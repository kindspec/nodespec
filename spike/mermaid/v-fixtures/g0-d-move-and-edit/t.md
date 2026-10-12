# Writing guide

## Style

Use sentence case for headings.

## Workflow

```mermaid
flowchart TD
  draft[Draft] --> review{Peer review}
  review -->|changes| draft
  review -->|approved| legal[Legal check]
  legal --> publish[Publish]
```

## Tooling

Drafts live in the `articles/` folder.
