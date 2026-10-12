# Checkout services

```mermaid
graph LR
  checkout --> fraud_check
  checkout --> inventory
  inventory --> warehouse
  warehouse --> shipping
```

Every call has a two-second timeout.
