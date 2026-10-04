---
name: api-analysis
description: >
  Turns every API call in the <TARGET> JS into functionality-grouped attack maps and hunts old API versions for authorization regressions. USE THIS SKILL whenever the user wants to map all API calls, find old API versions, run an API version downgrade test. Trigger on: "map all API calls", "find old API versions", "API version downgrade test". This skill produces the ammunition – 03_content_discovery/api_discovery fires it.
---

# API Analysis

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn every API call in the JS into a functionality-grouped attack map, and hunt old API versions for authZ regressions — the class of bug where v1 forgot the checks that v2 enforces.

## Step 1 – Gather inputs

- <WORKDIR>/normalized/ — all API extraction runs here; regex passes miss string-concatenated URLs, so also read axios/fetch wrapper modules by hand.
- <WORKDIR>/routes_params.md — the param inventory from params-routes: params feed endpoints, so map each endpoint to the params it consumes.
- <WORKDIR>/gadgets.json — gadget chains that end in API calls (e.g. sink = fetch URL built from location.hash) are priority targets.
- jsluice: `find <WORKDIR>/normalized -name '*.js' | jsluice urls` (verified). Verified options you may use: `-S/--include-source` (see which file emitted the URL), `-R/--resolve-paths <url>` (resolve relative paths), `-I/--ignore-strings`, `-c/--concurrency N`. Anything else — verify with `jsluice --help` first.
- Baseline: one known-dead API endpoint on <TARGET> (e.g. `/api/v9/nope`) — record its exact 404 shape (status, body, content-type). Every API claim is judged against it.
- Decision rule: if jsluice returns zero `/api/` URLs, the API calls are probably string-concatenated (`"/api/" + ver + "/users"`). Grep for the fragments (`"/api/"`, `"users"`, template literals with `${}`) and reconstruct — do not conclude "no API surface" from one empty tool run.

Worked downgrade example (what a real regression looks like):

- v2 reference: `GET /api/v2/users/8471` with your own token → 200 own profile; with another user's ID → 403 `{"error":"forbidden"}`. AuthZ enforced. Baseline dead-endpoint 404 shape recorded separately.
- v1 twin: `GET /api/v1/users/8471` with the SAME token → 200 own profile; with another user's ID → 200 full profile including `email`, `phone`, `internal_notes`. AuthZ missing + extra fields.
- Verdict: CONFIRMED authZ regression (2x reproduced, raw pairs saved). The report states exactly what v1 returns that v2 withholds — field names verbatim, values redacted.
- Counter-example: v1 returns 404 identical to the dead-endpoint baseline → the old version is decommissioned → NEGATIVE, one line, move on. Do not keep hammering a dead version hoping it wakes up.

## Step 2 – Extract base URLs and API clients

1. Find client configuration: `axios.create({`, `baseURL:`, `fetch(` prefixes, `new WebSocket(`, `io(`, `EventSource(`. Record every baseURL verbatim — multiple baseURLs mean multiple API surfaces.
2. Harvest environment indirection: `REACT_APP_API_URL`, `VITE_API_URL`, `NEXT_PUBLIC_API`, `process.env.*API*`, `window.__CONFIG__`, `window.__ENV__`. Resolve each to its literal value from the bundle or the served HTML — an env var you cannot resolve is a gap, not a base URL.
3. List auth-header mechanics per client (`Authorization: Bearer`, `x-api-key`, cookies with `credentials: "include"`, CSRF token headers) AND note API-adjacent transports: GraphQL endpoints (`/graphql`), tRPC (`/api/trpc`), WebSocket/SSE channels, third-party SDK calls (Stripe, analytics) — mark third-party as out-of-scope noise unless the app leaks keys into them. Auth mechanics tell you what the downgrade test must replay.

## Step 3 – Map HTTP methods per endpoint

5. Extract method+path pairs: `fetch(url, {method: "POST"})`, `axios.get/post/put/patch/delete(`, `$.ajax({type:`, and the method constants in wrapper modules. A bare `fetch(url)` is GET — record it as such.
6. Build the endpoint table: `METHOD | path | client module | params consumed | auth header used`. De-dupe identical pairs; keep the file:line of first occurrence as evidence.
7. Flag method anomalies: state-changing actions on GET (CSRF-able), `DELETE` without confirmation flows, `PUT`/`PATCH` on collection paths (mass-assignment smell), endpoints accepting `_method` overrides.

## Step 4 – Group endpoints by functionality

8. Classify every endpoint into: auth (login, refresh, logout, register, password-reset, OTP, OAuth callbacks), user/profile (me, settings, avatar), payment/billing (checkout, invoices, subscriptions, webhooks), admin (users list, roles, impersonate, feature toggles), search (query endpoints, autocomplete), upload (multipart, presigned URLs, avatar/asset), notifications (push subscribe, email prefs), websockets/realtime.
9. Rank groups by impact: auth > payment/billing > admin > upload > user/profile > search > notifications. Your testing time follows this ranking — this is the time-pass filter applied to the whole API surface.
10. For each group, note the sensitive-object smell: endpoints returning other users' data, bulk export endpoints, endpoints taking IDs in the path (IDOR candidates), endpoints with `role`/`isAdmin` in request or response.

## Step 5 – Hunt old API versions

11. Version inventory: grep for `/v1/`, `/v2/`, `/v3/`, `/beta/`, `/staging/`, `/dev/`, `/internal/`, `/legacy/`, `api-version`, `X-API-Version`, `?version=`, `?apiVersion=`. Record every versioned prefix and which endpoints exist under each.
12. For every v2 (current) endpoint, construct its v1 (old) twin by path substitution. Check whether the v1 twin is referenced anywhere in JS or responds live — unreferenced-but-live old versions are the regression goldmine.
13. Inventory version-signaling headers/params: `X-API-Version: 1`, `Accept: application/vnd.app.v1+json`, `?api_version=1`. Some APIs version by header alone — the path never changes, so path-only hunting misses them.
14. Also sweep non-versioned legacy: `/api/internal/`, `/api/admin/`, `/api/debug/`, endpoints with `test`/`staging` in the path, and old GraphQL schemas if a schema file or introspection is reachable.

## Step 6 – Version-downgrade test plan

15. Pick a v2 endpoint you can call authenticated (or unauthenticated if the endpoint allows). Record its exact behavior: status, response body shape, and what authorization it enforces (e.g. 403 on another user's ID).
16. Replay the IDENTICAL request against the v1 twin: same method, same params, same auth headers. Compare authorization behavior — the three regression questions: does v1 skip authZ checks? does v1 return MORE data (extra fields, other users' records)? does v1 accept weaker auth (no token, expired token, different role)?
17. Test the version-header variant too: send the v2 request with `X-API-Version: 1` / `?version=1` and observe whether the server downgrades its own behavior while keeping the v2 path.
18. Time-pass filter applies: a v1 that behaves identically to v2 is NEGATIVE — document and move on. Only behavioral divergence (weaker authZ, more data, missing checks) is a lead.

## Step 7 – No-FP verification for every claim

19. Every API claim follows baseline → probe → verify: BASELINE = known-dead endpoint 404 shape on the same host; PROBE = the endpoint/version request; VERIFY = second independent run with a different canary value. A probe matching the baseline 404 shape is NEGATIVE. A probe differing from baseline but explainable by error-handling (generic 500 page, WAF block page) is INCONCLUSIVE until the response is understood against a known-live endpoint's error shape.
20. CONFIRMED requires: baseline differentiation + 2x reproduction + raw request/response pairs saved to <WORKDIR>/raw/api_<endpoint>_probeN.txt. Static-only endpoint listings (in JS, never called live) are CANDIDATE.
21. Auth-walled endpoints you cannot test are BLOCKED — document the wall (login required, MFA, invite-only) and what credential would unlock it. Never fabricate the other side of a wall.

## Step 8 – Exact commands

Endpoint extraction (regex + verified jsluice):
```bash
cd <WORKDIR>/normalized
grep -rhoE '(axios\.(get|post|put|patch|delete)|fetch\()[^;]{0,120}' . | sort -u > <WORKDIR>/raw/api_calls.txt
grep -rhoE '(baseURL\s*:\s*["'"'"'`][^"'"'"'`]+|/api/v[0-9]+/|/graphql|/api/trpc)' . | sort | uniq -c | sort -rn > <WORKDIR>/raw/api_versions.txt
find . -name '*.js' | jsluice urls -S | jq -r 'select(.url | test("/api/|/graphql|/trpc")) | "\(.url)  <== \(.source // "?")"' | sort -u > <WORKDIR>/raw/api_urls_sourced.txt
```

Baseline / probe / verify trio (replace path with the actual target):
```bash
# BASELINE — known-dead endpoint shape (run once per session)
curl -sk -o /tmp/apibase.txt -w "HTTP %{http_code} | %{size_download}B | %{content_type}\n" \
  "https://<TARGET>/api/v9/definitely-not-real-zz99"
# PROBE — v2 behavior reference (add real auth header when you hold it)
curl -sk -o /tmp/apiv2.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  -H "Authorization: Bearer <TOKEN_IF_HELD>" "https://<TARGET>/api/v2/users/me"
# VERIFY — v1 twin replayed identically; then a second run with a changed canary
curl -sk -o /tmp/apiv1a.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  -H "Authorization: Bearer <TOKEN_IF_HELD>" "https://<TARGET>/api/v1/users/me"
curl -sk -o /tmp/apiv1b.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  -H "Authorization: Bearer <TOKEN_IF_HELD>" "https://<TARGET>/api/v1/users/me?canary=2"
diff /tmp/apiv2.txt /tmp/apiv1a.txt && echo "v1 IDENTICAL TO v2 — likely NEGATIVE"
cp /tmp/apiv1a.txt /tmp/apiv1b.txt <WORKDIR>/raw/ 2>/dev/null; true
```

Version-header downgrade variant:
```bash
curl -sk -o /tmp/apihdr.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  -H "Authorization: Bearer <TOKEN_IF_HELD>" -H "X-API-Version: 1" \
  "https://<TARGET>/api/v2/users/me"
```

Method-anomaly spot checks (state-changing GETs, mass-assignment smells):
```bash
# Suspected state-changing GET found in JS? Compare against the dead-endpoint baseline,
# then re-run with a canary param for the 2x rule. Never trigger destructive actions
# (delete/cancel/refund) without explicit user approval — read-only twins only.
curl -sk -o /tmp/meth1.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  "https://<TARGET>/api/v2/account/deactivate?canary=1"
curl -sk -o /tmp/meth2.txt -w "HTTP %{http_code} | %{size_download}B\n" \
  "https://<TARGET>/api/v2/account/deactivate?canary=2"
diff /tmp/apibase.txt /tmp/meth1.txt >/dev/null && echo "MATCHES DEAD BASELINE — NEGATIVE"
```

Bulk twin-generation for the downgrade sweep:
```bash
# Build v1 twins from the v2 endpoint list you extracted; probe each, diff vs v2 behavior
grep -oE '/api/v2/[a-zA-Z0-9/_-]+' <WORKDIR>/raw/api_urls_sourced.txt | sort -u \
  | sed 's|/api/v2/|/api/v1/|' > <WORKDIR>/raw/v1_twins.txt
wc -l <WORKDIR>/raw/v1_twins.txt
```

## Step 9 – Completion checklist

- [ ] Base URLs extracted and env vars resolved to literal values
- [ ] Auth-header mechanics documented per API client
- [ ] Method-mapped endpoint table built (METHOD | path | params | auth)
- [ ] Endpoints grouped by functionality and ranked auth > payment > admin > upload > profile > search > notifications
- [ ] Old-version inventory complete (path versions, header versions, legacy/internal paths)
- [ ] v1 twins constructed for v2 endpoints; live-vs-referenced status recorded
- [ ] Downgrade tests run: identical replay v2→v1, plus version-header variant
- [ ] Every claim verified baseline → probe → 2x repro; raw pairs in <WORKDIR>/raw/
- [ ] v1 twins that 404 identically to the dead baseline marked NEGATIVE (not retried endlessly)
- [ ] Method anomalies documented; no destructive action triggered without approval
- [ ] Verdicts assigned: CONFIRMED / INCONCLUSIVE / CANDIDATE / NEGATIVE / BLOCKED

### Review

A reviewer must verify: (a) the dead-endpoint baseline was recorded before any probe and every verdict references it; (b) no endpoint was marked CONFIRMED from JS strings alone — live reproduction with saved raw pairs is mandatory; (c) v1 twins were replayed with IDENTICAL auth/params, not weaker requests that prove nothing; (d) BLOCKED endpoints name the credential that would unlock them; (e) every CONFIRMED downgrade states verbatim what v1 leaks that v2 withholds, with values redacted. *Which v1 twin diverged from v2 — weaker authZ, more data, or missing checks?* *Which endpoint group holds the most IDOR-shaped paths, and are they reachable unauthenticated?* *Did any "old version" turn out to be a 404-shaped twin — and was it correctly marked NEGATIVE?* "Done" = <WORKDIR>/api_map.md exists with all four sections and a verdict on every downgrade test.

## Step 10 – Evidence standard (no false positives)

An API finding is CONFIRMED only with baseline differentiation, two independent reproductions, and raw pairs on disk. A versioned endpoint that exists in JS but was never called live is CANDIDATE. Identical v1/v2 behavior is NEGATIVE. Error pages that merely differ from the 404 baseline are INCONCLUSIVE until the error is understood against a known-live endpoint's error shape. Auth walls are BLOCKED, documented with the required credential. Secrets (tokens, keys) in JS or responses are redacted in reports and never live-tested without explicit user approval.

## Step 11 – Finished artifact & handoff

Finished artifact: `<WORKDIR>/api_map.md` — four sections: (1) base URLs + auth mechanics, (2) method-mapped endpoint tables grouped by functionality with params and rank, (3) old-version inventory (path/header/legacy), (4) version-downgrade test results — each test with baseline, probe, verify outputs and a verdict (CONFIRMED/INCONCLUSIVE/NEGATIVE/BLOCKED) plus evidence file paths.

Section 4 rows use this fixed format so the next skill can parse them at a glance:

- `| v2 endpoint | v1 twin | authZ delta | data delta | verdict | evidence |`
- Example: `| GET /api/v2/users/{id} | GET /api/v1/users/{id} | v1 skips owner check | v1 returns email, phone, internal_notes | CONFIRMED | raw/api_users_v1_probe1.txt |`

Handoff: **03_content_discovery/api_discovery** takes the versioned APIs and legacy paths into swagger/openapi probing and active fuzzing — hand it the full section 3 inventory, not just the CONFIRMED rows, because undiscovered v1 surface is its fuzzing fuel. **report_output** consumes CONFIRMED items only, with the saved raw pairs as evidence.
