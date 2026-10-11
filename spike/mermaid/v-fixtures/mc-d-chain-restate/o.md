# Onboarding

```mermaid
graph TD
  signup[Sign-up form] --> verify[Verify email]
  verify --> profile[Create profile]
  profile --> welcome[Welcome email]
  verify --> crm[(CRM)]
  verify --> profile --> tour[Product tour]
```

Unverified accounts are deleted after a week.
