---
name: spider-harvest
description: >
  Crawls the target app and downloads EVERY JavaScript file plus every inline <script> body, building a complete JS inventory before any analysis begins. USE THIS SKILL whenever the user wants to map a target's JavaScript surface, start JS recon, or kick off Phase 1. Trigger on: "spider the js", "download all javascript", "harvest scripts", "js inventory", "crawl and grab js", "phase 1 js". This skill produces the raw ammunition (raw/*.js + manifest.json) – the chunk-harvest, sourcemap, historical and Phase-2 analysis skills all fire it.
---

# Spider Harvest

You are operating as the world's best bug bounty hunter and red teamer. Your job is to build a COMPLETE inventory of every JavaScript file and every inline script on the target — because every unmapped JS file is a blind spot where endpoints, admin routes, API keys and feature flags hide from generic recon.

## Step 1 – Gather Inputs

Collect everything before touching the target:

- **Consumes:** target base URL (`<TARGET>`, e.g. `https://app.example.com`), scope confirmation (host is in scope — check `~/workspace/levi/START.md` scope gate), optional seed paths (`/login`, `/dashboard`, `/app`) if the app has JS-heavy authenticated areas you can reach.
- Verify scope FIRST. If the host is not in scope, stop and document why — no crawling.
- Create the work folder for this run: `<RUN_DIR>/js_inventory/` with subfolders `raw/`, `raw/inline/`, `raw/maps/`.
- Decide crawl bounds now: `max-depth` (default 2 — homepage + one link hop; raise to 3 only for small SPAs), `same-origin-only` (default true — cross-origin `<script src>` to CDNs gets recorded in the manifest as `third_party: true` but NOT downloaded, because vendor bundles pollute your inventory).
- Note the framework guess from headers if visible (`X-Powered-By`, `Server`, `Set-Cookie`) — it tells you where chunks will live later.

## Step 2 – Decide When to Use vs When to Skip

**USE when:** the target renders an app with first-party JavaScript; you are starting any JS recon or Phase 1; the target is an SPA, dashboard, portal, or SaaS product; previous recon found JS endpoints worth inventorying.

**SKIP when (time-pass filter):**
- The target serves static HTML with zero first-party `<script>` — spidering it is time-pass. Verify with one baseline fetch (Step 3); if no scripts and no JS files, document NEGATIVE and stop.
- The host is out of scope. Scope beats curiosity, always.
- All JS is third-party CDN (Google Analytics, Stripe.js) and zero first-party bundles exist — record the third-party list in the manifest and stop; there is nothing to analyze.
- The target is hard-blocked on every fetch (403/captcha on rung 1) — hand off to `anti-automation-fetch` first, then return here.

## Step 3 – Establish the Fetch Baseline

Before crawling, prove your fetcher sees what a real visitor sees:

```bash
# Baseline: homepage as a real browser
curl -sS -D /tmp/base_headers.txt -o /tmp/base.html \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  --compressed "<TARGET>/" && wc -c /tmp/base.html && head -20 /tmp/base_headers.txt

# Baseline: a known-dead path on the same host (your false-positive control)
curl -sS -o /tmp/dead.html -w "%{http_code} %{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  "<TARGET>/this-path-definitely-does-not-exist-9f3k2"
```

If the dead path returns 200 with the same body size as the homepage, the target is an SPA with a 200-fallback — record this in `fetch_log.md` NOW, because every later "hit" must diverge from this baseline or it is a false positive.

## Step 4 – Crawl Same-Origin Pages to Bounded Depth

Use `bin/js_spider.py` (stdlib-only: urllib + html.parser) or this crawl pattern. Bounded breadth-first crawl — depth 0 is the homepage, each hop follows same-origin `<a href>` links:

```bash
python3 ~/workspace/levi/01_js_discover_download/bin/js_spider.py \
  --target "<TARGET>" \
  --outdir "<RUN_DIR>/js_inventory" \
  --max-depth 2
```

Crawl rules the spider enforces:
- Only follow links whose netloc equals the target netloc (unless `--no-same-origin-only` is explicitly passed).
- Skip non-HTML content types (`application/pdf`, images, binaries) — do not crawl them.
- Cap at ~200 pages per run. If the app is bigger, seed additional entry points (sitemap.xml, `/robots.txt` Disallow paths) as separate runs — do not let the crawler wander unbounded.
- 0.5s delay between requests. You are a guest, not a DDoS.

## Step 5 – Extract Script Tags Two Ways

Every crawled page gets TWO extraction passes — the HTML parser is primary, the regex is the safety net for malformed markup:

```bash
# Pass 1 (parser): bin/js_spider.py already extracts via html.parser — verify its work:
grep -c "inline_or_file" <RUN_DIR>/js_inventory/manifest.json

# Pass 2 (regex safety net) on any saved page that yielded zero scripts but looks like an app:
python3 - <<'EOF'
import re, glob
pat = re.compile(r'<script[^>]*src=["\']([^"\']+)["\']', re.I)
for f in glob.glob('/tmp/saved_pages/*.html'):
    hits = pat.findall(open(f, encoding='utf-8', errors='ignore').read())
    if hits: print(f, '->', hits)
EOF
```

If the regex pass finds `src` values the parser missed, your parser is broken — fix it before continuing. A harvester that silently drops scripts is worse than no harvester.

## Step 6 – Resolve Relative URLs to Absolute

Every `src` must become a fetchable absolute URL. Resolution order:

1. Protocol-relative (`//cdn.example.com/a.js`) → inherit the page scheme.
2. Root-relative (`/static/app.js`) → join with scheme + netloc.
3. Page-relative (`js/app.js`) → join with the page URL directory.
4. Strip cache-buster query strings (`?v=abc123`) for the DOWNLOAD key, but keep the original full URL in the manifest (`url_raw` vs `url_canonical`) — two query variants of the same file are one file.

Record every resolution decision in the manifest (`page_found_on` + `url_raw`). If a `src` cannot be resolved (empty, `javascript:` pseudo-URL, template placeholder like `{{asset}}`), log it as a lead — template placeholders mean a build system injects the real path, which is itself a finding for the analysis phase.

## Step 7 – Download Every File, Log Every Failure

Download each resolved URL. Dedupe by sha256 — the same bundle served from 5 pages is downloaded once:

```bash
# Manual verification pattern for one file (baseline vs probe):
curl -sS -o /tmp/probe.js -w "%{http_code} %{size_download} %{content_type}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  --compressed "<JS_URL>"
sha256sum /tmp/probe.js
```

- Store as `raw/<sha256[:16]>.js` (first 16 hex chars of the full sha256). Full sha256 goes in the manifest.
- If a download fails (timeout, 403, 404, truncated body), LOG it to `fetch_log.md` with the URL, the HTTP code, and the page that referenced it — then CONTINUE. A failed download is a fact, not a reason to stop the run.
- If the failure is a 403/WAF block (not a 404), escalate to `anti-automation-fetch` — do NOT skip the file and pretend the inventory is complete.
- If the response `Content-Type` is `text/html` for a `.js` URL, the server is serving a fallback page — compare its sha256 against the dead-path baseline from Step 3. Match = SPA fallback, mark `false_positive: true`, do not store as JS.

## Step 8 – Save Inline Scripts With Page Context

Inline `<script>` bodies are frequently where config, API base URLs, and feature flags live. Save every non-empty inline block:

- Store as `raw/inline/<sha256[:16]>.js`.
- Manifest entry: `inline_or_file: "inline"`, `page_found_on: <page URL>`, plus `script_index` (nth script on the page) so you can trace it back.
- Skip empty blocks and blocks under 50 bytes unless they contain `src=`-less JSON config — tiny JSON blobs (`{"apiBase":"..."}`) are gold; empty whitespace is not. When in doubt, save it — inline storage is cheap, missed config is expensive.

## Step 9 – Build manifest.json

The spider writes `<RUN_DIR>/js_inventory/manifest.json`. Every entry has exactly this schema:

```json
{
  "url": "https://app.example.com/static/app.abc123.js",
  "url_raw": "https://app.example.com/static/app.abc123.js?v=2",
  "sha256": "<full hex>",
  "size": 482103,
  "inline_or_file": "file",
  "page_found_on": "https://app.example.com/dashboard",
  "third_party": false,
  "false_positive": false,
  "map_probed": true,
  "map_found": false
}
```

Validate the manifest before moving on: `python3 -c "import json; d=json.load(open('<RUN_DIR>/js_inventory/manifest.json')); print(len(d['files']), 'entries')"`. Zero entries with a non-empty crawl = something broke — do not proceed on an empty inventory.

## Step 10 – Spot-Verify Inventory Completeness

Trust but verify — pick 3 crawled pages and manually confirm their scripts are all in the manifest:

```bash
# For a sampled page: count script tags in the raw HTML, compare to manifest entries with that page_found_on
grep -oi '<script[^>]*>' /tmp/sample_page.html | wc -l
python3 -c "
import json
m = json.load(open('<RUN_DIR>/js_inventory/manifest.json'))
print(sum(1 for f in m['files'] if f['page_found_on'] == '<SAMPLE_PAGE_URL>'))
"
```

If the counts disagree, find the missing scripts and re-run extraction for that page. An inventory you have not spot-checked is an inventory you do not have.

## Step 11 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

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

**Nudge prompts (say these before declaring done):** "Did I check pages behind the login, or only the public surface?" — "Is the manifest empty because the site has no JS, or because my fetcher got blocked?" — "Do not report done before manifest.json exists on disk."

## Step 12 – Evidence Standard (No False Positives)

- **Baseline:** every downloaded file's HTTP response was compared against the known-dead path baseline from Step 3. A `.js` URL returning the SPA fallback page is a NEGATIVE, not a JS file.
- **2x reproduction:** any file that failed to download gets retried once after a 60s pause; if it fails twice with the same code, the failure is CONFIRMED as a fetch failure (not a transient) and logged.
- **Raw pairs saved:** keep the request/response headers of the baseline fetch (`/tmp/base_headers.txt` → copy into the run folder as `baseline_headers.txt`). Later disputes about "was it really JS?" get answered from this file.
- **Verdicts:** each manifest entry is implicitly CONFIRMED (downloaded, sha256'd) or documented-failed. There are no silent gaps — a URL with no entry and no failure log is a process failure, fix it.
- **Blocked = BLOCKED:** if a WAF/captcha blocks downloads, write `BLOCKED: <reason> at <rung>` in `fetch_log.md` and escalate to `anti-automation-fetch`. Never fabricate a file or mark an undownloaded script as harvested.

## Step 13 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/manifest.json` (schema-validated, non-empty for any JS-bearing target) + `raw/*.js` + `raw/inline/*.js`.

**Handoff:** `lazy-loaded-chunks` consumes `manifest.json` next — it needs the list of downloaded first-party bundles to hunt for chunk-loading code and framework manifests. Then `sourcemap-harvest` probes `.map` for every entry, and `historical-js` uses the canonical URLs for Wayback queries. Phase 2 analysis skills consume the whole `js_inventory/` tree.
