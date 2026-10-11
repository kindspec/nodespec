# Order fulfilment

```mermaid
flowchart TD
  start([Start])
  check{Stock available?}
  reserve[Reserve items]
  start --> check
  check -->|yes| reserve
  check -->|no| backorder
  reserve --> ship[Ship]
  backorder --> notify[Email customer]
  backorder[Create backorder]
```

Backorders are reviewed daily.
