---
name: framework-tech
description: >
  Fingerprints the target's exact frontend framework, version, build tooling, and rendering mode from its own HTML, headers, and bundles — precision matters because this single file decides which app-specific paths exist in Pipeline 2. USE THIS SKILL whenever the user wants to know what framework a site is built with, fingerprint the tech stack, or tell webpack from vite. Trigger on: "what framework is this built with", "fingerprint the tech stack", "webpack or vite". This skill produces the targeting map – the 03_content_discovery/app_specific_files skill fires it.
---

# Framework & Tech Analysis

You are operating as the world's best bug bounty hunter and red teamer. Your job is to fingerprint the exact framework and build tooling so precisely that every framework-specific path, manifest, and default file probed in Pipeline 2 is chosen from evidence — never from a generic fingerprinter's guess.

## Step 1 – Gather inputs

- Fresh fetch of `https://<TARGET>/` — save the HTML AND the response headers to disk
- `<WORKDIR>/normalized/` — bundle content markers
- `<WORKDIR>/inventory_final.json` — bundle filenames are markers too (`main.<hash>.js` vs `_next/static/` vs `_nuxt/`)
- `<WORKDIR>/sourcemaps/` — `webpack://` vs vite-style `sources[]` prefixes fingerprint the build tool
- `<WORKDIR>/raw/*.js` — pre-normalization copies, in case normalization stripped comments

Check first: read the homepage HTML before grepping anything. A `__NEXT_DATA__` script tag or an empty `<div id="root">` tells you more in ten seconds than a hundred greps.

## Step 2 – Framework marker sweep

2.1 React: `react-dom` strings, `__REACT_DEVTOOLS_GLOBAL_HOOK__`, `data-reactroot`, `createRoot` (React 18+). STRONG when the devtools hook or `data-reactroot` appears.
2.2 Vue: `__VUE__`, `vue.runtime.esm`, `data-v-` scoped attributes, `__vue__` on DOM nodes.
2.3 Angular (2+): `ng-version="x.y.z"` on the root element, `zone.js`, `_ngcontent` attributes. AngularJS (1.x): `ng-app`, `angular.module`, `ng-controller` — a different beast with its own sink patterns; never conflate the two.
2.4 Next.js: `__NEXT_DATA__` JSON blob, `/_next/static/` asset paths, `_buildManifest.js` references. Nuxt: `__NUXT__` state blob, `/_nuxt/` paths. Remix: `@remix-run`, `__remixManifest`. Gatsby: `___gatsby`, `/page-data/` JSON paths. Svelte: `svelte/internal`, `.svelte-` scoped classes. Ember: `EmberENV`, `assets/vendor-`. Backbone: `Backbone.Model.extend`.
2.5 Score every marker STRONG (framework-specific global, data attribute, or asset path) vs WEAK (a string that could be a mere dependency — e.g. a React widget inside an Angular shell).
2.6 Multiple STRONG markers from different frameworks → hybrid app or migration in progress. Determine which framework actually bootstraps the app (whose init call runs on load); mark the other as embedded/legacy with its own version. Only WEAK markers → INCONCLUSIVE until the bootstrap call is found; say so.

## Step 3 – Build-tooling markers

3.1 webpack: `webpackChunk`, `__webpack_require__`, `webpack://` sourcemap prefixes, content-hashed chunk filenames.
3.2 Vite: `import.meta.env`, `assets/index-<hash>.js` naming, vite preload markers. (`/@vite/client` is dev-only — its absence in prod means nothing.)
3.3 esbuild: characteristic minification style plus absence of a webpack runtime; Rollup: `chunk-` filenames and rollup chunk comments; Parcel: `parcelRequire`.
3.4 Confirm from sourcemaps: `webpack:///./src` vs vite-style file URLs vs plain relative paths — the sourcemap prefix is the most reliable build-tool fingerprint you have.

Why it matters: the build tool decides chunk naming, manifest filenames, and whether sourcemaps ship in production — each one is a direct content-discovery input.

## Step 4 – Rendering mode: SSR vs CSR

4.1 SSR signals: `__NEXT_DATA__` with populated `props.pageProps`, `__NUXT__` state blob, real content inside the root div before JS runs, `window.__INITIAL_STATE__`.
4.2 CSR signals: empty `<div id="root"></div>` / `<div id="app"></div>`, content appearing only after JS executes, `noscript` fallback text.
4.3 Hybrid: shell SSR'd, inner routes CSR — note it per route if the evidence differs (homepage SSR, `/app/*` CSR is a common split).

Rendering mode decides your discovery strategy: SSR → server-rendered state blobs leak data shapes and API contracts; pure CSR → the bundles ARE the app, and every unknown path 200s on the SPA fallback, so baseline calibration is critical before claiming any discovered path is real.

## Step 5 – Backend hints

5.1 Headers: `X-Powered-By`, `Server`, framework cookies (`next-auth`, Laravel `XSRF-TOKEN`, Django `csrftoken`).
5.2 Error pages: request a 404/500 on an API-ish path and read the body — framework error pages name the backend outright.
5.3 Conventions: `/graphql`, REST plural-noun routes, `/_next/data/` JSON routes (Next.js data fetching), `/page-data/` (Gatsby), `/.netlify/` functions.

If the backend hides behind a CDN with sanitized headers → say so explicitly; never guess the backend from the frontend framework alone.

## Step 6 – Version pinning and conflict resolution

6.1 Pin the framework version from evidence: `ng-version="14.2.0"`, React banner or `react-dom` package path in sourcemaps. (`__NEXT_DATA__`'s `buildId` is NOT a version — never confuse the two.)
6.2 Pin the build-tool major only when evidence exists (webpack 5 vs 4 runtime patterns); otherwise record "webpack (major unknown)".
6.3 Write every conclusion as: choice, version, the exact evidence quote (marker string + file), confidence (HIGH / MEDIUM / LOW).

## Step 7 – Write the annotated tech_choices.md

Every choice gets a "why it matters for content discovery" annotation with concrete paths — this is the whole point of the file:

- Next.js → probe `/_next/static/<buildId>/_buildManifest.js` and `/_ssgManifest.js` for the full page list; `/_next/data/<buildId>/<route>.json` for data routes
- Nuxt → `/_nuxt/` payload files and build manifest; per-route `/_payload.js`
- Angular → `/assets/i18n/*.json` locale files, `3rdpartylicenses.txt`
- Gatsby → `/page-data/<route>/page-data.json` per route
- Remix → build manifest and `__remixManifest` route list
- SPA fallback (any CSR app) → every unknown path returns 200 with `index.html`; baseline calibration is critical before claiming any discovered path is real
- Sourcemaps shipped in prod → re-run library-analysis against them; every `sources[]` entry is a file path

Table format: `| Choice | Version | Evidence | Confidence | Why it matters for content discovery |` — one row per choice, no choice without its annotation.

## Step 8 – Exact commands

```bash
# BASELINE — homepage HTML + headers + dead-path signature
curl -sS -D /tmp/levi_home.hdrs -o /tmp/levi_home.html \
  -w 'code=%{http_code} size=%{size_download}\n' 'https://<TARGET>/'
curl -sS -o /tmp/levi_dead.html -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/levi-dead-path-9f3a2c1d'
md5sum /tmp/levi_home.html /tmp/levi_dead.html
```

```bash
# PROBE — framework markers across homepage and bundles
cd <WORKDIR>
for pat in '__NEXT_DATA__' '__NUXT__' '__REACT_DEVTOOLS_GLOBAL_HOOK__' '__VUE__' \
           'ng-version' 'ng-app' '___gatsby' '__remixManifest' 'svelte/internal'; do
  echo "== $pat =="
  grep -rl "$pat" normalized/ raw/ 2>/dev/null | head -5
done
grep -oE 'ng-version="[^"]+"' /tmp/levi_home.html | head -3
grep -oE '/_next/static/[^" ]+' /tmp/levi_home.html | head -5
grep -oE '/_nuxt/[^" ]+' /tmp/levi_home.html | head -5
```

```bash
# PROBE — build-tooling markers + sourcemap prefix (most reliable signal)
cd <WORKDIR>
for pat in 'webpackChunk' '__webpack_require__' 'import.meta.env' 'parcelRequire'; do
  echo "== $pat =="; grep -rl "$pat" normalized/ 2>/dev/null | head -3
done
for m in sourcemaps/*.map; do jq -r '.sources[0]' "$m" 2>/dev/null; done \
  | sort | uniq -c | head -10
```

```bash
# VERIFY — Next.js manifests; ONLY if Next.js was confirmed in Step 2
# Replace <BUILD_ID> with the buildId value from __NEXT_DATA__
curl -sS -o /tmp/levi_buildmanifest.js -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/_next/static/<BUILD_ID>/_buildManifest.js'
curl -sS -o /tmp/levi_ssgmanifest.js -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/_next/static/<BUILD_ID>/_ssgManifest.js'
# Real page list = a 200 whose size+hash does NOT match the dead-path baseline
```

```bash
# VERIFY — backend hint via error page (judge against the baseline signature)
curl -sS -o /tmp/levi_err.html -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/api/levi-no-such-endpoint-9f3a2c1d'
head -c 600 /tmp/levi_err.html
```

## Step 9 – Completion checklist

- [ ] Homepage HTML + headers fetched and saved to disk
- [ ] Framework marker sweep run across homepage, normalized bundles, and raw bundles
- [ ] Every marker scored STRONG / WEAK with the exact string quoted
- [ ] Conflicts resolved via the bootstrap test; embedded/legacy frameworks marked
- [ ] Build tooling fingerprinted and confirmed via the sourcemap prefix
- [ ] Rendering mode determined (SSR / CSR / hybrid) with evidence
- [ ] Backend hints recorded, or explicitly marked hidden behind the CDN
- [ ] Framework version pinned from evidence; buildId never mistaken for a version
- [ ] `<WORKDIR>/tech_choices.md` written, every row carrying its content-discovery annotation

### Review
A reviewer must verify: each framework choice quotes its exact marker string and file; no framework is claimed from a WEAK marker alone; the buildId/version distinction holds; every tech_choices.md row has a "why it matters" annotation with concrete paths.

*If two frameworks left STRONG markers, which one actually bootstraps the app — and how did you prove it?*
*Which framework-specific manifest would you fetch first in content discovery, and what dead-path check guards it?*
*What did you mark INCONCLUSIVE rather than guessing — and what single test would resolve it?*

Done = `<WORKDIR>/tech_choices.md` exists on disk with every choice annotated for content discovery.

## Step 10 – Evidence standard (no false positives)

- Baseline every live check against the known-dead path: a manifest or page fetch matching the dead-path signature (status + size + hash) is the SPA fallback, not a discovery.
- Framework claims require a STRONG marker quoted verbatim with its file; WEAK-only evidence stays INCONCLUSIVE.
- Verdicts: CONFIRMED (STRONG marker + bootstrap evidence), INCONCLUSIVE (ambiguous, resolving test named), NEGATIVE (marker absent where it must appear — e.g. no `__NEXT_DATA__` on a claimed Next.js app), BLOCKED (could not fetch, exact blocker documented).
- Version pins are CANDIDATE until the marker quote is in the file.

## Step 11 – Finished artifact & handoff

Artifact: `<WORKDIR>/tech_choices.md` — table `| Choice | Version | Evidence | Confidence | Why it matters for content discovery |`, one row per choice (framework, build tool, rendering mode, backend hints), no row without its annotation.

Handoff: `03_content_discovery/app_specific_files` takes this file as REQUIRED input — every tech-derived path it probes (build manifests, payload files, locale JSON, page-data) comes from the "why it matters" column. `bugbounty_report_intel` consumes the framework identity for framework-specific writeup patterns (e.g. Next.js `/_next/data` exposure, Angular i18n leaks).
