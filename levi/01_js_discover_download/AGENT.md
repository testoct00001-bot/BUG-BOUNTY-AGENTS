# AGENT.md — Phase 1: Discover / Download (01_js_discover_download)

## Purpose

This phase builds the COMPLETE JavaScript inventory of the target before any analysis begins. Nothing in Phase 2 (`02_js_analyze/`) runs on an incomplete corpus: every unmapped bundle, missed lazy chunk, unfetched sourcemap, or skipped historical version is attack surface you will never see. The phase succeeds when `inventory_final.json` describes every unique JS file the target serves — or documents exactly why a file could not be fetched.

## Skill chain (run in this order — each leaves its finished artifact before the next starts)

1. **`spider-harvest`** — Crawl the app (bounded depth, same-origin default), collect every `<script src>` + inline `<script>` body. Produces `js_inventory/manifest.json` + `raw/*.js` + `raw/inline/*.js`. Establishes the dead-path baseline the whole phase reuses.
2. **`lazy-loaded-chunks`** — Mine entry bundles for webpack/Vite/Next chunk-loading, fetch framework manifests, force-load routes, recurse into chunks-of-chunks. Produces `raw/chunks/*.js` + `chunk_manifest.json`.
3. **`historical-js`** — Wayback CDX + waymore pull old bundles; token-set diff old-vs-new; live-probe removed paths against baseline. Produces `historical/*.js` + `diff_old_new.md`.
4. **`sourcemap-harvest`** — Probe `.map` for EVERY harvested file (conventional URL, headers, tail comment); extract `sourcesContent`; record source-tree leads. Produces `sourcemaps/*.map` + `sourcemap_sources/` + `sourcemap_report.md`.
5. **`anti-automation-fetch`** — Called BY any skill above the moment a block appears (it is also a standalone skill). Six rungs: real-UA curl → HTTP/2 ordered headers → webfetch → mitmproxy interception → Chrome DevTools MCP → Puppeteer/Playwright. Produces per-rung sections in `fetch_log.md`. Iron rule: exhausted ladder = documented `BLOCKED`, never fabricated bytes.
6. **`store-normalize`** — Enforce `raw/` + `normalized/` + manifest layout, sha256 dedupe across all sources, per-run versioning, prettier for minified, sandboxed string-array recovery for obfuscated (honest limits, failures logged). Produces `normalized/` + `inventory_final.json` + `normalize_failures.md` + `dedupe_map.json`.

Helper: `bin/js_spider.py` — stdlib-only spider (urllib + html.parser): crawls pages, downloads `<script src>` files, saves inline scripts, probes `.map` per file, writes `manifest.json`.

```
target URL
   │
   ▼
spider-harvest ──(blocked?)──▶ anti-automation-fetch ──▶ resume caller
   │ manifest.json + raw/
   ▼
lazy-loaded-chunks ──▶ chunk_manifest.json + raw/chunks/
   │
   ▼
historical-js ──▶ historical/ + diff_old_new.md
   │
   ▼
sourcemap-harvest ──▶ sourcemaps/ + sourcemap_sources/ + sourcemap_report.md
   │
   ▼
store-normalize ──▶ normalized/ + inventory_final.json
   │
   ▼
REVIEW GATE 1 ──▶ Phase 2 (02_js_analyze/)
```

## Division of labor

- **Consumes:** target base URL (+ scope confirmation), optional seed paths, optional auth cookies for authenticated areas.
- **Produces:** `<RUN_DIR>/js_inventory/` containing `raw/`, `raw/chunks/`, `raw/inline/`, `raw/maps/`, `sourcemaps/`, `sourcemap_sources/`, `historical/`, `normalized/`, `manifest.json`, `chunk_manifest.json`, `sourcemap_report.md`, `diff_old_new.md`, `fetch_log.md`, `dedupe_map.json`, `normalize_failures.md`, and the canonical **`inventory_final.json`**.
- This phase NEVER declares vulnerabilities. Its outputs are CANDIDATE material and documented NEGATIVEs/BLOCKEDs for Phase 2 to verify.

## How the skills call each other

- `spider-harvest` → `anti-automation-fetch` on any 403/challenge/captcha/TLS-reset; resumes with the winning rung's configuration or marks `fetch_failed`.
- `lazy-loaded-chunks` → `anti-automation-fetch` if chunk/manifest endpoints are defended.
- `sourcemap-harvest` → `anti-automation-fetch` if `.map` endpoints are defended; skips probes for files already BLOCKED.
- `historical-js` documents archive.org rate limits as BLOCKED in `fetch_log.md` (no ladder — that is a third-party service, not the target).
- `store-normalize` consumes ALL prior outputs and is always last.

## Review gate 1 checklist (from START.md — all must be YES)

- [ ] **Inventory complete?** `inventory_final.json` exists, schema-valid, `in_analysis_set > 0` (or every URL documented BLOCKED). Spot-check: 3 pages' script counts match the manifest.
- [ ] **Chunks caught?** `chunk_manifest.json` exists with bundler verdict; chunk recursion reached its documented depth; route force-loading covered spider-discovered routes.
- [ ] **Historical diff done?** `diff_old_new.md` exists with removed-path table (live/dead verdicts vs baseline) and retired-API table — or a documented NEGATIVE (target too new / no archive coverage).
- [ ] **Sourcemaps attempted for every file?** `sourcemap_report.md` shows per-file results across all three probe methods (conventional URL, headers, tail comment) for entry bundles AND chunks.
- [ ] **Blocks documented?** `fetch_log.md` has a section per blocked URL ending in a working config or a `BLOCKED` entry. Zero silent gaps.
- [ ] **Corpus clean?** `dedupe_map.json` written; `raw/` immutable; every normalized file has a `.meta.json`; failures in `normalize_failures.md`.

If any box is unchecked, the phase is NOT done. Go back and finish it — Phase 2 on a broken inventory manufactures false confidence, which is worse than no recon at all.

## Stop conditions

- Target out of scope → stop everything, document why.
- Zero JS on target (verified via baseline + crawl) → `manifest.json` with zero entries IS the finished artifact; record NEGATIVE, skip to gate.
- All fetches BLOCKED after full ladder → `fetch_log.md` BLOCKED entries ARE the finished artifact; gate records the gap; Phase 2 does not run on fabricated data.

## Nudge prompts (read before declaring the phase complete)

- "Keep going until you have tested every parameter, not just the first one that responded."
- "Do not report done before the finished artifact exists on disk."
- "If you stopped because it got boring, that is exactly where the bugs live — continue."
- "One more pass: what did the historical JS have that the current bundle removed?"
