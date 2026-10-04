---
name: feature-map
description: >
  Maps every application feature visible in the target's JavaScript to its attack surface — entry points plus one-hop data flows — turning each feature into one concrete, testable hunt lead ranked by what leaks, what's sensitive, and what's reachable unauthenticated. USE THIS SKILL whenever the user wants to map the app features, see the attack surface per feature, or answer what an app can do. Trigger on: "map the app features", "attack surface per feature", "what can this app do". This skill produces the ammunition – the deep-hunt-loop fires it.
---

# Feature Map

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn a pile of JavaScript into a ranked list of hunt leads where every row names the exact endpoint and parameter to test next — leads that generic crawling will never produce.

## Step 1 – Gather inputs

- `<WORKDIR>/normalized/` — all bundles; routes, fetch calls, and SDK strings live here
- `<WORKDIR>/sourcemaps/` — route files often appear as `pages/`, `routes/`, `views/` in `sources[]`; the file tree IS the feature list
- `<WORKDIR>/inventory_final.json` — chunk names hint at features (`checkout.`, `admin.`, `upload.`)
- `<WORKDIR>/tech_choices.md` — framework decides route syntax (Next.js file routes vs React Router paths)
- `<WORKDIR>/libraries.md` — SDK presence means feature presence: a stripe SDK string means payments exist even if you haven't found the checkout page yet
- `<TARGET>` — base URL, used only for live verification of lead endpoints

Check first: read the sourcemap `sources[]` tree before grepping. A `pages/admin/users.tsx` path hands you the admin feature with zero regex.

## Step 2 – Feature-pattern sweep

2.1 Identity: auth (login/register/token-refresh endpoints, OAuth `/callback` routes, JWT/session markers, magic-link flows), password reset (`/forgot`, `/reset`, token params like `?token=` or `/reset/<token>`), API-key management (`/api-keys`, key generation/regeneration endpoints, any place a key is displayed — display = leak check).
2.2 File upload: `input type=file`, `FormData`, presigned-URL flows (the endpoint that ISSUES the PUT URL matters more than the PUT itself), S3/GCS/Azure markers (`.s3.amazonaws.com`, `storage.googleapis.com`, `blob.core.windows.net`, `x-amz-`).
2.3 Search: `/search`, `?q=`, `?query=`, autocomplete endpoints, elastic/opensearch marker strings.
2.4 Payments: stripe/razorpay/paypal/braintree SDK strings, `/checkout`, `/billing`, `/subscribe`, webhook endpoints (`/webhooks/`, `/stripe/webhook` — webhooks are signature-verification targets).
2.5 Admin: `isAdmin` / `role === 'admin'` checks, `/admin` routes, admin-only API prefixes. Client-side role checks are not access control — every admin endpoint they guard is a direct request test waiting to happen.
2.6 Realtime: `new WebSocket(`, `socket.io`, `/ws`, `/socket.io`, subscription channel names; messaging/comments (`/comments`, `/messages`, rich-text editors — cross-check library-analysis for XSS sinks in the editor); notifications (`/notifications`, push-subscription endpoints).
2.7 Profile/settings: `/profile`, `/settings`, `/account`, avatar upload, preferences endpoints — profile fields are stored-XSS and IDOR territory.

For each hit record the exact string and file. A feature with no endpoint string is a rumor, not a feature — keep sweeping until you have the string or drop it.

## Step 3 – Group hits per feature and extract entry points

3.1 Cluster the sweep hits: route definitions + `fetch`/`axios` calls + SDK init calls, grouped per feature. One feature, one cluster — no orphans.
3.2 Entry points = frontend routes + API endpoints + the parameters each accepts. Quote the exact strings from the bundle; record the HTTP method where visible (`fetch` options, `axios.post`).
3.3 If a feature's endpoints live on a different host (`api.<target>`, a CDN, a third party) → record the host; cross-origin features get their own lead rows with the trust boundary named.

Chunk-name hints: code-split chunk filenames (`checkout.8f2a.js`, `admin.3c1d.js`) name features the sweep may have missed — especially lazily loaded ones whose strings live only inside the chunk. Cross-check every chunk name in `inventory_final.json` against your feature clusters; an unmatched chunk is an unmapped feature until proven otherwise.

## Step 4 – Trace data flow one hop

4.1 For each entry point: where does user-controlled input enter, and where does it go within one hop? Form field → fetch body. URL param → rendered HTML. File input → presign request → PUT URL.
4.2 Mark every trust-boundary crossing: client→API, API→third-party (S3, Stripe), client→websocket. Crossings are where the interesting bugs live.
4.3 Record observed auth requirements per endpoint: `Authorization` headers, `withCredentials`, token-refresh logic — or nothing at all. Nothing at all ranks the lead up.

One hop is enough for the map; deeper tracing belongs to the deep-hunt-loop agents that consume these leads.

## Step 5 – Write the lead row

Table format: `| Feature | Entry point (exact endpoint + param) | Data flow (one hop) | Auth observed | THE LEAD (concrete next test) |`

The iron rule: if a row cannot name the exact endpoint and parameter to test next, it is not a lead — it is a wish. Delete it or demote it to a note.

Lead patterns to instantiate per feature — always with the target's real endpoint strings, never generics:
- upload → file-type bypass + presign abuse: request a PUT URL from `<presign-endpoint>` with `filename` set to `<name>.html`, then fetch what the bucket serves back
- search → injection / XS-leak on `GET <search-endpoint>?<q-param>=`
- websockets → auth on the handshake + message forgery on `wss://<TARGET>/<ws-path>` channel `<name>`
- password reset → token entropy and host-header poisoning on `POST <reset-endpoint>`
- admin → direct request to `<admin-endpoint>` with a low-privilege or missing session
- API keys → regeneration CSRF and key-display leakage on `<apikey-endpoint>`

Every lead also records its prerequisites: does the test need an account, a second user, or a specific role? A lead that needs two accounts is still a lead — but its rank drops unless account creation is open and unauthenticated.

## Step 6 – Rank the leads

6.1 Score every lead against the doctrine: does it LEAK? Is it SENSITIVE? Is it reachable UNAUTHENTICATED?
6.2 P1: unauthenticated + sensitive leak or a direct access primitive (presigned PUT URL issuance, IDOR-shaped endpoint, token in URL, admin endpoint without a session check).
6.3 P2: authenticated-but-testable, or unauthenticated with lower impact (verbose errors, info disclosure).
6.4 P3: everything else worth a look — interesting, not first. Time-pass surface (marketing pages, static content, locale files) gets no lead row at all — the doctrine says skip it, so skip it.

## Step 7 – Exact commands

```bash
# BASELINE — dead-path signature; every lead endpoint is judged against this
curl -sS -o /tmp/levi_dead.html -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/levi-dead-path-9f3a2c1d'
md5sum /tmp/levi_dead.html
```

```bash
# PROBE — endpoint-shaped strings across normalized bundles
cd <WORKDIR>
grep -rhoE '"/(api/)?[a-z0-9/_.-]{2,60}"' normalized/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -80 > /tmp/levi_endpoints.txt
```

```bash
# PROBE — feature markers across normalized bundles
cd <WORKDIR>
grep -rn -iE 'new WebSocket\(|socket\.io|"/ws"' normalized/ | head -20
grep -rn -iE 'stripe|razorpay|paypal|braintree' normalized/ | head -20
grep -rn -iE 's3\.amazonaws\.com|storage\.googleapis\.com|blob\.core\.windows\.net' normalized/ | head -20
grep -rn -iE 'isAdmin|role.{0,12}admin|"/admin' normalized/ | head -20
grep -rn -iE 'forgot|"/reset|api-keys|/webhook' normalized/ | head -20
```

```bash
# PROBE — route files from the sourcemap tree (the file tree IS the feature list)
cd <WORKDIR>
for m in sourcemaps/*.map; do jq -r '.sources[]' "$m" 2>/dev/null; done \
  | grep -iE 'pages/|routes/|views/|screens/' | sort -u | head -60
```

```bash
# PROBE — route definitions (framework syntax varies; check tech_choices.md first)
cd <WORKDIR>
grep -rhoE '(path|route):[[:space:]]*["'"'"'][a-z0-9/_.-]{2,60}["'"'"']' normalized/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -40
```

```bash
# VERIFY — a lead endpoint is real only if it differs from the dead-path baseline
# <ENDPOINT> = the exact endpoint string from the lead row, quoted from the bundle
curl -sS -o /tmp/levi_lead.json -D /tmp/levi_lead.hdrs \
  -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/<ENDPOINT>'
md5sum /tmp/levi_lead.json
# compare code + size + hash against /tmp/levi_dead.html from BASELINE
```

Never invent endpoints — every VERIFY target must be quoted from the bundle first.

## Step 8 – Completion checklist

- [ ] Inputs gathered: normalized bundles, sourcemap tree, inventory, tech_choices.md, libraries.md
- [ ] Feature-pattern sweep run for all seven clusters in Step 2
- [ ] Every hit recorded with exact string + file; rumor-features dropped
- [ ] Hits clustered per feature; entry points extracted with methods and params
- [ ] Cross-origin features recorded with their host and trust boundary
- [ ] One-hop data flow traced per entry point; auth observations recorded
- [ ] Lead table written; every row names the exact endpoint + param or it was deleted
- [ ] Leads ranked P1/P2/P3 by leak × sensitive × unauthenticated
- [ ] Time-pass surface excluded — no lead rows for marketing/static content
- [ ] `<WORKDIR>/feature_map.md` written at its exact path

### Review
A reviewer must verify: every lead row quotes an endpoint string that exists in the bundles; every P1 lead is reachable unauthenticated with the evidence shown; no row is a wish dressed as a lead.

*Pick any P1 lead: can you paste the bundle line where its endpoint string appears?*
*Which feature had the most trust-boundary crossings — and did its lead say so?*
*What did you deliberately leave out as time-pass, and why?*

Done = `<WORKDIR>/feature_map.md` exists on disk with the feature table and the ranked hunt leads.

## Step 9 – Evidence standard (no false positives)

- Baseline every lead-endpoint check against the known-dead path: matching status + size + hash means the SPA fallback answered, not the endpoint.
- Endpoint strings are static until verified live: unverified rows are marked CANDIDATE in the table, never presented as live attack surface.
- Verdicts per lead: CONFIRMED (endpoint live + behavior observed), INCONCLUSIVE (ambiguous response, next probe named), NEGATIVE (dead-path signature or definitive 404), BLOCKED (auth wall / WAF, exact blocker documented).
- 2x reproduction for any behavioral claim; raw request/response pairs saved under `<WORKDIR>/raw/`.
- Secrets (API keys, tokens) found during the sweep are redacted everywhere and never live-tested without the user's explicit approval.

## Step 10 – Finished artifact & handoff

Artifact: `<WORKDIR>/feature_map.md` — the feature table (`| Feature | Entry point | Data flow | Auth observed | THE LEAD |`) followed by the ranked hunt leads (P1 first), each lead naming the exact endpoint and parameter to test next.

Handoff: `report_output` consumes the lead inventory section (P1/P2 leads with their evidence). The deep-hunt-loop / THINKER agents take each lead as a starting point — one lead, one hunt thread. `03_content_discovery` consumes the feature-specific paths (admin routes, upload endpoints, websocket paths) as targeted discovery inputs.
