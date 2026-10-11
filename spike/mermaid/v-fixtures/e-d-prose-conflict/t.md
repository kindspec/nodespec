# Caching

Responses are cached for one minute.

```mermaid
flowchart LR
  client --> edge
  edge --> origin
  edge --> stale_cache
  origin --> db
```

Purge with `cachectl purge <path>`.
