# Build

```mermaid
flowchart LR
  src[Source] --> compile[Compile and link]
  compile --> unit[Unit tests]
  unit --> package[Package]
  package --> publish[Publish]
```

Builds run on every push.
