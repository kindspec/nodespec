# Checkout services

```mermaid
graph LR
  checkout --> fraud_check
  checkout --> inventory
  inventory --> warehouse
  fraud_check --> risk_api
  warehouse --> shipping
```

Every call has a two-second timeout.
