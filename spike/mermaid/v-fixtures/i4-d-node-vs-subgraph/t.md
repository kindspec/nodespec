# Shop services

```mermaid
flowchart TB
  web[Storefront] --> cart[Cart service]
  cart --> orders[Order service]
  orders --> mq[[Event bus]]
  subgraph billing [Billing]
    invoicer[Invoicer]
    dunning[Dunning]
  end
  mq --> billing
```

Each service owns its own database.
