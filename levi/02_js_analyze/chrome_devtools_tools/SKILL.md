---
name: chrome-devtools-tools
description: >
  Squeezes the live app for what static analysis cannot see: which code actually executes, which API calls the app really makes at runtime, and live filter-bypass tests via Local Overrides — all without touching the server beyond normal browsing. USE THIS SKILL whenever the user wants to run a DevTools coverage analysis, export a HAR, re-rank gadget reachability against live code, or test a sanitizer hypothesis with local overrides. Trigger on: "devtools coverage analysis", "export HAR", "local overrides testing". This skill produces the live runtime ammunition — the dangerous_functions_gadgets skill fires it.
---

# Chrome DevTools Workflow

You are operating as the world's best bug bounty hunter and red teamer. Your job is to extract the runtime truth that static analysis cannot see — which sinks actually execute, which endpoints the app really calls, and whether a filter hypothesis holds under live code — so every downstream gadget and API lead is ranked by reality, not by grep.

## Step 1 – Gather inputs

- `<TARGET>`: the live target host/URL (same origin the phase-1 JS was harvested from).
- `<WORKDIR>`: the target work folder containing `raw/*.js`, `normalized/`, `inventory_final.json`, and phase-2 artifacts produced so far — especially `gadgets.json` (dangerous_functions_gadgets output: sink → file → line → source trace) and the static API list from `jsluice`.
- Context you must know before touching DevTools: the app's auth model (anonymous vs authenticated journey available), which phase-2 gadget hypotheses are the top 3 candidates for override testing, and any anti-automation behavior (bot walls, WAF) that would poison a headless capture — if the app fights automation, do the capture in a real, attended Chrome session instead.
- Check first: can you reach `<TARGET>` in a normal browser and does the app boot to an interactive state? If it does not boot, STOP — there is no runtime to analyze; document as BLOCKED and move on.

## Step 2 – Coverage capture and sink reachability re-ranking

1. Open Chrome, navigate to `<TARGET>`, open DevTools, press Cmd/Ctrl+Shift+P, type "Show Coverage", and start coverage recording. Hard-reload the app (Cmd/Ctrl+Shift+R) and exercise every reachable UI surface: click through nav, open every drawer/modal, submit every form with benign input, trigger every tab.
2. Stop recording and export the coverage as JSON (Coverage panel → export icon). Save the raw export to `<WORKDIR>/devtools_notes.md`'s companion raw file — the JSON itself goes to `<WORKDIR>/raw/coverage.json`; never analyze only the colored rows by eye.
3. Parse the JSON with python3: for each script URL, compute `executed_bytes / total_bytes` per function range. Red rows = dead code (never executed); green = executed. Write the per-file executed ratio into the coverage summary table.
4. Intersect coverage with `gadgets.json`: for every gadget sink, look up whether its file+line range falls inside an executed range. A sink in dead code is DEPRIORITIZED (not deleted — see sub-step 6). A sink in executed code jumps the queue to the top of the override-test list. Record the old rank → new rank delta for each gadget.
5. Re-run your sink/source greps against the LIVE-loaded code, not the static files: in DevTools Sources, Ctrl+Shift+F searches across ALL loaded scripts including lazy chunks fetched after boot. Static harvests routinely miss lazy chunks, service-worker scopes, and dynamically-imported bundles — anything your grep finds in live code that was absent from `raw/` is a phase-1 gap; note it and (if valuable) add the chunk URL to the download list for the next phase-1 pass.
6. Decision branch — the "removed UI, live backend" case: if dead (red) code contains fetch/XHR calls to endpoints that respond live, that is a HIGH-VALUE lead, not a dead end. Dead UI + live backend = hidden attack surface the developers thought they removed. If you find this, do NOT deprioritize: pivot immediately to testing those endpoints directly (hand the endpoint list to api_analysis with the flag `removed-ui-live-backend`). If no dead-code endpoint responds live, deprioritize the dead-code sinks normally.
   Coverage trap: the exported JSON nests ranges inside `functions[]` per script — a script that appears 90% green can still hide every sink inside the 10% red. Always intersect at the RANGE level (file + line within executed ranges), never at the file level. File-level green is how gadgets get falsely promoted.
   Example delta table row for devtools_notes.md: `POST /api/v2/internal/sync | runtime-only | 200, 14KB JSON | fired by lazy chunk cart-drawer.js (not in raw/) | PRIORITY: runtime-confirmed`.
   HAR size trap: a 60-second journey with polling can produce a 50MB+ HAR dominated by identical beacon requests. Dedupe BEFORE reading — the python extractor above does this via the `seen` set. If `journey.har` exceeds 100MB, re-capture with "Preserve log" on but the Media/WS filters hiding noisy frames, or trim `entries` to unique (method, path) before saving.

## Step 3 – HAR capture of a full user journey and runtime API extraction

7. With coverage still fresh or in a clean session, open DevTools → Network, enable "Preserve log" and disable cache. Walk the FULL user journey: the authenticated journey if credentials exist, otherwise the complete anonymous journey (every page, every widget, every poll/retry — wait at least 60 seconds on the main view to catch polling and beacons).
8. Right-click any request → "Save all as HAR with content". Save to `<WORKDIR>/raw/journey.har`. HAR-with-content is mandatory: without bodies you cannot distinguish a 200-empty from a 200-with-data, and body content reveals error schemas and undocumented fields.
9. Parse the HAR with python3 (or jq): extract every request as `METHOD + URL + status + response_size + content_type`. Dedupe by (method, path-normalized URL). Sort by method, then path. This is the RUNTIME API LIST — what the app ACTUALLY called, which is ground truth in a way static analysis never is.
10. Diff the runtime list against the jsluice static endpoint list: compute the DELTA in both directions. Runtime-only calls (present in HAR, absent from static) are high-value — typical members: lazy-chunk APIs, analytics/telemetry beacons, polling endpoints, retry/fallback URLs, and endpoints built by string concatenation that static parsing choked on. Static-only calls (in jsluice, never fired in your journey) are CANDIDATE-unexercised — keep them, but mark them as not runtime-confirmed.
11. Decision branch: any runtime-only endpoint with a state-changing method (POST/PUT/PATCH/DELETE) goes to the TOP of the api_analysis queue with the note `runtime-confirmed`. Read-only GET beacons go to a low-priority telemetry note — they are time-pass surface unless they leak data in query params. If a runtime call returns 4xx/5xx consistently, note the error schema: verbose error bodies are an information-leak lead for report_output.
12. While the journey is fresh, harvest the Application panel: dump `localStorage` and `sessionStorage` (feature flags, rollout keys, debug toggles — anything named `*debug*`, `*flag*`, `*admin*`, `*internal*`), list cookies with their flags (HttpOnly/Secure/SameSite — a session cookie missing these is a finding), and enumerate IndexedDB databases/object stores (cached API responses often contain data the UI never renders).

## Step 4 – Local overrides for live filter-bypass testing

13. Pick the TOP 3 gadget hypotheses from the re-ranked list (Step 2). For each, set up Local Overrides: Sources → Overrides → select an EMPTY local folder → allow DevTools → find the served JS file containing the sink → right-click → "Save for overrides" → edit the local copy in place.
14. The standard override experiment: NEUTRALIZE the sanitizer/validator guarding the sink (e.g. replace the sanitize call with a pass-through) and reload. If the sink now fires on your probe input, the hypothesis is LIVE-VERIFIED as a code path — this proves the sink is reachable and the only thing standing between you and it is the filter, which is exactly the bypass problem to solve next. If the sink still does not fire, your source trace was wrong: re-trace before claiming anything.
   Keep experiments surgical: override ONE file and ONE guard per test. Overriding three sanitizers at once tells you nothing about which one mattered — and a sink that fires only when every guard is down is a weaker lead than one that fires when a single guard is down.
15. Document EVERY override in the overrides log (file, original line, exact edit, hypothesis, result). REVERT all overrides when the experiment ends — delete the override files or disable the Overrides folder. Overrides never leave the local machine and never touch the server; they modify only what YOUR browser executes.
16. Decision branch: if neutralizing the sanitizer fires the sink AND the sanitizer is client-side-only (no server-side re-validation observed in the HAR for that flow), escalate the gadget to CONFIRMED-impact pending a real bypass payload — hand it to dangerous_functions_gadgets with `client-side-only-filter`. If the HAR shows the same validation enforced server-side (422/400 on malformed input to the endpoint), the gadget is INCONCLUSIVE for unauthenticated impact — document and move on, do not burn hours on a filter the server re-checks.
17. Coverage over-counting caveat: a range counts as "executed" if it ran ONCE, including boot-time init, error-handler fallbacks, and polyfill shims. Do not treat "executed" as "user-reachable". Before promoting a gadget on coverage alone, confirm the sink's range executed during YOUR interactive journey (compare a boot-only coverage export against a post-journey export — sinks that only appear in the delta are the ones a user can actually reach).
18. Scrub the HAR before it leaves your machine: HAR-with-content routinely captures Authorization headers, session cookies, and tokens. Redact `Authorization`, `Cookie`, and `*-token*` values in `<WORKDIR>/raw/journey.har` (keep a `.redacted` copy as the shareable one) and NEVER paste raw HAR content into reports, tickets, or chat. The redacted copy is what report_output's Evidence appendix may reference.

## Step 5 – Exact commands

```bash
# BASELINE — known-dead path on the same host. Everything runtime is compared against this.
curl -sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n' \
  "https://<TARGET>/this-path-definitely-does-not-exist-9f3k2"
# Record the status code + body size above. A "live" candidate must differ from BOTH,
# not just the status code (SPA fallbacks return 200 with the index.html body — compare sizes).

# BASELINE — prove the target serves JS normally and DevTools can attach.
# (Manual: open https://<TARGET>, DevTools → Coverage → reload. Then:)
ls -la <WORKDIR>/raw/coverage.json && python3 -c "import json;d=json.load(open('<WORKDIR>/raw/coverage.json'));print('scripts captured:',len(d))"

# PROBE — parse coverage JSON into a per-file executed-ratio table.
python3 - <<'EOF'
import json
cov=json.load(open('<WORKDIR>/raw/coverage.json'))
for e in cov:
    url=e.get('url','?')
    total=used=0
    for f in e.get('functions',[]):
        for r in f.get('ranges',[]):
            total+=r['end']-r['start']
            if r['count']>0: used+=r['end']-r['start']
    print(f"{used/total*100:5.1f}%  {url}")
EOF

# PROBE — extract the runtime API list from the HAR.
python3 - <<'EOF'
import json
from urllib.parse import urlparse
har=json.load(open('<WORKDIR>/raw/journey.har'))
seen=set()
for e in har['log']['entries']:
    r=e['request']; s=e['response']['status']
    p=urlparse(r['url']).path or '/'
    key=(r['method'],p)
    if key not in seen:
        seen.add(key)
        print(f"{r['method']:6} {s}  {p}")
EOF

# VERIFY — diff runtime API list vs the jsluice static list.
comm -23 <(python3 -c "
import json;from urllib.parse import urlparse
har=json.load(open('<WORKDIR>/raw/journey.har'))
for e in sorted({(x['request']['method'],urlparse(x['request']['url']).path) for x in har['log']['entries']}): print(e[0],e[1])" | sort -u) \
       <(sort -u <WORKDIR>/api_static_list.txt) > <WORKDIR>/runtime_only.txt
echo "runtime-only endpoints:"; cat <WORKDIR>/runtime_only.txt

# HEADLESS CDP (verified pattern) — rendered DOM snapshot without a GUI.
google-chrome --headless=new --remote-debugging-port=9222 https://<TARGET> >/dev/null 2>&1 &
sleep 3
curl -s http://localhost:9222/json | python3 -c "import json,sys; [print(t['type'],t['url']) for t in json.load(sys.stdin)]"
```

## Step 6 – Completion checklist

- [ ] Coverage recorded across a full UI walk, exported to `<WORKDIR>/raw/coverage.json`
- [ ] Per-file executed-ratio table computed and written into devtools_notes.md
- [ ] Every gadget sink intersected with coverage ranges; old→new rank deltas recorded
- [ ] Sources global search (Ctrl+Shift+F) re-run against live-loaded code; lazy-chunk gaps noted
- [ ] "Removed UI, live backend" case explicitly checked (dead-code fetch/XHR targets probed)
- [ ] Full user journey walked (auth if available, else anonymous + 60s dwell); HAR with content saved to `<WORKDIR>/raw/journey.har`
- [ ] Runtime API list extracted, deduped, and diffed against the jsluice static list; `runtime_only.txt` written
- [ ] Runtime-only state-changing endpoints flagged to api_analysis as `runtime-confirmed`
- [ ] Application panel harvested: localStorage/sessionStorage flags, cookie flags, IndexedDB stores
- [ ] Top 3 gadget hypotheses tested with Local Overrides; every override logged with exact edit + result
- [ ] All overrides reverted/disabled; overrides confirmed local-only
- [ ] Boot-only vs post-journey coverage delta computed; user-reachable sinks identified
- [ ] HAR scrubbed of Authorization/Cookie/token values; redacted copy saved
- [ ] `<WORKDIR>/devtools_notes.md` written with all four sections

### Review

A reviewer must verify: (a) coverage.json and journey.har exist on disk and are non-trivial in size; (b) the static-vs-runtime delta table names specific endpoints, not vague claims; (c) every override log entry has a result (fired / did-not-fire) and a revert note; (d) no gadget was marked CONFIRMED on coverage alone — coverage re-ranks, it does not prove exploitability.

*Did any sink move from "dead code" to top priority — and can you name the exact line that executed?*
*Which runtime-only endpoint surprised you most, and what method does it accept?*
*If you had to delete one section of devtools_notes.md, which finding would you still defend?*

Done = `<WORKDIR>/devtools_notes.md` exists on disk with coverage summary, HAR-derived runtime API list, static-vs-runtime delta table, and overrides log — all four sections populated. If any section is empty, say WHY it is empty (e.g. "no lazy chunks loaded during journey") rather than padding it — an honest gap beats a fabricated table.

## Step 7 – Evidence standard (no false positives)

- Coverage claims are verified against the exported JSON (`raw/coverage.json`), not the colored DevTools rows — eyeballing red/green is a CANDIDATE observation until the byte ranges are computed.
- "Removed UI, live backend" endpoints are verified with 2x independent requests against a known-dead path on the same host as baseline: the dead path must return the app's standard 404/fallback while the candidate returns a distinct live response. One divergent status code is not enough — confirm twice, minutes apart.
- Override experiments prove code-path reachability only. A sink that fires after sanitizer neutralization is a LIVE-VERIFIED PATH, not a CONFIRMED vulnerability — verdict stays CANDIDATE until a real bypass payload executes without the override.
- Application-panel flags are observations, never findings: a `debug=true` flag in localStorage is not a vulnerability until you demonstrate what it unlocks.
- Blocked = BLOCKED: if anti-automation walls, login walls, or WAF blocks prevented the journey or headless capture, document exactly what blocked you and stop — never fabricate a HAR or coverage table.

## Step 8 – Finished artifact & handoff

Finished artifact: `<WORKDIR>/devtools_notes.md` — four sections, in this order: (1) coverage summary table (script URL | executed % | gadget sinks inside), (2) HAR-derived runtime API list (`METHOD status path`, deduped), (3) static-vs-runtime delta table (runtime-only | static-only-unexercised, with notes), (4) overrides log (hypothesis | file:line | edit | result | reverted?). Companion raw files: `<WORKDIR>/raw/coverage.json`, `<WORKDIR>/raw/journey.har`, `<WORKDIR>/runtime_only.txt`.

Handoff:
- **dangerous_functions_gadgets** consumes the coverage summary + overrides log: re-rank every sink by executed-vs-dead, and promote the top-3 override results (with `client-side-only-filter` flags where they apply).
- **api_analysis** consumes the runtime API list + `runtime_only.txt`: merge runtime-confirmed endpoints into `api_map.md`, prioritizing runtime-only state-changing methods.
- **report_output** consumes the full `devtools_notes.md` for the Evidence appendix and the Feature-leads section (feature flags from the Application panel).

When in doubt, capture more and claim less: a bloated HAR you never cite costs disk; a thin claim you cannot reproduce costs credibility.

---
