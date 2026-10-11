# Caching

Responses are cached for five minutes.

```mermaid
flowchart LR
  client --> edge
  edge --> origin
  edge --> stale_cache
  origin --> db
  stale_cache --> db
```

Purge with `cachectl purge <path>`.
