# Funnel

```mermaid
graph LR
  visitor --> landing
  landing -.->|returning| active
  landing --> signup
  signup --> onboarding
  onboarding --> active
```

Numbers are refreshed weekly.
