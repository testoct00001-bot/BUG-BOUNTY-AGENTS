---
name: params-routes
description: >
  Extracts the full route table, parameter inventory, admin paths, and feature flags from the <TARGET> JS bundles into a ranked attack map. USE THIS SKILL whenever the user wants to extract routes and params from JS, find admin paths in the bundle, run a feature flag analysis. Trigger on: "extract routes and params from JS", "find admin paths in the bundle", "feature flag analysis". This skill produces the ammunition – the api_analysis skill and 03_content_discovery/generic_routes fire it.
---

# Params & Route Analysis

You are operating as the world's best bug bounty hunter and red teamer. Your job is to extract the app's full route table and parameter inventory to surface admin paths, hidden feature flags, and statistically-vulnerable parameters that generic crawlers never see.

## Step 1 – Gather inputs

- <WORKDIR>/normalized/ — all route-extraction regex passes run here; never trust a single minified raws read for path literals.
- <WORKDIR>/sourcemaps/ — original source paths and variable names survive here; use them to resolve framework-specific route structures.
- <WORKDIR>/inventory_final.json — confirm which bundle is the app shell vs lazy-loaded chunks (routes hide in lazy chunks).
- Build manifests if present: asset-manifest.json, __NEXT_DATA__ payloads, .next/build-manifest.json, Nuxt .nuxt routes. Grep normalized/ for `__NEXT_DATA__`, `buildManifest`, `asset-manifest`.
- jsluice URL output: `find <WORKDIR>/normalized -name '*.js' | jsluice urls` → JSONL, parse with jq. Verified flags only (`-S/--include-source`, `-R/--resolve-paths <url>`); anything else — verify with `jsluice --help` first.
- Baseline: a known-dead path on <TARGET> (record exact 404 status/body). Every admin/flag route probe gets compared against it.
- Decision rule: if the route table is empty after the framework passes, the app is likely server-rendered or the routes live in a chunk inventory_final.json flagged as lazy — re-run the passes with the chunk files included before concluding there are no client routes.

Worked param-flow example (the unit of value this skill produces):

- Param `next` read at `auth.js:88` via `searchParams.get("next")`, flows into `window.location = next` at `auth.js:104` on the unauthenticated `/login` page.
- Row in the inventory: `next | count 14 | open-redirect | auth.js:88 → location assignment auth.js:104 | unauthenticated /login page | TOP PRIORITY`.
- Contrast: param `theme` read at `settings.js:12`, flows into a CSS class allowlist (`["dark","light"].includes(theme)`) on an authenticated page → `theme | count 3 | allowlisted, no sink | authenticated | NEGATIVE candidate`.
- The inventory is not a wordlist — every row must say where the param is READ, where it FLOWS, and whether the page is reachable unauthenticated. Rows missing the flow column are incomplete.

## Step 2 – Extract the route table by framework

1. Detect the router: `createBrowserRouter` / `<Route path=` → react-router; `routes:` array with `path:`/`component:` → vue-router; `RouterModule.forRoot` / `loadChildren` → Angular; `app/` directory conventions + `page.js` → Next.js app router; `pages/` → Next pages / Nuxt; `createBrowserRouter` + `.data` loaders → Remix.
2. React: regex for `path:\s*["'`]([^"'`]+)["'`]`, `<Route[^>]*path=["']([^"']+)`, and lazy `import(` targets — lazy chunks hold the routes generic scans miss.
3. Vue: extract the full `routes` array — record `path`, `name`, `meta.requiresAuth`/`meta.roles`, and per-route guards. Guard metadata is your auth map for free.
4. Angular: pull `RouterModule.forRoot([...])` and `forChild` arrays plus `canActivate` guards; note `loadChildren` chunk names and map them to files in inventory_final.json.
5. Next.js: parse `__NEXT_DATA__` (`page`, `query`, `buildId`) and build manifests for the complete page list; Nuxt: parse the `pages/` route generation; Remix: map the `routes/` directory to URL paths.
6. Normalize everything into ONE table: `path | framework | lazy_chunk | auth_guard | reachable_unauth (yes/no/unknown)`. De-dupe parameterized variants (`/user/:id` vs `/user/123`).

## Step 3 – Hunt admin paths and privileged routes

7. Keyword-sweep the route table for: `/admin`, `/internal`, `/debug`, `/console`, `/ops`, `/manage`, `/superuser`, `/staff`, `/backoffice`, `/godmode`, `/impersonate`. Also sweep for component names containing Admin/Internal/Debug even when the URL path looks innocent.
8. For every hit, read the surrounding guard logic: `isAdmin`, `canAccess`, `role ===`, `hasPermission(`. Record whether the guard is client-side-only (UI hiding) or backed by a server 401/403 — client-side-only gates are leads, not walls.
9. Cross-check each admin/feature route live: BASELINE (dead path 404 shape) → PROBE (`curl` the route unauthenticated) → compare. A 200 with app content vs the 404 shape = unauthenticated access or a UI-only gate; a 302 to login = real server gate.
10. Prioritize: routes whose guards reference roles/permissions in JS but return 200 unauthenticated are top-tier leads. Routes that 403/302 are NEGATIVE for direct access but stay as candidates for IDOR/BOLA if they take IDs.

## Step 4 – Feature-flag and hidden-functionality mining

11. SDK markers: grep for `unleash`, `launchdarkly`, `flagsmith`, `split.io`, `growthbook`, `statsig`, `useFlag(`, `useFeatureFlag(`, `isFeatureEnabled(`. Extract every flag KEY referenced — each key is a potential hidden feature.
12. Query-param flags: `?feature=`, `?flag=`, `?experiment=`, `?variant=`, `?beta=` reads via `URLSearchParams.get`. For each, find where the value is consumed — a flag that toggles an admin panel or debug mode is a live lead.
13. Storage flags: `localStorage.getItem`/`sessionStorage.getItem` keys that gate features (`ff_`, `feature_`, `beta_`, `debug_`). These are client-settable — note them as trivially toggleable.
14. Config-embedded flags: JSON blobs in the bundle (`window.__CONFIG__`, `__ENV__`, `runtimeConfig`) containing `features:`, `flags:`, `enabledModules:`. Dump the whole object; flags marked `false`/`disabled` that the code still branches on are worth toggling in the browser.

## Step 5 – Interesting comments and leaked internals

15. Harvest comments: `TODO`, `FIXME`, `HACK`, `XXX`, `console.log(`, `debugger`, staging URLs, internal hostnames (`*.internal`, `*.corp`, `*.local`, `staging-*`, `dev-*`). One `// TODO: remove before prod` has ended more hunts than a week of fuzzing.
16. Internal hostnames and staging URLs go into a leak list with the file/line — they are recon leads (SSRF targets, cookie-scope questions), not findings until probed.
17. `console.log` statements that print tokens, user objects, or API responses mark PII-leak candidates; verify in the live app's devtools, never from the bundle alone.

## Step 6 – Parameter inventory with vuln-class annotation

18. Extract parameters from three sources: jsluice `urls` output query strings, `URLSearchParams.get("...")` / `.getAll(` calls, and route params (`:id`, `{id}`, `[slug]`). Merge and count occurrences across the bundle — frequency hints at how central a param is.
19. Annotate every param with its statistically-likely vuln class:
    - Open redirect: `redirect`, `url`, `next`, `return`, `returnUrl`, `callback`, `cb`, `continue`, `dest`
    - LFI / path traversal: `file`, `path`, `template`, `theme`, `page`, `include`
    - SSTI: `template`, `theme`, `name` (where rendered into templates)
    - IDOR / BOLA: `id`, `userId`, `accountId`, `email`, `orderId`
    - Auth bypass: `token`, `key`, `debug`, `test`, `admin`, `role`, `preview`, `bypass`
    - Locale/Lang injection: `lang`, `locale` (XSS via locale files, cache poisoning)
20. For each annotated param, record: where it is read (file:line), where it flows (the request it lands in — this feeds api_analysis), and a reachability note (unauthenticated page? admin-only?). Params on unauthenticated pages with redirect/file semantics go to the top of the probe queue.

## Step 7 – Exact commands

Route-table extraction passes (run over normalized/):
```bash
cd <WORKDIR>/normalized
grep -rhoE 'path:\s*["'"'"'`][^"'"'"'`]+["'"'"'`]' . | sort -u > <WORKDIR>/raw/route_paths.txt
grep -rhoE '<Route[^>]*path=["'"'"'][^"'"'"']+' . | sort -u >> <WORKDIR>/raw/route_paths.txt
grep -rhoE '(createBrowserRouter|RouterModule\.forRoot|useFlag|useFeatureFlag)' . | sort | uniq -c | sort -rn
```

Admin + flag + comment sweeps:
```bash
grep -rhoiE '/(admin|internal|debug|console|ops|manage|backoffice|impersonate)[a-zA-Z0-9/_-]*' . | sort -u > <WORKDIR>/raw/admin_paths.txt
grep -rhoE '(unleash|launchdarkly|flagsmith|growthbook|statsig|split\.io)' . | sort | uniq -c
grep -rhoE '(TODO|FIXME|HACK|XXX):[^"\n]{0,120}' . | sort -u > <WORKDIR>/raw/comments_of_interest.txt
grep -rhoE 'https?://[a-zA-Z0-9.-]*\.(internal|corp|local|staging)[a-zA-Z0-9./_-]*' . | sort -u > <WORKDIR>/raw/internal_hosts.txt
```

Param inventory from jsluice URLs (verified usage):
```bash
find . -name '*.js' | jsluice urls | jq -r '.url' | grep -oE '[?&][a-zA-Z_]+=' | tr -d '?&=' | sort | uniq -c | sort -rn > <WORKDIR>/raw/param_counts.txt
grep -rhoE 'URLSearchParams[^;]{0,80}|searchParams\.get\(["'"'"'][^"'"'"']+' . | sort -u > <WORKDIR>/raw/searchparams_reads.txt
```

Baseline / probe / verify for an admin route:
```bash
curl -sk -o /tmp/base404.html -w "%{http_code} %{size_download}\n" "https://<TARGET>/no-such-route-zz99"
curl -sk -o /tmp/adm.html -w "%{http_code} %{size_download}\n" "https://<TARGET>/admin"
diff -q /tmp/base404.html /tmp/adm.html || echo "DIFFERS FROM 404 BASELINE — investigate"
```

Next.js / Nuxt manifest parsing (when the bundles reference them):
```bash
grep -rhoE '__NEXT_DATA__[^<]{0,200}' <WORKDIR>/raw/*.html 2>/dev/null | head -5
find <WORKDIR>/sourcemaps -name '*build-manifest*' -o -name '*asset-manifest*' | head
python3 -c "
import json,glob
for f in glob.glob('<WORKDIR>/sourcemaps/**/*build-manifest*', recursive=True):
    d=json.load(open(f)); pages=list(d.get('pages',{}).keys()); print(f, len(pages))
" 2>/dev/null | head
```

Feature-flag toggle test (localStorage-gated flags — verify live, then record):
```bash
# In the live browser console on https://<TARGET>/ :
#   localStorage.setItem("ff_admin_panel","true"); location.reload();
# Baseline: screenshot/record behavior with the flag absent, then with it set.
# A UI change = CANDIDATE lead for feature_map; no change = NEGATIVE for that flag.
```

Admin-route auth comparison (three-way: dead baseline vs route vs route-with-junk-token):
```bash
curl -sk -o /tmp/adm2.txt -w "%{http_code} %{size_download}\n" \
  -H "Authorization: Bearer invalid-junk-token" "https://<TARGET>/admin/users"
echo "--- 200-unauthenticated here + 404-baseline elsewhere = client-side-only gate (LEAD)"
```

## Step 8 – Completion checklist

- [ ] Router framework detected and documented
- [ ] Full route table extracted (including lazy-chunk routes) → normalized into path|framework|guard table
- [ ] Admin-path sweep done; every hit checked for client-side-only vs server-backed guards
- [ ] Each admin/feature route probed live vs the 404 baseline (baseline recorded first)
- [ ] Feature-flag SDK markers, query-param flags, storage flags, and config-embedded flags extracted
- [ ] Comments of interest harvested (TODO/FIXME/HACK/staging URLs/internal hostnames)
- [ ] Param inventory built with occurrence counts from jsluice + URLSearchParams + route params
- [ ] Every param annotated with suspected vuln class + reachability note
- [ ] Every inventory row has read-location AND flow-destination (no orphan rows)
- [ ] Raw evidence files saved under <WORKDIR>/raw/

### Review

A reviewer must verify: (a) lazy-loaded chunks were included — routes in async chunks are the ones crawlers miss; (b) no admin path was declared "vulnerable" without a live baseline-vs-probe comparison; (c) every param's suspected vuln class matches where the param actually flows, not just its name; (d) internal hostnames are listed as recon leads, not findings; (e) every "client-side-only gate" claim has the three-way comparison (404 baseline vs unauthenticated probe vs junk-token probe) saved as raw output. *Which admin route has a client-side-only guard — and what did the live probe return vs the 404 baseline?* *Which feature flag can you toggle from localStorage, and what UI does it unlock?* *Of your top-5 params by count, which sit on unauthenticated pages?* "Done" = <WORKDIR>/routes_params.md exists with all five sections populated.

## Step 9 – Evidence standard (no false positives)

An "exposed admin route" is CONFIRMED only when the live probe returns app content or a 200 that differs from the known-dead 404 baseline — a route string in JS is CANDIDATE. 403/302-to-login is NEGATIVE for direct unauthenticated access (still log the guard type; it may be IDOR-relevant). Feature flags are CANDIDATE until toggled live with an observed behavior change. Params are CANDIDATE until the request they feed is replayed with a canary and the reflection/sink is observed twice. Static-only route/param findings never get reported as vulnerabilities.

## Step 10 – Finished artifact & handoff

Finished artifact: `<WORKDIR>/routes_params.md` — five sections: (1) route table (path | framework | lazy chunk | auth guard | unauth reachability), (2) admin paths with guard analysis + probe verdicts, (3) feature flags (SDK keys, query params, storage keys, config flags), (4) comments of interest + internal hostnames, (5) parameter inventory (param | count | suspected vuln class | read location | reachability note).

Handoff: **api_analysis** consumes the param inventory (params → the requests they feed) as its endpoint-testing fuel. **03_content_discovery/generic_routes** takes the admin paths and flag-gated routes into active fuzzing. High-value admin/flag leads also feed **feature_map** as hunt leads.
