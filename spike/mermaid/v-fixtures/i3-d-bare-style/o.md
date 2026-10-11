# File delivery

Uploads are scanned before delivery to partners. FTP delivery has been
switched off.

```mermaid
flowchart LR
  upload --> scan
  scan --> s3
  s3 --> partner
```

Contact the integrations team to add a partner.
