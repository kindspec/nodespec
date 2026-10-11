# Release checklist

Red boxes are blocked.

```mermaid
flowchart TD
  plan[Plan] --> build[Build]
  build --> review[Review]
  review --> release[Release]
  classDef blocked fill:#fdd,stroke:#c00
  classDef done fill:#dfd
  class review blocked
  class plan done
```

Update the diagram at each stand-up.
