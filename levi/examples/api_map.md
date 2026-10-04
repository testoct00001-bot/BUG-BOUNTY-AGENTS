# API map — shop-example.com

Base URLs: `https://api.shop-example.com` (v2 current), `https://api.shop-example.com/v1` (retired, partially live)

## Auth
- `POST /v2/auth/login` — JSON {email, password} → {token}
- `POST /v2/auth/refresh` — {refresh_token} → {token}
- ~~`POST /v1/auth/token`~~ — 401 on all methods, dead (documented, do not re-test)

## User
- `GET /v2/users/me` — bearer required
- `GET /v2/users/{id}` — **IDOR lead**: no ownership check observed in JS; needs live test vs baseline

## Orders / Payments
- `POST /v2/orders` — bearer required; `currency` param client-controlled (lead)
- `POST /v2/payments/intent` — Stripe client secret returned to browser (sensitive, reachable unauth? no — bearer required)

## Admin (old version!)
- `GET /v1/admin/export` — **CONFIRMED live, no auth** (from historical diff) — version-downgrade finding
- `GET /v2/admin/users` — 403 without admin role (correctly gated)

## Version notes
- v1 retired 2024-06 but `/v1/admin/export` still live → test every v1 route in the old bundle.
