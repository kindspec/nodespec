# Release train

Every change rides the same path to production. Canary releases were
retired in favour of feature flags.

```mermaid
graph TD
  commit --> ci
  ci --> build
  build --> staging
  staging --> prod
  build --> artifacts
```

Artifacts are kept for ninety days.
