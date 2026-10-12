# File delivery

Uploads are scanned before delivery to partners.

```mermaid
flowchart LR
  upload --> scan
  scan --> ftp
  scan --> s3
  ftp --> partner
  s3 --> partner
  style ftp stroke:#f66,stroke-width:3px
```

Contact the integrations team to add a partner. FTP is deprecated and is
drawn in red.
