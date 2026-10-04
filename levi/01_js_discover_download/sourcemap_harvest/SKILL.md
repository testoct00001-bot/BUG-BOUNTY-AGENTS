---
name: sourcemap-harvest
description: >
  Probes every harvested JS file for sourcemaps (.map URLs, SourceMap headers, sourceMappingURL comments), downloads them, and extracts sourcesContent into readable original source. USE THIS SKILL whenever the user wants sourcemaps, after spider-harvest and lazy-loaded-chunks, or says "find .map files", "sourcesContent", "original source". Trigger on: "sourcemap harvest", ".map files", "sourceMappingURL", "sourcesContent", "unminified source", "map the original code". This skill produces sourcemaps/*.map plus sourcemap_sources/ – the Phase-2 analysis skills fire it for original-source mining.
---

# Sourcemap Harvest

You are operating as the world's best bug bounty hunter and red teamer. Your job is to recover the ORIGINAL, unminified source of every JavaScript file on the target. A published sourcemap hands you the developer's own source tree — real filenames, comments, dead code paths, and internal API routes that minification was supposed to hide.

## Step 1 – Gather Inputs

Collect everything before starting:

- **Consumes:** `<RUN_DIR>/js_inventory/manifest.json` (every `file` + `inline` entry with a fetchable `url`), plus `raw/chunks/` from `lazy-loaded-chunks`. Inline scripts have no `.map` — skip them, but note the skip.
- Output home: `<RUN_DIR>/js_inventory/sourcemaps/` (raw `.map` files) + `<RUN_DIR>/js_inventory/sourcemap_sources/` (extracted originals) + `<RUN_DIR>/js_inventory/sourcemap_report.md`.
- You need the dead-path baseline from spider-harvest — a `.map` probe that returns the SPA fallback is a NEGATIVE, and you must be able to prove it.

## Step 2 – Decide When to Use vs When to Skip

**USE when:** you have harvested JS files (entry bundles and/or chunks); you are in Phase 1 of any JS recon; the target ships minified code (minified code without maps is exactly when maps matter most).

**SKIP when (time-pass filter):**
- There are zero harvested JS files — nothing to probe. This skill never runs before spider-harvest.
- A previous run on this exact bundle set already probed maps with zero hits AND the bundles have not changed (compare sha256) — re-probing identical files is time-pass. Document the prior NEGATIVE and stop.
- The target is BLOCKED on fetch — escalate to `anti-automation-fetch` first; map probing needs working HTTP.

## Step 3 – Probe the Conventional .map URL for Every File

For EVERY downloaded JS file, the first probe is mechanical: append `.map` to the file URL (strip query strings and hashes first — `app.a1b2.js?v=3` probes as `app.a1b2.js.map`):

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# Derive the map URL, then probe it against the dead-path baseline
MAP_URL="<JS_URL_WITHOUT_QUERY>.map"
curl -sS -o /tmp/probe.map -w "%{http_code} %{size_download} %{content_type}\n" -A "$UA" "$MAP_URL"
# It must be JSON with "mappings" or "sources" — anything else is not a map:
python3 -c "import json; d=json.load(open('/tmp/probe.map')); assert 'mappings' in d or 'sources' in d; print(len(d.get('sources',[])), 'sources')"
```

Decision branch: **if** the probe 404s, move to Step 4 (headers) and Step 5 (comment) — the conventional location is only the first guess. **If** it returns 200 HTML, compare against the dead-path baseline: match = SPA fallback NEGATIVE, do not store.

## Step 4 – Check SourceMap / X-SourceMap Response Headers

Re-fetch each JS file's headers. Servers sometimes advertise the map location in a header instead of (or in addition to) the conventional URL:

```bash
curl -sSI -A "$UA" "<JS_URL>" | grep -iE '^sourcemap:|^x-sourcemap:'
```

If a header is present, resolve its value (relative → absolute against the JS URL) and probe THAT URL with the Step 3 verification. Record the header value in `sourcemap_report.md` — header-advertised maps on non-conventional paths are easy to miss and often the interesting ones (staging maps left on production).

## Step 5 – Parse the sourceMappingURL Comment

The ground truth lives in the last bytes of the JS file itself. Read the tail — never the whole file — and extract the comment:

```bash
# Last 2KB is enough; the comment is always at the very end
tail -c 2048 <RUN_DIR>/js_inventory/raw/<sha16>.js | grep -oE '//# sourceMappingURL=[^ ]+' | tail -1
```

Three cases, handle each:
1. **Relative/absolute URL** (`app.js.map`, `/maps/app.js.map`) → resolve against the JS URL, probe with Step 3 verification.
2. **Data URI** (`data:application/json;base64,....`) → it IS the map, inline. Decode it directly: `echo '<b64>' | base64 -d > sourcemaps/<sha16>.map`. No HTTP probe needed.
3. **Absent** → no map advertised. Record `map_advertised: false` for this file and move on — absence is data, not failure.

## Step 6 – Download and Validate Every Found Map

Store validated maps as `sourcemaps/<js_sha16>.map`. Validation is mandatory — a `.map` URL returning an error JSON or HTML is not a map:

```bash
python3 - <<'EOF'
import json, glob
for f in glob.glob('<RUN_DIR>/js_inventory/sourcemaps/*.map'):
    try:
        d = json.load(open(f))
        assert isinstance(d.get('sources'), list), 'no sources list'
        print(f, 'OK -', len(d['sources']), 'sources,', 'sourcesContent:', 'sourcesContent' in d)
    except Exception as e:
        print(f, 'INVALID:', e)
EOF
```

Delete INVALID files — do not keep them "just in case". An invalid map on disk becomes someone else's false positive later.

## Step 7 – Extract sourcesContent Into sourcemap_sources/

When the map embeds `sourcesContent`, you get the original files byte-for-byte. Extract each one, preserving its path:

```bash
python3 - <<'EOF'
import json, os, glob
out = '<RUN_DIR>/js_inventory/sourcemap_sources'
for mf in glob.glob('<RUN_DIR>/js_inventory/sourcemaps/*.map'):
    d = json.load(open(mf))
    contents = d.get('sourcesContent') or []
    for src, code in zip(d.get('sources', []), contents):
        if code is None: continue
        # neutralize ../ escapes — never write outside out/
        safe = os.path.normpath(src).lstrip('/').replace('../', '_/')
        p = os.path.join(out, os.path.basename(mf, '.map')[:8], safe)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8', errors='ignore').write(code)
print('extracted into', out)
EOF
```

Verify extraction: count files written vs `sources` entries with non-null content. A mismatch means the script dropped something — fix it before continuing.

## Step 8 – Mine the Extracted Source (Triage Only)

Quick triage pass over the extracted originals. Deep analysis belongs to Phase 2 — here you only build the lead list:

```bash
cd <RUN_DIR>/js_inventory/sourcemap_sources
grep -rn "TODO\|FIXME\|HACK\|XXX\|remove before prod\|debug only" --include='*.js' --include='*.ts' . | head -30 > /tmp/sm_comments.txt
grep -rhoE '"/(api|admin|internal|debug)[^"]*"' -r . | sort | uniq -c | sort -rn | head -30 > /tmp/sm_endpoints.txt
wc -l /tmp/sm_comments.txt /tmp/sm_endpoints.txt
```

Write both files' contents into `sourcemap_report.md` as CANDIDATE leads. Do not upgrade a comment saying "TODO: secure this" into a vulnerability — it is a lead for Phase 2, nothing more.

## Step 9 – Record sources[]-Without-sourcesContent as Leads

Some maps ship the `sources` filename list but NOT the content. That is still gold: the filenames reveal the source tree layout, internal module names, and sometimes absolute build-machine paths (`/home/dev/project/src/admin/...`):

```bash
python3 - <<'EOF'
import json, glob
for mf in glob.glob('<RUN_DIR>/js_inventory/sourcemaps/*.map'):
    d = json.load(open(mf))
    if not d.get('sourcesContent'):
        print('== CONTENT-ABSENT:', mf)
        for s in d.get('sources', [])[:40]:
            print('   ', s)
EOF
```

Record every content-absent map's source list in `sourcemap_report.md` under "Source-tree leads". Flag absolute filesystem paths and any `admin`/`internal`/`secret` path segments as HIGH-PRIORITY leads for Phase 2 `params-routes`. Also note: content-absent maps sometimes mean the `.js` next to the map IS fetchable — try the sibling `sources/` URL pattern if one is inferable, exactly once, then stop.

## Step 10 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

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

**Nudge prompts:** "Did I probe the CHUNKS too, or only the entry bundles?" — "Did I check the tail comment, or stop at the 404 on .map?" — "Do not report done before sourcemap_report.md exists on disk."

## Step 11 – Evidence Standard (No False Positives)

- **Baseline:** every `.map` probe compared against the dead-path baseline. On SPA-fallback hosts a 200 for `app.js.map` is meaningless unless the body diverges from baseline AND parses as JSON with `sources`.
- **2x reproduction:** each found map is re-downloaded once; identical bytes = CONFIRMED. (Maps are static files — variance here means CDN weirdness worth noting, not ignoring.)
- **Raw pairs saved:** keep the first 300 bytes + headers of each map probe in `sourcemap_report.md`'s evidence section. A disputed map gets re-verified from this, not from memory.
- **Verdicts:** validated map on disk = CONFIRMED. 404/no-comment/no-header across all three probe methods = NEGATIVE for that file (logged per-file, not assumed). Extracted source strings = CANDIDATE leads until Phase 2 verifies. Content-absent source lists = LEAD.
- **Blocked = BLOCKED:** map endpoints behind WAF get the `anti-automation-fetch` ladder; total failure = `BLOCKED` in `fetch_log.md`, never a fabricated map.

## Step 12 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/sourcemaps/*.map` (validated only) + `<RUN_DIR>/js_inventory/sourcemap_sources/` (extracted originals) + `<RUN_DIR>/js_inventory/sourcemap_report.md` (per-file probe results, triage leads, source-tree leads).

**Handoff:** Phase 2 consumes everything here — `params-routes` mines the source-tree leads, `api-analysis` mines extracted endpoints, `secrets-analysis` scans the ORIGINAL source (far higher signal than minified), and `jsluice-jxscout-tools` runs cleaner on unminified input. `store-normalize` dedupes `sourcemap_sources/` into the final inventory. The single most valuable handoff line: "these original-source files contain admin/internal paths the minified bundle hid."
