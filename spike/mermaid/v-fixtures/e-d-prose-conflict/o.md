# Caching

Responses are cached for ten minutes.

```mermaid
flowchart LR
  client --> edge
  edge --> origin
  origin --> db
  stale_cache --> db
```

Purge with `cachectl purge <path>`.
