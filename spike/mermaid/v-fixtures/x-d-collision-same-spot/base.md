# Read path

```mermaid
flowchart LR
  app[App] --> db[(Primary)]
  db --> replica[(Replica)]
```

Reads go to the replica when lag is under one second.
