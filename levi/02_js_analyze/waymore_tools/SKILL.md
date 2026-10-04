---
name: waymore-tools
description: >
  Wayback Machine historical harvest for <TARGET>: archived URLs plus old JS bundles, diffed against current code to surface removed-UI-but-live-backend endpoints. USE THIS SKILL whenever the user wants to mine historical URLs or archived bundles for forgotten endpoints. Trigger on: "waymore historical URLs", "wayback JS harvesting", "old bundles from archive". This skill produces the time-travel ammunition – the api_analysis fires it.
---

# Waymore Historical Harvest

You are operating as the world's best bug bounty hunter and red teamer. Your job is to harvest the target's past from the Wayback Machine — old URLs, archived JS bundles, removed UI — because a feature deleted from the frontend often leaves its backend alive and unauthenticated.

## Step 1 – Gather inputs
1. Confirm `<TARGET>` (host only, e.g. `app.example.com` — waymore takes `-i <target>`; check the phase-1 config or work folder name, never guess).
2. Verify waymore is installed: `which waymore`. If missing, install per the xnl-h4ck3r README — do not invent install flags; verify with `waymore --help` first.
3. Read `<WORKDIR>/inventory_final.json` — you need the CURRENT bundle list so the old-vs-new diff in Step 5 means something.
4. Check the phase-1 `historical/` folder and `diff_old_new.md` if they exist — waymore output feeds that existing diff, it doesn't replace it.
5. Create the output dir: `mkdir -p <WORKDIR>/waymore_out`.
6. Confirm scope covers archived subdomains: if the engagement scope includes `*.example.com`, harvest each in-scope host that shows archive history — but one host per run, merged after, so a giant host can't starve a small one.
7. Check disk space before downloading: `du -sh <WORKDIR>/historical/` and `df -h <WORKDIR> | tail -1` — a thousand archived bundles at ~1MB each is fine; ten thousand is a plan-first situation.

## Step 2 – Estimate before you burn (check-only first)
6. Run `waymore -i <TARGET> --check-only` (also `-co`) FIRST — it estimates request count and time before a full run.
7. If the estimate is absurd (tens of thousands of requests or many hours), abort the full run and narrow scope: harvest the most promising subdomain only, or cap by piping through a filter early. Concrete narrowing: run one host at a time (`waymore -i app.<TARGET>` instead of the apex), or harvest URLs but skip the bundle-download step for CDN-hosted files.
8. If X do Y: if `--check-only` errors out, run with `-v` for error details and diagnose — a proxy or network block here means the full run will fail identically. If Z pivot: if the estimate is small (<500 requests), skip straight to the full run and spend the saved time on the diff instead.
9. Save the estimate: `waymore -i <TARGET> --check-only > <WORKDIR>/waymore_out/check_only.txt 2>&1` — the evidence standard requires the scale on record before the harvest runs.

## Step 3 – Full URL harvest (mode U)
10. Run the full harvest: `waymore -i <TARGET> -mode U -oU <WORKDIR>/waymore_out/waymore_urls.txt`. Mode U = URLs only; archived responses are NOT printed to stdout, only saved to disk — stdout stays clean for piping.
11. Remember the stream contract: links go to stdout and errors to stderr, so piping works — e.g. `waymore -i <TARGET> -mode U | unfurl keys | sort -u` for a live param-key view.
12. Stdin input works: `cat subs.txt | waymore` — use this when harvesting several in-scope hosts in one pass.
13. Note where results land: waymore also saves under its results directory (`~/Tools/waymore/results/<target>/`) — copy the canonical files into `<WORKDIR>/waymore_out/` so the work folder is self-contained.
14. Multi-host merges: when harvesting several in-scope hosts, keep per-host files (`waymore_urls_app.txt`, `waymore_urls_api.txt`) AND a merged `waymore_urls.txt` — per-host files preserve provenance for the handoff counts; the merged file is what the JS filter reads.
15. If X do Y: if the run dies partway (network drop, rate-limit wall), re-running `-mode U` is idempotent enough — dedupe with `sort -u` after merging the partial outputs. If Z pivot: if waymore returns zero URLs for a target you know is old, verify the target spelling (apex vs www matters to the archive) before concluding there's no history.

## Step 4 – Filter to historical JS and download archived bundles
13. Filter the URL list to JS: `grep -iE '\.js(\?|$)' <WORKDIR>/waymore_out/waymore_urls.txt | sort -u > <WORKDIR>/waymore_out/historical_js_urls.txt`.
14. Eyeball the count: `wc -l historical_js_urls.txt`. If it's thousands, prioritize — keep bundle-shaped names (`main.*.js`, `app.*.js`, `chunk-*`) and drop obvious third-party CDN URLs first (they can be revisited).
15. Prioritization heuristic, in order: (a) bundles whose names match the CURRENT bundle roles in inventory_final.json (direct diff possible); (b) bundles with auth/admin/upload/dashboard in the name or path; (c) the largest bundles (more code = more forgotten endpoints); (d) everything else. Work through (a) and (b) completely before touching (d).
16. Download archived bundles with curl, POLITELY: `sleep` between requests — web.archive.org rate-limits aggressively, and a ban mid-harvest kills the run.
16. Save each bundle into `<WORKDIR>/historical/` with a name encoding its archive date: `historical/<name>_<YYYYMMDD>.js`.
17. If X do Y: if a download returns the Wayback "not archived" stub or an HTML error page, delete it immediately — stub files poison the diff. If Z pivot: if downloads are consistently 429/503, back off (longer sleeps, fewer parallel) rather than hammering; a blocked harvest is BLOCKED, documented, never faked.
18. Prefer the OLDEST usable snapshot per bundle, not the newest: the newest archive is usually identical to current code and teaches you nothing. If a bundle has snapshots across years, grab the oldest plus one mid-point — two diffs bracket when an endpoint disappeared.
19. Log every download: URL, archive timestamp, HTTP status, byte size → `<WORKDIR>/waymore_out/download_log.txt`. A bundle that downloaded at 200 but is 400 bytes is a stub until proven otherwise.
20. Dedupe identical bundles by hash before diffing: `sha256sum <WORKDIR>/historical/*.js | sort` — the same bundle archived under five timestamps diffs five times for zero insight; keep the oldest copy per hash and note the dedupe in the log.

## Step 5 – Diff old vs current bundles
20. For each downloaded old bundle, find its current counterpart in `<WORKDIR>/normalized/` (match by bundle role: `main.*.js` ↔ `main.*.js`, not by hash — hashes change every deploy).
21. Diff them: `diff old.js current.js` or feed into the phase-1 `historical/` skill's `diff_old_new.md` — extend that file, don't fork a competing diff.
22. Classify every removed hunk: removed UI string, removed endpoint, removed feature flag, removed auth flow. Removed ENDPOINTS are the prize — list them in `<WORKDIR>/waymore_out/removed_endpoints.txt`.
23. If X do Y: if an old bundle has no current counterpart (whole bundle gone), treat the entire bundle as removed surface — extract all its endpoints per Step 6. If Z pivot: if the diff is empty (archive served the current bundle), the snapshot is useless — pick an older timestamp from the CDX list and re-download.
24. Also record the reverse direction — endpoints present NOW but absent in the old bundle — into `added_endpoints.txt`. New endpoints are the current attack surface's freshest part; `api_analysis` probes them too, but the removed ones stay priority.

## Step 6 – Extract endpoints from old bundles (feed the jsluice workflow)
25. Pipe the downloaded old bundles through the jsluice workflow: `find <WORKDIR>/historical -name '*.js' | jsluice urls -c 5 -S > <WORKDIR>/waymore_out/old_urls.jsonl`.
26. Extract and dedupe: `jq -r '.url' old_urls.jsonl | sort -u > <WORKDIR>/waymore_out/old_endpoints.txt`; params via the same cut-on-`?` split into `old_params.txt`.
27. Subtract the present: `comm -23 old_endpoints.txt <(sort <WORKDIR>/jsluice_out/endpoints.txt) > <WORKDIR>/waymore_out/removed_endpoints.txt` — endpoints that existed in the archive but are absent from current bundles.
28. Flag every line of `removed_endpoints.txt` as a PRIORITY probe for `api_analysis`: removed UI often means still-live backend, and old endpoints skip the WAF rules written for the new frontend.
29. If X do Y: if `removed_endpoints.txt` is dominated by versioned paths (`/v1/...` vs current `/v2/...`), group by version prefix and hand `api_analysis` a version-downgrade probe list — old API versions are the classic still-live backend. If Z pivot: if subtraction yields almost nothing, the archives may all postdate the current deploy — say so in the handoff instead of padding the list.
30. Bonus triage inside the old bundles: grep the OLD code around each removed endpoint for auth headers (`Authorization`, `Bearer`, `x-api-key`). A removed endpoint that the old bundle called WITHOUT an auth header is the highest-value probe of all — it was unauthenticated by design when it was live.

## Step 7 – Exact commands
```bash
# BASELINE: prove waymore works and the target has archive history
waymore -i <TARGET> --check-only
# Expected: an estimate of request count/time. Absurd estimate -> narrow scope before proceeding.

# PROBE: full URL harvest, then filter to JS
mkdir -p <WORKDIR>/waymore_out <WORKDIR>/historical
waymore -i <TARGET> -mode U -oU <WORKDIR>/waymore_out/waymore_urls.txt
grep -iE '\.js(\?|$)' <WORKDIR>/waymore_out/waymore_urls.txt | sort -u > <WORKDIR>/waymore_out/historical_js_urls.txt
wc -l <WORKDIR>/waymore_out/waymore_urls.txt <WORKDIR>/waymore_out/historical_js_urls.txt

# Polite archived-bundle download (web.archive.org rate-limits: sleep between requests)
while read -r u; do
  ts=$(echo "$u" | grep -oP 'web\.archive\.org/web/\K[0-9]{14}' | head -1)
  base=$(basename "${u%%\?*}" .js)
  out="<WORKDIR>/historical/${base}_${ts:-unknown}.js"
  curl -sL --max-time 60 "$u" -o "$out" && sleep 3
  # drop Wayback stub/error pages immediately
  grep -qi 'wayback machine.*not archived\|<html' "$out" && head -c 400 "$out" | grep -qi '<html' && rm -f "$out" && echo "dropped stub: $u"
done < <WORKDIR>/waymore_out/historical_js_urls.txt

# List all archived snapshots of one bundle across time (archive.org CDX API — pick oldest + midpoint)
curl -s "https://web.archive.org/cdx/search/cdx?url=<TARGET>/static/js/main.*.js&output=text&fl=timestamp,original,statuscode&filter=statuscode:200&collapse=digest" \
  | head -20 | tee <WORKDIR>/waymore_out/cdx_main_snapshots.txt

# VERIFY: old-bundle endpoint extraction + subtraction vs current inventory
find <WORKDIR>/historical -name '*.js' | jsluice urls -c 5 -S > <WORKDIR>/waymore_out/old_urls.jsonl
jq -r '.url' <WORKDIR>/waymore_out/old_urls.jsonl | sort -u > <WORKDIR>/waymore_out/old_endpoints.txt
comm -23 <WORKDIR>/waymore_out/old_endpoints.txt <(sort -u <WORKDIR>/jsluice_out/endpoints.txt) \
  > <WORKDIR>/waymore_out/removed_endpoints.txt
echo "old endpoints: $(wc -l < <WORKDIR>/waymore_out/old_endpoints.txt)  removed-not-in-current: $(wc -l < <WORKDIR>/waymore_out/removed_endpoints.txt)"
head -20 <WORKDIR>/waymore_out/removed_endpoints.txt

# Final summary for the handoff note
{
  echo "target: <TARGET>"
  echo "archived_urls: $(wc -l < <WORKDIR>/waymore_out/waymore_urls.txt)"
  echo "historical_js_urls: $(wc -l < <WORKDIR>/waymore_out/historical_js_urls.txt)"
  echo "bundles_downloaded: $(ls <WORKDIR>/historical/*.js 2>/dev/null | wc -l)"
  echo "download_failures: $(grep -c 'FAIL\|429\|503' <WORKDIR>/waymore_out/download_log.txt 2>/dev/null || echo 0)"
  echo "old_endpoints: $(wc -l < <WORKDIR>/waymore_out/old_endpoints.txt)"
  echo "removed_endpoints_priority: $(wc -l < <WORKDIR>/waymore_out/removed_endpoints.txt)"
} | tee <WORKDIR>/waymore_out/harvest_summary.txt
```

## Step 8 – Completion checklist
- [ ] `waymore --check-only` run first; estimate sane (or scope narrowed with reason recorded)
- [ ] Full `-mode U` harvest complete → `<WORKDIR>/waymore_out/waymore_urls.txt`
- [ ] JS filter applied → `historical_js_urls.txt`, `sort -u` deduped
- [ ] Archived bundles downloaded politely (sleeps between requests) into `<WORKDIR>/historical/` with date-stamped names
- [ ] Wayback stub/error pages detected and deleted, not diffed
- [ ] Old-vs-current diff done; phase-1 `diff_old_new.md` extended (not forked)
- [ ] Old bundles piped through jsluice → `old_urls.jsonl`, `old_endpoints.txt`, `old_params.txt`
- [ ] Subtraction vs current `endpoints.txt` → `removed_endpoints.txt` (priority probes)
- [ ] waymore's own results dir (`~/Tools/waymore/results/<target>/`) copied into `waymore_out/` for self-containment
- [ ] `download_log.txt` written (URL, timestamp, status, bytes per download); stubs deleted, not diffed
- [ ] Oldest-usable snapshot preferred per bundle (not just the newest); CDX snapshot list saved
- [ ] `added_endpoints.txt` (present now, absent in old) built alongside `removed_endpoints.txt`
- [ ] Version-downgrade grouping done if removed endpoints cluster on `/v1/` vs current `/v2/`
- [ ] `harvest_summary.txt` written with all handoff counts (URLs, bundles, failures, removed endpoints)
- [ ] Minified-vs-unminified diff noise acknowledged: if the old bundle is unminified and current is minified, diff at the endpoint level (Step 6), not the line level

### Review
A reviewer must verify: (1) `waymore_urls.txt` actually contains archived `web.archive.org` URLs, not live-target URLs — mode U harvests history; (2) every file in `<WORKDIR>/historical/` is real JS (spot-check `head -c 200` — no HTML stubs); (3) `removed_endpoints.txt` is the true set difference (`comm -23` against the CURRENT endpoints.txt, both sorted); (4) no invented waymore flags were used — only `-i`, `-mode U`, `-oU`, `--check-only`/`-co`, `-v`, and stdin piping; (5) the download log proves polite fetching (timestamps spaced seconds apart, no 429 streak ignored).
*Which removed endpoints look like auth/admin/upload flows — those jump the api_analysis probe queue?*
*Is there an old bundle with no current counterpart at all — a fully deleted feature whose backend may still answer?*
*Did the version-downgrade check find a whole old API version (`/v1/`) missing from current bundles — the highest-probability still-live surface?*

"Done" = `<WORKDIR>/waymore_out/` exists with `waymore_urls.txt`, `historical_js_urls.txt`, `old_endpoints.txt`, `removed_endpoints.txt`, and the downloaded archived bundles sit in `<WORKDIR>/historical/`, at those exact paths.

## Step 9 – Evidence standard (no false positives)
- Baseline: `--check-only` output is saved (`waymore_out/check_only.txt`) so the harvest's scale is on record before it runs — no silent mega-runs.
- Removed endpoints are CANDIDATE until `api_analysis` probes them live against a known-dead-path baseline on the same host; a 200 on the old path vs the baseline's 404-pattern is what promotes it.
- Static = CANDIDATE: "present in the 2024 bundle, absent now" is a lead, not a finding — archive snapshots can be partial or mislabeled.
- Blocked = BLOCKED: rate-limited downloads, empty archives, or a target with no Wayback history are documented as BLOCKED/EMPTY with the evidence (`check-only` output, HTTP status), never padded with invented URLs.
- Verdicts: CANDIDATE (removed endpoint, probe queued) / INCONCLUSIVE (archive snapshot ambiguous, e.g. stub-adjacent content) / NEGATIVE (endpoint confirmed dead on live probe).
- Provenance rule: every line in `removed_endpoints.txt` must trace to a dated archived bundle in `<WORKDIR>/historical/` — an endpoint with no archive date is INCONCLUSIVE, because "removed" requires knowing WHEN it was last seen.
- Diff hygiene: `diff_old_new.md` entries carry both timestamps (archive date vs current bundle date); an undated diff entry is worthless for the version-downgrade analysis.
- Wayback stub rule: a downloaded bundle smaller than 2 KB that contains `<html` is a stub page, not a bundle — delete it and log it in the download log, or it pollutes the old-endpoint extraction with archive UI links.
- CDX sanity check: before downloading, confirm each `web.archive.org` URL returns HTTP 200 with `curl -sI` — a 404/302 on the archive URL means the snapshot is dead; skip it rather than saving an error page into `historical/`.
- Timestamp skew rule: if the newest archived bundle is NEWER than the current live bundle, treat the "removed" set with suspicion — the target may have rolled back, and `removed_endpoints.txt` becomes INCONCLUSIVE until the live probe settles it.

## Step 10 – Finished artifact & handoff
- Finished artifact: `<WORKDIR>/waymore_out/` — `waymore_urls.txt`, `historical_js_urls.txt`, `old_urls.jsonl`, `old_endpoints.txt`, `old_params.txt`, `removed_endpoints.txt`, `check_only.txt` — plus downloaded archived bundles in `<WORKDIR>/historical/`.
- Handoff: two consumers —
  - `api_analysis` consumes `removed_endpoints.txt` as its priority probe list (old endpoints feed the version inventory; each line needs the archive date it came from so probes can note "removed circa <date>").
  - The phase-1 `historical_js` skill consumes the extended `diff_old_new.md` (old-vs-current bundle diffs with the waymore snapshots appended, dated).
- Handoff note must state: total archived URLs, JS bundle count, download success/failure counts, and the removed-endpoint count queued as priority probes.
- Also hand `api_analysis` the `added_endpoints.txt` list separately — new endpoints get probed too, but they are NOT priority; the removed ones are, because nobody wrote WAF rules or auth checks for UI that no longer exists.
- One-line handoff summary goes at the top of `waymore_out/README.txt` so the next agent can orient in under a minute: `target=<TARGET> archived_urls=<N> js_bundles=<M> removed_endpoints=<K> harvested=<date>`.
