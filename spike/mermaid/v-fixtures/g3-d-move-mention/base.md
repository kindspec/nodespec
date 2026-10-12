# ETL

```mermaid
flowchart LR
  poller[Poller]
  validator[Schema validator]
  enrich[Enricher]
  dedupe[Dedupe]
  writer[Warehouse writer]
  subgraph collect [Collection]
    poller
    validator
  end
  subgraph transform [Transform]
    enrich
    dedupe
  end
  subgraph load [Load]
    writer
  end
  poller --> validator --> enrich --> dedupe --> writer
```

Runs hourly.
