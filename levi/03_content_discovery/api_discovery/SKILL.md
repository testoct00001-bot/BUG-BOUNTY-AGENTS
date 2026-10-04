---
name: api-discovery
description: >
  Maps the target's API surface through versioned path probing, spec-document discovery (swagger/openapi), GraphQL introspection checks, /.well-known enumeration, per-endpoint HTTP method enumeration, and version-downgrade tests — all under the same baseline discipline as route discovery. USE THIS SKILL whenever the user wants to map hidden APIs, find old API versions, or enumerate allowed HTTP methods on a target. Trigger on: "API discovery", "find hidden APIs", "swagger discovery", "GraphQL introspection", "enumerate HTTP methods", "old API versions", "version downgrade". This skill produces the verified API surface map – the js-to-wordlist skill fires it further by tokenizing discovered API paths into custom wordlist entries.
---

# API Discovery

You are operating as the world's best bug bounty hunter and red teamer. Your job is to map the API surface the developers forgot to document: the `/v1` that still answers next to `/v3`, the `/openapi.json` with admin operations, the GraphQL endpoint with introspection on, the `/.well-known/` files leaking configuration, the endpoint that accepts DELETE when the docs say GET-only. APIs are where the money bugs live — IDORs, broken authz, mass assignment — and you can't test what you haven't mapped.

## Step 1 – Gather Inputs

- `<TARGET>` base URL. One host per run.
- `discovery/baseline.txt` — reuse the host baseline (recalibrate if stale).
- `02_js_analyze/api_map.md` — ALL API calls grouped by functionality, including
  old API versions spotted in JS. This is your seed list; every endpoint here gets
  method-enumerated.
- `discovery/generic_routes.txt` — CONFIRMED admin/API-ish routes (mount spec
  probes on each: `/admin/openapi.json`, `/admin/graphql`, …).
- `custom_list.txt` (if `js-to-wordlist` already ran) — API-ish tokens become
  versioned-path candidates.

Division of labor: consumes the API map + route inventory; produces
`discovery/api_surface.md` (the verified API surface: versions, spec docs,
GraphQL status, method matrix, well-known files) and raw probe logs.
Skip when `api_map.md` shows no API surface and no spec markers exist (a static
brochure site has no API to discover — say so), or when a previous
`api_surface.md` covers the same host + API version set.

## Step 2 – Enumerate API Versions

APIs version; old versions rot. For each API root observed in `api_map.md`
(e.g. `/api/v3/users` → root `/api/`):
1. Probe `/api/`, `/api/v1/`, `/api/v2/`, `/api/v3/` (+ v0, v4 if the observed
   version is high — rot exists on both sides of current).
2. Version-downgrade test: take a known-good endpoint (`/api/v3/users/me`) and
   replay it against `/api/v2/users/me`, `/api/v1/users/me`. A 200 with data on
   an old version = CONFIRMED version-downgrade surface (old versions often lack
   newer authz checks — that's the follow-up track's prize, this skill maps it).
3. Unversioned alias: probe `/api/users/me` alongside `/api/v3/users/me` —
   unversioned aliases sometimes route to the oldest handler.
4. Non-`/api` roots from JS: `/rest/`, `/v1/`, `/graphql` treated as its own root,
   `/internal/api/`. Every root gets the version battery.

Baseline discipline applies per root: some hosts return different baselines for
`/api/*` (JSON 404 `{"error":"not found"}`) vs `/` (HTML). Calibrate a dead path
UNDER EACH ROOT (`/api/v9/levi-dead-<rand>`) and compare within the root.

## Step 3 – Hunt Spec Documents

Spec docs are the API's own map — find them first, mine them second:
- Swagger/OpenAPI: `/swagger`, `/swagger-ui`, `/swagger-ui.html`,
  `/swagger-ui/index.html`, `/api-docs`, `/v2/api-docs`, `/v3/api-docs`,
  `/openapi.json`, `/openapi.yaml`, `/swagger.json`, `/api/openapi.json`,
  `/api/swagger.json`, `/redoc`, `/api/redoc`, `/docs`, `/api/docs`
- Mount on CONFIRMED admin routes: `/admin/openapi.json`, `/admin/api-docs`
- On a hit: verify it parses as a spec (has `openapi:`/`swagger:` key and a
  `paths:` object — an HTML page titled "Swagger" with no spec JSON is a UI
  shell, still worth logging as INFO but not as a spec win). Extract every path
  + method into the surface map and feed unprobed ones back as candidates.
- Redoc/Scalar/elements UIs: same treatment — the UI proves the spec URL exists
  nearby; find the JSON.

## Step 4 – GraphQL: Find It, Fingerprint It, Test Introspection

- Discovery probes: `/graphql`, `/graphiql`, `/playground`, `/api/graphql`,
  `/v1/graphql`, `/console/graphql` — GET first (GraphiQL UI?), then POST.
- Fingerprint with a minimal POST: `{"query":"{__typename}"}` with
  `Content-Type: application/json`. A JSON response with `data` = GraphQL
  endpoint CONFIRMED (even if errors — errors still prove the parser).
- Introspection test: POST `{"query":"{__schema{queryType{name}}}"}`. Full schema
  back = introspection ON (high-value finding — the schema IS the map; save it,
  don't paste it whole into chat). Error "introspection disabled" = hardened,
  log as INFO.
- GET with `?query={__typename}` — some endpoints only bind GET.
- Batching test: `[{"query":"{__typename}"},{"query":"{__typename}"}]` — array
  accepted = batching enabled (rate-limit/amplification lead for the next track).
- Never run destructive mutations. Discovery maps; it doesn't mutate.

## Step 5 – Enumerate HTTP Methods per Endpoint

For every CONFIRMED endpoint (from `api_map.md` seeds + spec-extracted paths +
GraphQL): send OPTIONS, then GET, POST, PUT, PATCH, DELETE, HEAD with an empty/minimal
body. Record the full matrix: status + `Allow` header + body marker per method.
What you're hunting:
- `Allow` header listing more than docs admit (especially PUT/PATCH/DELETE).
- A method returning 200/201 where only GET was expected (unadvertised write).
- 405 with an `Allow` header vs 404/501 without — the difference between
  "method not allowed here" (endpoint exists) and "nothing here."
- Method-override headers (`X-HTTP-Method-Override: PUT` on a POST) — note as a
  lead for the bypass track, don't exploit here.
Baseline: the method matrix of a known-dead path under the same root — some hosts
answer OPTIONS 200 on everything (CORS middleware), which is noise, not signal.

## Step 6 – Enumerate /.well-known/

Probe: `/.well-known/change-password`, `/.well-known/security.txt`,
`/.well-known/openid-configuration`, `/.well-known/assetlinks.json`,
`/.well-known/apple-app-site-association`, `/.well-known/jwks.json`,
`/.well-known/oauth-authorization-server`, `/.well-known/host-meta`,
`/.well-known/nodeinfo`. Verify content-kind (JSON parses? `security.txt` has
`Contact:`?). `openid-configuration` and `jwks.json` are high-value: they leak
the auth architecture — map the `issuer`, `jwks_uri`, token endpoints into the
surface map as auth-leads.

## Step 7 – Reproduce, Save Raw Pairs, Build the Surface Map

2× reproduction for every CONFIRMED item (spec doc, GraphQL endpoint, versioned
hit, method-matrix anomaly, well-known file). Raw pairs to
`discovery/api_surface_raw.md`. Then compile `discovery/api_surface.md`:

```markdown
# API surface — <host> — <date>
## Roots & versions (with downgrade results)
## Spec documents (path | spec-kind | path-count | notes)
## GraphQL (endpoint | introspection on/off | batching | notes)
## Method matrix (endpoint | OPTIONS | GET | POST | PUT | PATCH | DELETE | Allow | anomaly?)
## .well-known (path | content-kind | notes)
## Leads for next track (authz-testable endpoints, batching, version-downgrade hits)
```

## Step 8 – Exact Commands (Copy-Paste)

```bash
TARGET="https://target.example.com"

# 1. Per-root baselines (JSON 404s differ from HTML 404s)
for r in "api/v9/levi-dead-$RANDOM" "v9/levi-dead-$RANDOM"; do
  echo "== /$r =="
  curl -sk -o /tmp/ab -w "status=%{http_code} size=%{size_download}\n" "$TARGET/$r"
  head -c 120 /tmp/ab | tr -d '\n'; echo
done

# 2. Version battery + downgrade test
for v in v0 v1 v2 v3 v4; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 15 "$TARGET/api/$v/users/me")
  echo "/api/$v/users/me -> $code"; sleep 1
done

# 3. Spec docs
for p in openapi.json swagger.json v3/api-docs api-docs swagger-ui.html api/redoc; do
  out=$(curl -sk -o /tmp/sp -w "%{http_code} %{size_download}" --max-time 15 "$TARGET/$p")
  marker=$(head -c 60 /tmp/sp | tr -d '\n' | cut -c1-50)
  echo "$p -> $out :: $marker"; sleep 1
done
# Verify a spec hit parses:
python3 -c "import json; d=json.load(open('/tmp/sp')); print(d.get('openapi') or d.get('swagger'), len(d.get('paths',{})))"

# 4. GraphQL fingerprint + introspection
curl -sk -X POST "$TARGET/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__typename}"}' --max-time 15 | head -c 300; echo
curl -sk -X POST "$TARGET/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{queryType{name}}}"}' --max-time 15 -o /tmp/intro -w "intro http=%{http_code} size=%{size_download}\n"
head -c 200 /tmp/intro; echo

# 5. Method matrix for one endpoint (repeat per endpoint)
EP="/api/v3/users/me"
for m in OPTIONS GET POST PUT PATCH DELETE HEAD; do
  printf "%-8s " "$m"
  curl -sk -X $m -o /dev/null -D /tmp/mh -w "%{http_code}" --max-time 15 "$TARGET$EP"
  echo " allow=$(grep -i '^allow:' /tmp/mh | tr -d '\r' | head -1)"
  sleep 1
done

# 6. .well-known sweep
for p in change-password security.txt openid-configuration jwks.json assetlinks.json apple-app-site-association oauth-authorization-server; do
  out=$(curl -sk -o /tmp/wk -w "%{http_code} %{size_download}" --max-time 15 "$TARGET/.well-known/$p")
  echo "$p -> $out :: $(head -c 70 /tmp/wk | tr -d '\n')"; sleep 1
done
```

## Step 9 – Completion Checklist

- [ ] Per-root baselines calibrated (`/api/*` JSON-404 vs `/` HTML-404 distinguished)
- [ ] Version battery run on every API root from `api_map.md` + JS-observed roots
- [ ] Version-downgrade test executed on ≥3 known-good endpoints
- [ ] Spec-doc battery probed; every hit verified to parse as a spec (not a UI shell)
- [ ] Spec-extracted paths fed back as new candidates (documented count)
- [ ] GraphQL discovered (or documented absent after the full probe set); fingerprint
      POST + introspection test + GET-variant + batching test all executed
- [ ] Method matrix completed for every CONFIRMED endpoint; `Allow` headers captured
- [ ] `/.well-known/` sweep done; `openid-configuration`/`jwks.json` mapped as auth-leads
- [ ] Every CONFIRMED item reproduced 2×; raw pairs in `discovery/api_surface_raw.md`
- [ ] `discovery/api_surface.md` compiled in the exact section format
- [ ] Review: reviewer re-probes 2 spec hits (verifies JSON parses), 1 GraphQL
      endpoint (re-runs introspection query), and 1 method-matrix anomaly.
      Any item that doesn't reproduce = struck from the surface map.
- Nudge prompts:
  - "You found /v3. Did you check /v1 and /v2, or assume they're dead? Rot lives in old versions."
  - "That 'Swagger UI' page — does /openapi.json behind it actually parse? A shell without a spec is INFO, not a win."
  - "Introspection is on. Did you SAVE the schema to disk, or just admire it in the terminal?"

## Step 10 – Evidence Standard (No False Positives)

- **CONFIRMED** = in-root baseline divergence + content-kind verified (spec parses /
  GraphQL returns `data` / method anomaly reproduces) + 2× reproduction + raw pair.
- **INCONCLUSIVE** = diverges once, flaky, or content ambiguous (HTML on a JSON path).
- **NEGATIVE** = matches in-root baseline; OPTIONS-200-everywhere from CORS
  middleware is NEGATIVE noise, not a method finding.
- **BLOCKED** = documented with observed behavior.
- GraphQL "errors" responses still CONFIRM the endpoint exists (the parser ran) —
  but introspection-OFF is INFO/hardened, not a finding.
- No destructive mutations during discovery. Ever.

## Step 11 – Finished Artifact & Handoff

Done = `discovery/api_surface.md` exists in the exact section format (roots/versions,
specs, GraphQL, method matrix, well-known, leads) with every CONFIRMED item carrying
status + size + marker, plus `discovery/api_surface_raw.md` with raw pairs. Zero
surface = a `NO-API-SURFACE <host> <date>` block with the probe trail proving it.

Handoff: **js-to-wordlist** consumes `api_surface.md` — every discovered path,
version qualifier, and method anomaly becomes tokenized wordlist entries.
**phases-generic-specific** consumes the surface map for the Specific-phase exit
gate. Version-downgrade hits, batching-enabled GraphQL, and unadvertised write
methods go to the next track's lead queue (authz testing is a different pipeline).
