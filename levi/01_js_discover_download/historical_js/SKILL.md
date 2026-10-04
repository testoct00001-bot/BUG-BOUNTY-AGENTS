---
name: historical-js
description: >
  Pulls historical JavaScript bundles from the Wayback Machine (CDX API + waymore) and diffs them against current bundles to find removed-but-still-live endpoints, retired API versions, and old auth flows. USE THIS SKILL whenever the user wants historical JS, after spider-harvest, or says "wayback js", "old bundles", "diff old vs new". Trigger on: "historical js", "wayback machine js", "old javascript versions", "waymore", "diff old new bundles", "removed endpoints". This skill produces historical/*.js plus diff_old_new.md – the api-analysis and content-discovery skills fire it to resurrect dead-but-live surface.
---

# Historical JS

You are operating as the world's best bug bounty hunter and red teamer. Your job is to resurrect the target's PAST JavaScript — old bundles contain endpoints, API versions, and debug features the current build deleted but the backend may still serve. Developers delete code; they rarely delete routes.

## Step 1 – Gather Inputs

Collect everything before starting:

- **Consumes:** canonical JS URLs from `<RUN_DIR>/js_inventory/manifest.json` (`url_canonical` per file — strip cache-busters; Wayback indexes the path, not your `?v=` param), target domain `<TARGET_DOMAIN>` (bare host, e.g. `app.example.com`).
- Output home: `<RUN_DIR>/js_inventory/historical/` + `<RUN_DIR>/js_inventory/diff_old_new.md`.
- Check tool availability: `waymore --help` and `curl` to `web.archive.org`. If waymore is missing: `pip install waymore` (it is a real PyPI package by xnl-h4ck3r). If pip is unavailable, the CDX API via curl covers the core workflow — document the gap.
- Note the current bundle hashes — you need them to prove a historical bundle is actually DIFFERENT, not just re-archived.

## Step 2 – Decide When to Use vs When to Skip

**USE when:** spider-harvest completed; the target has versioned bundles (hashed filenames like `app.a1b2c3.js` scream "old versions exist"); the app is ≥1 year old; you are hunting retired API versions or removed admin features.

**SKIP when (time-pass filter):**
- The target is brand-new (launched this quarter) — there is no history worth mining. One CDX probe proving zero captures is enough; document NEGATIVE and stop.
- The JS is a single unversioned file that never changes — Wayback will hold identical copies. Verify with one CDX query; identical sha256 = stop.
- The target is BLOCKED on fetch — historical downloads need working HTTP. Fix fetch first.

## Step 3 – Query the Wayback CDX API Per Known Bundle

For EACH canonical JS URL from the manifest, pull its capture history. This is the exact CDX query — these parameters are real:

```bash
# Captures of one bundle URL, 200s only, JS mime types, one row per unique digest
curl -sS "https://web.archive.org/cdx/search/cdx?url=app.example.com/static/app.*.js&output=json&filter=statuscode:200&filter=mimetype:application/javascript&collapse=digest&fl=timestamp,original,digest,length" \
  -o /tmp/cdx_app.json && python3 -c "import json; print(len(json.load(open('/tmp/cdx_app.json')))-1, 'captures')"
```

- `collapse=digest` is load-bearing: without it you drown in identical re-crawls of the same file.
- If the bundle filename contains a content hash, ALSO query with a wildcard on the hash segment (`app.*.js`) — old versions had DIFFERENT hashes and a literal-URL query misses them.
- For each canonical URL, keep the OLDEST capture and the 2–3 captures with distinct digests closest to major version changes (roughly one per quarter). You do not need 400 captures of the same file.

## Step 4 – Run Waymore for Broad Historical URL Collection

Waymore finds JS URLs you never knew existed — old paths, renamed bundles, forgotten subdomains' assets. Real invocation:

```bash
# -mode U = URLs only; -oU writes them out. These flags exist in waymore.
waymore -i <TARGET_DOMAIN> -mode U -oU /tmp/waymore_urls.txt
# Then filter to JS:
grep -E '\.js($|\?)' /tmp/waymore_urls.txt | sort -u > /tmp/waymore_js.txt
wc -l /tmp/waymore_js.txt
```

Decision branch: **if** `/tmp/waymore_js.txt` has <10 lines, the target has thin archive coverage — proceed with CDX results only and note the limitation. **If** it has hundreds, prioritize: admin-ish paths, `/static/` with old hashes, and any path NOT in your current manifest — those are the highest-signal resurrection candidates.

## Step 5 – Download Historical Bundles

Download the selected captures. The `id_` suffix returns the ORIGINAL archived bytes (without it you get Wayback's rewritten HTML wrapper — a classic false-positive trap):

```bash
# Correct: id_ gives raw original bytes
curl -sS -o historical/app.2023q1.js "https://web.archive.org/web/20230115000000id_/https://app.example.com/static/app.oldhash.js"
# Verify it is actually JS, not a Wayback error page:
head -c 200 historical/app.2023q1.js && file historical/app.2023q1.js
```

- Name files `historical/<name>.<yyyymmdd>.js` using the capture timestamp.
- After download, sha256 each file and DROP any that match a current bundle hash — identical files are not "historical finds", they are archive noise.
- If a capture returns Wayback's "not archived" HTML, discard it and log the gap — do not store HTML as JS.
- Sanity-check every download in bulk before diffing — one bad file poisons the whole token set:

```bash
# Every historical file must be JS, non-empty, and distinct from current bundles
for f in <RUN_DIR>/js_inventory/historical/*.js; do
  printf "%s | " "$(basename $f)"; file -b "$f" | cut -c1-40; \
  sha256sum "$f" | cut -c1-16; done | tee /tmp/hist_verify.txt
# Cross-check: no historical sha256 may equal a current bundle sha256
cut -d' ' -f1 <(sha256sum <RUN_DIR>/js_inventory/historical/*.js) | sort > /tmp/hist_hashes.txt
cut -d' ' -f1 <(sha256sum <RUN_DIR>/js_inventory/raw/*.js) | sort > /tmp/cur_hashes.txt
comm -12 /tmp/hist_hashes.txt /tmp/cur_hashes.txt && echo "OVERLAP FOUND — drop those files" || echo "no overlap, clean"
```

## Step 6 – Diff Old vs New Bundles

Diffing raw minified bundles is noise. Extract the MEANINGFUL tokens first, then diff those:

```bash
# Extract candidate endpoints/paths from old and new, then diff the SETS
grep -rhoE '"/[a-zA-Z0-9/_\-\.]{2,80}"' historical/app.20230115.js | sort -u > /tmp/old_paths.txt
grep -rhoE '"/[a-zA-Z0-9/_\-\.]{2,80}"' <RUN_DIR>/js_inventory/raw/<current_sha16>.js | sort -u > /tmp/new_paths.txt
comm -23 /tmp/old_paths.txt /tmp/new_paths.txt > /tmp/removed_paths.txt
wc -l /tmp/removed_paths.txt && head -40 /tmp/removed_paths.txt
# Same for API-ish strings and version markers:
grep -rhoE '/api/v[0-9]+' historical/app.20230115.js | sort | uniq -c | sort -rn | head
grep -rhoE '/api/v[0-9]+' <RUN_DIR>/js_inventory/raw/<current_sha16>.js | sort | uniq -c | sort -rn | head
```

The `comm -23` output — paths in OLD but not in NEW — is your resurrection list. Triage it for: `/api/v1` vs current `/api/v2` (old API versions), `/admin`, `/debug`, `/internal`, feature-flag names, and old auth endpoints (`/oauth/token`, `/login/legacy`).

## Step 7 – Verify Removed Paths Are Still Live

A removed path is only interesting if the BACKEND still serves it. Probe each high-signal removed path against the live target, with the dead-path baseline beside it:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# Probe (removed path) vs baseline (known-dead path) — compare codes AND bodies
curl -sS -o /tmp/probe.body -w "%{http_code} %{size_download}\n" -A "$UA" "<TARGET><REMOVED_PATH>"
curl -sS -o /tmp/base.body -w "%{http_code} %{size_download}\n" -A "$UA" "<TARGET>/this-path-definitely-does-not-exist-9f3k2"
cmp -s /tmp/probe.body /tmp/base.body && echo "BASELINE-MATCH (dead)" || echo "DIVERGES (live candidate)"
```

- DIVERGES = CANDIDATE for resurrection (hand the URL to Phase 2 `api-analysis` and Pipeline 2 `api-discovery` for full verification).
- BASELINE-MATCH = NEGATIVE, logged once in `diff_old_new.md` so nobody re-probes it.
- Never declare a resurrected endpoint CONFIRMED from a single probe — it needs the 2x reproduction + raw pairs that Phase 2 performs.

## Step 8 – Record Old API Versions and Auth Flows

Old bundles frequently reveal versioned API roots and retired auth flows. Extract and tabulate:

```bash
grep -rhoE 'https?://[a-zA-Z0-9.\-]+(/[a-zA-Z0-9/_\-\.]+)?' historical/*.js | sort -u | grep -iE 'api|auth|oauth|token' | head -30
```

Write every distinct API base + version into `diff_old_new.md` under "Retired API surface". These feed DIRECTLY into Phase 2 `api-analysis` ("old versions" is literally on the board) and Pipeline 2's versioned-API discovery. An old `/api/v1` that still answers is one of the highest-ROI finds in this whole pack — flag it prominently, but keep the CANDIDATE verdict until Phase 2 verifies.

## Step 9 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

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

**Nudge prompts:** "Did I wildcard the hash segment, or only query the current filename?" — "Did I use id_ downloads, or am I diffing Wayback's rewritten HTML?" — "One more pass: what did the OLDEST bundle have that even the middle versions removed?"

## Step 10 – Evidence Standard (No False Positives)

- **Baseline:** every "removed path still live" claim is a probe-vs-dead-path comparison, not a bare 200. On SPA-fallback hosts the fallback body is the baseline — match means dead.
- **2x reproduction:** each resurrected-path probe is fetched twice; both must diverge from baseline identically. One-off divergences (CDN hiccups, A/B pages) are INCONCLUSIVE, not CONFIRMED.
- **Raw pairs saved:** keep probe/baseline bodies (`/tmp/probe.body`, `/tmp/base.body` → run folder as `evidence_resurrect_<path>.txt` with request line + response code + first 500 bytes).
- **Verdicts:** removed-but-live = CANDIDATE until Phase 2 verifies (this skill does not CONFIRM endpoints). Removed-and-dead = NEGATIVE (logged). Archive-only strings with no live probe = LEAD, not a finding.
- **Blocked = BLOCKED:** if web.archive.org rate-limits (429/503), back off, retry with delays, and if persistent, document `BLOCKED: archive.org rate limit` in `fetch_log.md`. Never invent historical URLs.

## Step 11 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/historical/*.js` (deduped, verified-JS historical bundles) + `<RUN_DIR>/js_inventory/diff_old_new.md` (removed-path table with live/dead verdicts, retired API surface table, waymore coverage note).

**Handoff:** Phase 2 `api-analysis` consumes the retired API surface table (its "old versions" job); Pipeline 2 `api-discovery` and `app-specific-files` consume the resurrected CANDIDATE paths as seed input; `store-normalize` includes `historical/` in dedupe/versioning. The single most valuable line in your handoff is: "these N removed paths diverge from baseline and are still live."
