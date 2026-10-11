# Build

```mermaid
flowchart LR
  src[Source] --> compile[Compile]
  compile --> unit[Unit tests]
  unit --> package[Package]
  package --> publish[Publish]
```

Builds run on every push.
