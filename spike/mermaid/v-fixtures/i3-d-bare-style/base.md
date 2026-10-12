# File delivery

Uploads are scanned before delivery to partners.

```mermaid
flowchart LR
  upload --> scan
  scan --> ftp
  scan --> s3
  ftp --> partner
  s3 --> partner
```

Contact the integrations team to add a partner.
