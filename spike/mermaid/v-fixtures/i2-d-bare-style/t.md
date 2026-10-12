## Telemetry path

```mermaid
graph LR
  sensor --> ingest
  ingest --> stream
  stream --> warehouse
  stream --> alerts
  alerts --> dlq
  style dlq stroke-dasharray: 4 2
```

Late events are dropped after one hour.
