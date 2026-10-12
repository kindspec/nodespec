# Services

```mermaid
flowchart TB
  subgraph backend [Backend]
    users[Users]
    orders[Orders]
  end
  web[Web] --> users
  web --> orders
```

All backend services run in one cluster.
