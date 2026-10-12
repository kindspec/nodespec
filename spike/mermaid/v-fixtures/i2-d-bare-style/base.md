## Telemetry path

```mermaid
graph LR
  sensor --> ingest
  ingest --> stream
  stream --> warehouse
  stream --> alerts
```

Late events are dropped after one hour.
