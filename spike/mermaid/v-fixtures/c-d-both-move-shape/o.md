# Order fulfilment

```mermaid
flowchart TD
  start([Start])
  check{Stock available?}
  reserve[Reserve items]
  start --> check
  check -->|yes| reserve
  check -->|no| backorder
  backorder[[Create backorder]]
  reserve --> ship[Ship]
  backorder --> notify[Email customer]
```

Backorders are reviewed daily. Creating one is a subprocess with its own
diagram in `backorders.md`.
