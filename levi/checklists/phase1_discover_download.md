# .MD Checklist — Phase 1 — Discover / Download

> Pipeline 1, Phase 1: every JS file found, downloaded, and normalized before any analysis begins.

> **Iron rule:** a box with no checkmark means the agent has NOT finished that step.
> Not finished means the skill gets **re-run** — not argued with, not summarized, re-run.
> Copy this file per target as `<target>_<date>.md` and tick boxes as you go.
**Skills in this phase:** 6 | **Total boxes:** 65

## Anti-Automation Fetch (`anti-automation-fetch`)

**Finished artifact:** `<RUN_DIR>/js_inventory/fetch_log.md` — per-rung sections for every blocked URL, ending in either a working fetch configuration or a BLOCKED entry. **Handoff:** the CALLING skill resumes with the w

- [ ] Blocker diagnosed (WAF vendor / TLS fingerprint / rate limit / captcha) before choosing the start rung
- [ ] Rate-limit (429) cases handled by backoff, NOT by climbing
- [ ] Rung 1 attempted with full browser header set; result + block signature logged
- [ ] Rung 2 attempted with `--http2`; actual negotiated version verified in output
- [ ] Rung 3 attempted or honestly marked NOT ATTEMPTED with the reason
- [ ] Rung 4 attempted (mitmproxy capture) or marked not-applicable with reason
- [ ] Rung 5 attempted (DevTools MCP) or marked not-applicable with reason
- [ ] Rung 6 attempted (Puppeteer/Playwright) or skipped per authorization boundary with reason
- [ ] `fetch_log.md` has one section PER RUNG with command evidence or honest skip reason
- [ ] If all rungs failed: BLOCKED entry written in the exact format, downstream skills notified of the gap
- [ ] If any rung succeeded: the working header/cookie set handed back to the calling skill

## Historical JS (`historical-js`)

**Finished artifact:** `<RUN_DIR>/js_inventory/historical/*.js` (deduped, verified-JS historical bundles) + `<RUN_DIR>/js_inventory/diff_old_new.md` (removed-path table with live/dead verdicts, retired API surface table,

- [ ] Canonical JS URLs extracted from `manifest.json` (cache-busters stripped)
- [ ] CDX queried per canonical URL with `collapse=digest`, `filter=statuscode:200`, JS mimetypes
- [ ] Hash-versioned bundles ALSO queried with wildcard hash segment (`app.*.js`)
- [ ] Waymore run (`-mode U -oU`), JS URLs filtered to `/tmp/waymore_js.txt`
- [ ] Historical bundles downloaded with `id_` suffix; Wayback HTML wrappers detected and discarded
- [ ] Downloaded files sha256-compared against current bundles; identical files dropped as archive noise
- [ ] Token-set diff performed (`comm -23` on extracted paths); removed-path list built
- [ ] High-signal removed paths live-probed vs dead-path baseline; verdicts recorded
- [ ] Retired API versions / auth flows tabulated in `diff_old_new.md`
- [ ] Bulk download verification passed (`file` says JS, no sha256 overlap with current bundles)
- [ ] `historical/*.js` + `diff_old_new.md` exist on disk

## Lazy Loaded Chunks (`lazy-loaded-chunks`)

**Finished artifact:** `<RUN_DIR>/js_inventory/raw/chunks/*.js` + `<RUN_DIR>/js_inventory/chunk_manifest.json` (bundler, chunk entries with triggers, triage leads). For apps with no lazy loading: `chunk_manifest.json` wi

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

## Sourcemap Harvest (`sourcemap-harvest`)

**Finished artifact:** `<RUN_DIR>/js_inventory/sourcemaps/*.map` (validated only) + `<RUN_DIR>/js_inventory/sourcemap_sources/` (extracted originals) + `<RUN_DIR>/js_inventory/sourcemap_report.md` (per-file probe results

- [ ] Every harvested JS file (entry bundles AND chunks) probed at `<file>.js.map` with baseline comparison
- [ ] `SourceMap` / `X-SourceMap` response headers checked for every JS file
- [ ] `sourceMappingURL` tail comment parsed for every JS file (URL / data-URI / absent — all three handled)
- [ ] Data-URI maps decoded directly, no phantom HTTP probe
- [ ] Every found map JSON-validated (`sources` list present); INVALID files deleted, not kept
- [ ] `sourcesContent` extracted to `sourcemap_sources/` with path-traversal neutralization; file counts verified
- [ ] Triage mining done (comments + endpoint-ish strings) → CANDIDATE leads in `sourcemap_report.md`
- [ ] Content-absent maps' `sources[]` lists recorded as source-tree leads
- [ ] Inline scripts explicitly noted as unprobable (not silently skipped)
- [ ] Fetch failures / blocks logged in `fetch_log.md`

## Spider Harvest (`spider-harvest`)

**Finished artifact:** `<RUN_DIR>/js_inventory/manifest.json` (schema-validated, non-empty for any JS-bearing target) + `raw/*.js` + `raw/inline/*.js`. **Handoff:** `lazy-loaded-chunks` consumes `manifest.json` next — it

- [ ] Scope confirmed for the target host (documented, not assumed)
- [ ] `<RUN_DIR>/js_inventory/` created with `raw/`, `raw/inline/`, `raw/maps/`
- [ ] Baseline fetch done: homepage + known-dead path, SPA-fallback status recorded in `fetch_log.md`
- [ ] Bounded crawl completed (max-depth honored, same-origin-only default, ≤200 pages, 0.5s politeness delay)
- [ ] Script extraction ran TWO passes (parser + regex safety net) on every crawled page
- [ ] All `src` values resolved to absolute URLs; unresolvable values logged as leads
- [ ] Every file downloaded to `raw/<sha256[:16]>.js`; failures logged in `fetch_log.md`, run continued
- [ ] Every inline block saved to `raw/inline/` with page context
- [ ] `manifest.json` written and schema-validated (url, sha256, size, inline_or_file, page_found_on all present)
- [ ] Spot-verification passed on 3 sampled pages (script counts match manifest)
- [ ] Third-party CDN scripts flagged `third_party: true`, not downloaded
- [ ] SPA-fallback false positives flagged `false_positive: true`, not stored as JS

## Store & Normalize (`store-normalize`)

**Finished artifact:** `<RUN_DIR>/js_inventory/normalized/` (working copies + `.meta.json` per file) + `<RUN_DIR>/js_inventory/inventory_final.json` (canonical index) + `<RUN_DIR>/js_inventory/normalize_failures.md` + `<

- [ ] Storage layout enforced exactly (`raw/`, `normalized/`, manifests at the named paths); `raw/` immutable after this step
- [ ] `run_id` assigned and stamped on all new artifacts
- [ ] sha256 dedupe run across raw + chunks + historical + sourcemap_sources; `dedupe_map.json` written
- [ ] Duplicates mapped to canonical files; historical hash-matches marked `superseded_by_current`
- [ ] Every unique file classified (readable / minified / obfuscated / empty)
- [ ] Minified files prettified; parse-verified with `node --check`; parser recorded in `.meta.json`
- [ ] Obfuscated files: string-array recovery attempted in sandboxed `vm` only; literals replaced only when deterministic 2x
- [ ] No claim of "fully deobfuscated" anywhere — residual obfuscation listed per file
- [ ] Every un-normalizable file logged in `normalize_failures.md` with analysis guidance
- [ ] `inventory_final.json` written, schema-valid, non-empty analysis set (or BLOCKED documented)
- [ ] BLOCKED URLs from `fetch_log.md` carried into `inventory_final.json`

---

## Phase Gate 1 — certify before Phase 2 starts

- [ ] Inventory complete: `manifest.json` covers every discovered script (no skill left boxes unticked above)
- [ ] Lazy-loaded chunks caught: `chunk_manifest.json` exists, recursion depth documented
- [ ] Historical diff done: `diff_old_new.md` exists (or "no historical bundles found" documented with the CDX queries run)
- [ ] Sourcemaps attempted for EVERY harvested file (attempted ≠ found — attempts are logged)
- [ ] `fetch_log.md` accounts for every fetch failure; blocks escalated or marked BLOCKED
- [ ] `inventory_final.json` + `normalized/` on disk
- [ ] Tool syntax: every tool invocation in this phase is written as the full explicit command (flags, inputs, output paths) — never a generic "probe with X"; the model must not infer tool syntax
- [ ] **Gate verdict:** PASS / FAIL — if FAIL, name the skill, re-run it, re-certify
