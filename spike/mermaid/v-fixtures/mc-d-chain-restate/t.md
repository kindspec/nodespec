# Onboarding

```mermaid
graph TD
  signup[Sign-up form] --> verify[Verify email]
  verify --> consent[Consent screen]
  consent --> profile[Create profile]
  profile --> welcome[Welcome email]
  verify --> crm[(CRM)]
```

Unverified accounts are deleted after a week. The consent screen is required
in the EU.
