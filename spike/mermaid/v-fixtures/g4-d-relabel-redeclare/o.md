# Request authorization

```mermaid
flowchart TD
  req[Request] --> authz{Authorized?}
  authz -->|yes| handler[Handler]
  authz -->|no| deny[401 or 403]
  handler --> resp([Response])
```

Tokens are checked against the policy service. A missing token gives 401.
