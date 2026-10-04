# Historical diff — old vs new bundles

Wayback CDX: 14 historical captures of JS assets, 6 unique digests after `collapse=digest`.

## Removed paths (in old bundle, gone from current) — live-probed vs dead-path baseline

| Removed path | Old bundle | Live probe | Verdict |
|--------------|-----------|------------|---------|
| `/api/v1/admin/export` | main-9c1.js (2024-06) | 200, CSV download, no auth | **CONFIRMED** — retired endpoint still live |
| `/api/v1/users/search?q=` | main-9c1.js (2024-06) | 404, matches baseline | NEGATIVE — truly retired |
| `/debug/state` | main-77e.js (2024-03) | 302 → /login | INCONCLUSIVE — auth-gated, needs session |

## Retired API versions / auth flows

- `v1` admin export: still live (see above) — version-downgrade lead.
- Old auth flow `POST /api/v1/auth/token` → now 401 on all methods — dead, documented so nobody re-tests.
