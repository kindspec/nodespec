# Services

```mermaid
flowchart TB
  subgraph be [Backend]
    users[Users]
    orders[Orders]
  end
  web[Web] --> users
  web --> orders
```

All backend services run in one cluster.
