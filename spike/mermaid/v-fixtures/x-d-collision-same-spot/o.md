# Read path

```mermaid
flowchart LR
  app[App] --> db[(Primary)]
  db --> replica[(Replica)]
  app --> cache[(Redis)]
```

Reads go to the replica when lag is under one second.
