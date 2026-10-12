# Services

```mermaid
flowchart TB
  subgraph be [Backend]
    users[Users]
    search[Search]
    orders[Orders]
  end
  web[Web] --> users
  web --> orders
  web --> search
```

All backend services run in one cluster.
