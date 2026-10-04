# Report — shop-example.com — 2026-10-04

## Summary
Next.js storefront. One CONFIRMED high-impact finding (unauthenticated retired admin
export), two leads (IDOR, client-controlled currency), zero padding.

## Tech choices
Next.js 14 (webpack), Stripe client-side, REST `/v2` (retired `/v1` partially live).

## Findings

| # | Finding | Verdict | Impact |
|---|---------|---------|--------|
| 1 | `GET /v1/admin/export` — no auth, full order CSV | CONFIRMED | High — PII leak, reachable unauthenticated |
| 2 | `GET /v2/users/{id}` — possible IDOR | INCONCLUSIVE | needs session test |
| 3 | `currency` param client-controlled on `POST /v2/orders` | CANDIDATE | needs live tamper test |

## Evidence appendix

### Finding 1 — raw pairs (2x reproduced)
**Baseline** (known-dead): `GET /v1/admin/nope` → 404 `{"error":"not_found"}` (211 bytes)
**Probe 1**: `GET /v1/admin/export` → 200 `text/csv`, 48,211 bytes, first rows:
`order_id,email,total,...` (PII redacted in this report; full capture in `raw/evidence/`)
**Probe 2** (reproduction, fresh session): identical 200.

### NEGATIVEs (documented so nobody re-tests)
- `/v1/auth/token` — 401 all methods. `/api/v1/users/search` — 404, matches baseline.
