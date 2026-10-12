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
  end
  subgraph transform [Transform]
    enrich
    dedupe
  end
  subgraph load [Load]
    validator
    writer
  end
  poller --> validator --> enrich --> dedupe --> writer
```

Runs hourly.
