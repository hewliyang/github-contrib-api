# github-contrib-api

Barebones wrapper/hosted API for contributions by date range

```bash
curl -X 'POST' \
  'https://github-contrib-api.vercel.app/contributions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "<a valid github username>",
  "from_date": "2022-09-09T16:37:49.511709",
  "to_date": "2023-09-16T16:37:49.511846"
}'
```
