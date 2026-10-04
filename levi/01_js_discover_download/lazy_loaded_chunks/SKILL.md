---
name: lazy-loaded-chunks
description: >
  Detects and downloads lazy-loaded / code-split JavaScript chunks (webpack, Vite, Next.js) that the initial page load never fetches — route-split admin panels, lazy modals, and deferred features hide here. USE THIS SKILL whenever the user wants complete JS coverage, after spider-harvest, or says "catch lazy chunks", "webpack chunks", "code splitting". Trigger on: "lazy loaded js", "webpack chunks", "code split bundles", "next.js chunks", "dynamic imports", "missing chunks". This skill produces raw/chunks/*.js plus a chunk manifest – the sourcemap and Phase-2 analysis skills fire it next.
---

# Lazy Loaded Chunks

You are operating as the world's best bug bounty hunter and red teamer. Your job is to catch the JavaScript that the initial page load NEVER fetches — lazy-loaded route chunks, deferred admin panels, and code-split features. Spider-harvest gets you the entry bundles; this skill gets you everything those bundles load on demand, which is exactly where developers hide the interesting surface.

## Step 1 – Gather Inputs

Collect everything before starting:

- **Consumes:** `<RUN_DIR>/js_inventory/manifest.json` + `raw/*.js` from `spider-harvest` (the entry bundles are your hunting ground), target base URL `<TARGET>`.
- Confirm which bundles are first-party (`third_party: false`) — you only mine those.
- Output home: `<RUN_DIR>/js_inventory/raw/chunks/` plus `<RUN_DIR>/js_inventory/chunk_manifest.json`.
- Note from spider-harvest's baseline: is this an SPA with 200-fallback? Chunk probing inherits the same baseline discipline.

## Step 2 – Decide When to Use vs When to Skip

**USE when:** spider-harvest completed on a JS app; bundles contain webpack/Vite/Next.js runtime code; the app has multiple routes but the homepage only loaded 1–2 bundles; you suspect admin or authenticated features load on demand.

**SKIP when (time-pass filter):**
- The target has no JS or only a single static bundle with no chunk-loading runtime — grep the bundles for `webpackChunk`, `__vite`, `_next/static` first; zero hits means there are no chunks to catch. Document NEGATIVE and stop.
- All bundles are third-party CDN code — their chunks are vendor code, not attack surface.
- Spider-harvest is BLOCKED on fetch — chunks cannot be harvested without the entry bundles. Escalate fetch first.

## Step 3 – Fingerprint the Bundler

The chunk URL scheme depends entirely on the build tool. Identify it from the downloaded bundles:

```bash
# webpack: chunk-loading runtime + jsonp array
grep -l "webpackChunk\|__webpack_require__\.e\|jsonpScriptSrc" <RUN_DIR>/js_inventory/raw/*.js
# Vite: dynamic import shims + asset manifest references
grep -l "__vite\|import.meta.url\|vite/preload-helper" <RUN_DIR>/js_inventory/raw/*.js
# Next.js: build manifests + chunk paths
grep -l "_next/static/chunks\|__NEXT_DATA__\|next/dist" <RUN_DIR>/js_inventory/raw/*.js
```

Record the verdict (webpack / vite / next / rollup / unknown) in `chunk_manifest.json` under `bundler`. If UNKNOWN: look for `import(` dynamic imports anyway (Step 4) — modern bundlers all emit them — but do not force a framework-specific manifest fetch that does not exist.

## Step 4 – Extract Dynamic import() and Chunk-Loading Calls

Mine every bundle for lazy-load sites. These regexes catch the real patterns:

```bash
cd <RUN_DIR>/js_inventory/raw
# dynamic imports: import("./path") or import(/* webpackChunkName: "x" */ "./path")
grep -rhoE 'import\((\/\*[^\*]+\*\/)?[^)]+\)' *.js | sort -u > /tmp/dynamic_imports.txt
# webpack chunk loading: __webpack_require__.e(<chunkId>) and u= (publicPath) + chunkFilename templates
grep -rhoE '__webpack_require__\.e\([^)]+\)' *.js | sort -u > /tmp/webpack_e.txt
grep -rhoE 'chunkFilename[^,;]{0,120}' *.js | sort -u | head -20
# Vite: __vitePreload / dynamic import with variable
grep -rhoE '__vitePreload\([^)]{0,80}' *.js | sort -u | head -20
wc -l /tmp/dynamic_imports.txt /tmp/webpack_e.txt
```

Decision branch: **if** `dynamic_imports.txt` is empty AND no framework manifest exists (Steps 5–6), the app likely has no lazy loading — record `lazy_loading: false` and stop. **If** hits exist, every unique chunk name/id becomes a probe target.

## Step 5 – Harvest Framework Chunk Manifests

Each framework publishes a manifest that LISTS its chunks. Fetch them directly:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# Next.js: build ID first, then manifests
curl -sS -A "$UA" "<TARGET>/" | grep -oE '"buildId":"[^"]+"' | head -1
# _next/static/<BUILDID>/_buildManifest.js and _ssgManifest.js list every route chunk
curl -sS -A "$UA" -o /tmp/buildManifest.js "<TARGET>/_next/static/<BUILDID>/_buildManifest.js"
# Vite: asset manifest (path varies; check common locations)
for p in "manifest.json" ".vite/manifest.json" "assets/manifest.json"; do
  curl -sS -A "$UA" -o /tmp/vite_$RANDOM.json -w "$p -> %{http_code} %{size_download}\n" "<TARGET>/$p"
done
# webpack: the runtime bundle embeds chunkFilename; also probe the app's known asset dir listing is OFF — do not brute-force, read the runtime
```

Compare every manifest response against the dead-path baseline from spider-harvest: a 200 with the SPA fallback body is a NEGATIVE, not a manifest. Only parse responses that diverge from baseline.

## Step 6 – Derive Chunk URLs From Runtime Code

When no manifest is published, reconstruct the chunk URL template from the webpack/Vite runtime:

```bash
# webpack: find publicPath (p) and chunkFilename pattern, e.g. "[id].[contenthash].js"
grep -rhoE '\.p\s*=\s*"[^"]*"' <RUN_DIR>/js_inventory/raw/*.js | sort -u | head -5
grep -rhoE '"[a-z0-9]*\.[a-z0-9]{8,20}\.js"' <RUN_DIR>/js_inventory/raw/*.js | sort -u | head -20
# Next.js chunks live under predictable paths once you have ONE example:
grep -rhoE '_next/static/chunks/[^"'"'"' ]+\.js' <RUN_DIR>/js_inventory/raw/*.js | sort -u | head -20
```

Build candidate chunk URLs = publicPath + chunkFilename for every chunk id found in Step 4. **Do not** brute-force numeric ids blindly — only probe ids/names OBSERVED in code or manifests. Blind enumeration is the content-discovery pipeline's job, not this skill's.

## Step 7 – Force-Load Routes to Trigger Chunk Fetches

Lazy chunks load when routes render. Force the issue: fetch every route you discovered during the spider crawl (especially `/admin`, `/settings`, `/dashboard`, error pages) and re-extract scripts — new bundles appearing here are route chunks:

```bash
# Re-crawl route URLs found in the spider page list and diff the script sets
python3 - <<'EOF'
import json
m = json.load(open('<RUN_DIR>/js_inventory/manifest.json'))
routes = sorted({f['page_found_on'] for f in m['files'] if not f.get('third_party')})
print('\n'.join(routes))
EOF
# Fetch each route with the browser UA, extract <script src>, and download anything not already in raw/
```

For each newly discovered bundle: download, sha256-dedupe against `raw/`, store in `raw/chunks/`, and RECURSE — chunks can lazy-load further chunks (depth 2 is usually enough; cap recursion at 3 and log the cap).

## Step 8 – Download, Dedupe, and Record Chunks

```bash
mkdir -p <RUN_DIR>/js_inventory/raw/chunks
# For each candidate chunk URL: download, verify content-type is JS (not the SPA fallback), sha256-dedupe
curl -sS -o /tmp/chunk_probe.js -w "%{http_code} %{size_download} %{content_type}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  --compressed "<CHUNK_URL>"
# Fallback check: compare sha256 against the dead-path baseline body hash — match means NEGATIVE, discard
```

Manifest entry (append to `chunk_manifest.json`): `{"chunk_url": ..., "sha256": ..., "size": ..., "trigger": "route:/admin | manifest:_buildManifest | dynamic-import:./AdminPanel", "parent_bundle": "<sha16>"}`. The `trigger` field is mandatory — a chunk with no recorded trigger is an unverified guess.

## Step 9 – Hunt the Admin/Deferred Surface in Chunks

Quick triage pass (deep analysis belongs to Phase 2, but flag the obvious now):

```bash
grep -rilE 'admin|dashboard|internal|debug|superuser' <RUN_DIR>/js_inventory/raw/chunks/*.js | head -20
```

This is TRIAGE, not findings — record paths/strings as CANDIDATE leads in `chunk_manifest.json` under `triage_leads`. Do not declare vulnerabilities from grep output. Ever.

## Step 10 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

- [ ] Bundler fingerprinted from entry bundles (webpack/vite/next/rollup/unknown recorded)
- [ ] Dynamic `import()` + framework chunk-loading calls extracted from ALL first-party bundles
- [ ] Framework manifests probed (`_buildManifest.js` / Vite manifest / webpack runtime) with baseline comparison
- [ ] Chunk URLs derived ONLY from observed code/manifests — no blind numeric brute-forcing
- [ ] Route force-loading performed for every spider-discovered route; new bundles captured
- [ ] Chunk recursion ran to depth ≤3 (or documented why it stopped earlier)
- [ ] Every chunk downloaded to `raw/chunks/<sha256[:16]>.js`, sha256-deduped against `raw/`
- [ ] SPA-fallback responses identified via baseline comparison and discarded (not stored)
- [ ] `chunk_manifest.json` written with bundler, chunk entries, mandatory `trigger` field, and triage leads
- [ ] Fetch failures logged in `fetch_log.md`; WAF blocks escalated to `anti-automation-fetch`

**Nudge prompts:** "Did I check the routes behind auth, or only public ones?" — "Did I recurse into chunks-of-chunks, or stop at depth 1?" — "Do not report done before chunk_manifest.json exists on disk."

## Step 11 – Evidence Standard (No False Positives)

- **Baseline:** every chunk probe compared against the known-dead path baseline. On SPA-fallback hosts, a 200 for a guessed chunk URL proves NOTHING — only a body that diverges from baseline counts.
- **2x reproduction:** any chunk that downloads successfully is re-fetched once; byte-identical sha256 = CONFIRMED harvest. Mismatched bytes between fetches = CDN variance, note it and keep the first.
- **Raw pairs saved:** keep the manifest fetch responses (`/tmp/buildManifest.js` → run folder). A "manifest" that was actually the SPA fallback must be provably excludable later.
- **Verdicts:** harvested chunks = CONFIRMED (sha256 on disk). Candidate chunk URLs that 404 = NEGATIVE (logged, not retried endlessly). Guessed URLs never probed = not even CANDIDATE — probe them or drop them.
- **Blocked = BLOCKED:** chunk endpoints behind bot protection get the ladder treatment via `anti-automation-fetch`; if all rungs fail, `BLOCKED` in `fetch_log.md`, never a fabricated chunk.

## Step 12 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/raw/chunks/*.js` + `<RUN_DIR>/js_inventory/chunk_manifest.json` (bundler, chunk entries with triggers, triage leads). For apps with no lazy loading: `chunk_manifest.json` with `lazy_loading: false` and the grep evidence — that IS the finished artifact.

**Handoff:** `sourcemap-harvest` consumes the chunk list next — it probes `.map` for every chunk exactly like entry bundles. `store-normalize` then dedupes `raw/` against `raw/chunks/`. Phase 2 (`params-routes`, `api-analysis`, `dangerous-functions-gadgets`) mines chunks and entry bundles together — route-split admin code is where the high-value gadgets live.
