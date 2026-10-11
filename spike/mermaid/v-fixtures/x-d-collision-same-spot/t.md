# Read path

```mermaid
flowchart LR
  app[App] --> db[(Primary)]
  db --> replica[(Replica)]
  replica --> cache[(Query cache)]
```

Reads go to the replica when lag is under one second.
