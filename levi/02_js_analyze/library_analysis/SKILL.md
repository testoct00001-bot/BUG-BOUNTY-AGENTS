---
name: library-analysis
description: >
  Identifies every third-party JavaScript library bundled on the target and pins its exact version, flags outdated packages against current releases, and maps each to known CVEs — all derived from the target's own bundles through deep analysis, never from a generic scanner. USE THIS SKILL whenever the user wants to check JS libraries for CVEs, run an outdated library scan, or answer which jQuery version is bundled. Trigger on: "check JS libraries for CVEs", "outdated library scan", "which jQuery version is bundled". This skill produces the evidence pack – the report_output fires it.
---

# Library Analysis

You are operating as the world's best bug bounty hunter and red teamer. Your job is to produce a library inventory so precise that it separates bundled-but-harmless from actually exploitable on THIS target — the gap between a scanner's noise and a finding generic approaches will never touch.

## Step 1 – Gather inputs

- `<WORKDIR>/inventory_final.json` — which bundle files exist, their sizes and fetch dates
- `<WORKDIR>/normalized/` — deduped, de-obfuscated bundles; your primary evidence
- `<WORKDIR>/sourcemaps/` — `sources[]` arrays; `node_modules/<pkg>/package.json` paths reveal package, version and file path in one shot
- `<WORKDIR>/historical/` — older bundle versions, for upgrade AND downgrade detection
- `<WORKDIR>/tech_choices.md` — if framework-tech already ran, cross-check its version claims
- `<TARGET>` — base URL, used only for live reachability verification

Check first: do the sourcemaps contain `sourcesContent`? If yes, library identification is mostly mechanical. If not, you work from banner comments and version markers — harder, identical evidence bar.

## Step 2 – Enumerate every library from the bundles

2.1 Banner comments: sweep every normalized bundle for license/version banners (`/*! jQuery v3.6.0 */`, `* @license React v18.2.0`). Record name, version, and banner style — banners lie less than heuristics.
2.2 Version markers: grep for `__VERSION__`, `VERSION =`, `version:"x.y.z"`, `.version =`, and `"version": "x.y.z"` literals. A marker inside minified code still pins the version when the literal survives.
2.3 Sourcemap `sources[]`: extract every `node_modules/<pkg>/...` path; the package name is the directory right after `node_modules/` (respect `@scope/name` for scoped packages). The deepest `package.json` in the path is authoritative.
2.4 Webpack chunk headers: production builds keep module comment paths like `./node_modules/lodash/lodash.js:` — package names survive even when banners are stripped.
2.5 License files: `3rdpartylicenses.txt`, `.LICENSE.txt`, `LICENSES.chunks` shipped next to bundles. A lib in the license file but missing from your bundle sweep means your sweep has a hole — find it.

Decision branches: if two versions of the same lib appear in different chunks → keep both rows; the vulnerable one may be the dead-code twin. If markers conflict → sourcemap wins, banner second, heuristic last; mark the conflict explicitly. If a "library" is first-party code vendored under `node_modules/` → reclassify as first-party and note it.

Transitive dependencies deserve their own pass: a CVE in `lib Y` still counts when the bundle ships `node_modules/libX/node_modules/libY/` — the vulnerable code is on the page regardless of which parent pulled it in. When an advisory names a dependency rather than the top-level package, grep the sourcemap `node_modules/` tree for the nested path and treat the parent package's version as irrelevant; pin the nested copy's version from its own `package.json` path or banner.

## Step 3 – Build the outdated table

3.1 For each pinned version, check the current release with `npm view <pkg> version`. Record latest version plus its release date.
3.2 Compute drift: patch-behind, minor-behind, major-behind. Flag REVIEW any lib ≥ 1 major behind, ≥ 6 months since last release, or marked deprecated/EOL by its maintainer.
3.3 Compare against `<WORKDIR>/historical/`: did the target upgrade or DOWNGRADE? A downgrade silently re-opens old CVEs — call it out with both versions quoted.

If the npm registry is unreachable → fall back to a web search for "<pkg> latest version release date" and mark the source column FALLBACK. Outdated ≠ vulnerable: this table is the candidate list for CVE mapping, nothing more. Never let a red "outdated" cell become a finding by itself.

## Step 4 – Map CVEs per outdated library

4.1 For every REVIEW-flagged lib, query NVD and the GitHub Advisory Database for CVEs whose affected range includes the pinned version.
4.2 Record per CVE: CVE ID, affected version range, the vulnerable function or component, the trigger conditions the advisory describes, and the advisory's own severity — never invent or inflate severity.
4.3 Separate two states sharply: "pinned version in affected range" = CANDIDATE (static, unverified). "Exploitable on this target" = unproven until Step 5 passes. A lib with no CVEs in range gets NEGATIVE with the search date — never leave a row blank.

Cross-reference the fix: read the advisory's fixed version and, when available, the fix commit. The commit names the exact vulnerable function and the trigger shape — that is your grep target in Step 5, not the CVE description's prose. If the fix touched a file whose path never appears in the bundle's sourcemap tree, say so; it strengthens a NEGATIVE.

## Step 5 – Reachability analysis: THE HARD RULE

A CVE in a bundled library is NOT a finding until you demonstrate the vulnerable code path is reachable on this target: the vulnerable function is actually invoked with attacker-influenced input, or the vulnerable component actually renders attacker-reachable data.

5.1 For each CANDIDATE CVE, grep `normalized/` for the vulnerable function's call sites. Zero call sites → NEGATIVE, reason "vulnerable function present but never called on this target".
5.2 If called: trace the arguments one hop back to their source. Attacker-influenced = URL params, `location.hash`, `postMessage` data, `localStorage`/`sessionStorage` values, or server API responses rendered into the DOM. Hardcoded strings and build-time constants are NOT attacker input — no matter how tempting.
5.3 If the CVE is in a rendering component (date picker, rich-text renderer, markdown parser): find where it mounts in the app — which page, which API response, which user action feeds it.
5.4 Called only with trusted constants → NEGATIVE or INCONCLUSIVE with the exact call site quoted and the reason stated ("sink reachable only from build-time constant").
5.5 Called with attacker-influenced input → CONFIRMED-CANDIDATE: write the PoC against THIS target's real entry point (actual URL + parameter), reproduce the behavior twice via the target's own input path, and save raw request/response pairs to disk. Blocked anywhere (auth wall, WAF, page unreachable unauthenticated) → BLOCKED with the exact blocker; never fabricate the missing hop to keep a finding alive.

Minified aliasing: the vulnerable function may be renamed in the bundle (`o.html(` instead of a readable name). If the advisory's function name yields zero hits, locate the library's code region via its banner offset and search for the sink pattern structurally (e.g. any `.html(` call within 200KB after the jQuery banner) before concluding NEGATIVE.

## Step 6 – Worked mini-example: jQuery < 3.5.0 `.html()` XSS

6.1 CVE-2020-11022 / CVE-2020-11023: jQuery before 3.5.0 passes HTML through `.html()` with insufficient sanitization — a real XSS sink, but only if reached.
6.2 Pin the version: banner `/*! jQuery v3.4.1 */` in `normalized/app.9f2c.js` → pinned version inside the affected range → CANDIDATE, not a finding.
6.3 Find the sinks, trace one hop, then judge: grep `normalized/` for `.html(` call sites and discard on sight any fed by hardcoded template strings. Is a remaining argument built from `location.search`, `location.hash`, a `postMessage` payload, or an API response rendered verbatim — e.g. `$('#result').html(data.message)` where `data` comes from `fetch('/api/search?q=' + userInput)`? If yes → attacker-influenced source reaches a vulnerable sink → CONFIRMED-CANDIDATE, and only now do you craft the PoC through the target's own search box or reflected parameter, reproduce 2x, save raw pairs, and report. If every `.html()` call takes a hardcoded string → NEGATIVE: "vulnerable sink present, no attacker-reachable source on this target."

## Step 7 – Exact commands

```bash
# BASELINE — calibrate this host's dead-path signature before any live verification
curl -sS -o /tmp/levi_baseline_dead.html -D /tmp/levi_baseline_dead.hdrs \
  -w 'code=%{http_code} size=%{size_download}\n' \
  'https://<TARGET>/levi-dead-path-9f3a2c1d'
md5sum /tmp/levi_baseline_dead.html
```

```bash
# PROBE — library banners and version markers from normalized bundles
cd <WORKDIR>
grep -rhoE '/\*!?[^\n*]{0,140}' normalized/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -80 > /tmp/levi_lib_banners.txt
grep -rhoE '"version"[[:space:]]*:[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+[^"]{0,20}"' \
  normalized/ 2>/dev/null | sort | uniq -c | sort -rn | head -40
```

```bash
# PROBE — package names from sourcemap sources[] (most reliable signal)
cd <WORKDIR>
for m in sourcemaps/*.map; do jq -r '.sources[]' "$m" 2>/dev/null; done \
  | grep -oE 'node_modules/(@[^/]+/[^/]+|[^/]+)' | sort | uniq -c | sort -rn | head -60
```

```bash
# VERIFY — latest release per package for the outdated table
npm view <pkg> version
# recent release history; if unsure of flags, verify with `npm view --help` first
npm view <pkg> versions --json | tail -5
```

```bash
# VERIFY — reachability: is the vulnerable function actually called on this target?
cd <WORKDIR>
grep -rn '\.html(' normalized/ | head -30
```

```bash
# VERIFY — historical comparison: upgrades AND downgrades across bundle versions
cd <WORKDIR>
for f in historical/*.js; do
  echo "== $f =="
  grep -oE '/\*!?[^\n*]{0,120}' "$f" 2>/dev/null | head -10
done > /tmp/levi_lib_history.txt
diff <(sort /tmp/levi_lib_banners.txt) <(sort /tmp/levi_lib_history.txt) | head -40
```

Never live-test a suspected leaked secret found in a bundle — redact it in every report and flag it for the user's explicit approval first.

## Step 8 – Completion checklist

- [ ] Inputs gathered: inventory, normalized bundles, sourcemaps, historical, tech_choices.md
- [ ] Every library enumerated with pinned version, identification method, and confidence
- [ ] Version conflicts resolved (sourcemap > banner > heuristic) and documented
- [ ] Outdated table built: pinned vs latest, drift, REVIEW flags, historical deltas
- [ ] CVE mapping complete for every REVIEW lib; no blank rows
- [ ] Reachability analysis run per CANDIDATE CVE with call-site evidence quoted
- [ ] PoCs only in the real trigger context; 2x reproduction; raw pairs saved under `<WORKDIR>/raw/`
- [ ] Transitive/nested copies checked via the sourcemap `node_modules/` tree
- [ ] Fix commits consulted so the Step 5 grep targets the real vulnerable function
- [ ] `<WORKDIR>/libraries.md` written at its exact path

### Review
A reviewer must verify: every version pin traces to a quoted banner, marker, or sourcemap line; every CVE row carries a reachability verdict with either the call-site evidence or the exact reason for NEGATIVE; no row claims exploitability from a version number alone.

*Did any library appear in two versions across chunks — and did you check the older twin for the CVE?*
*For each CONFIRMED-CANDIDATE, can you name the exact URL and parameter where attacker input reaches the sink?*
*Which NEGATIVE verdicts are one code change away from flipping — and did you say so in the file?*

Done = `<WORKDIR>/libraries.md` exists on disk with the inventory table, the outdated table, and a per-CVE reachability verdict.

## Step 9 – Evidence standard (no false positives)

- Baseline every live verification against the known-dead path from Step 7: a "live" response matching the dead-path signature (status + size + hash) is the SPA fallback, not a finding.
- 2x independent reproduction for any behavioral PoC; raw request/response pairs saved under `<WORKDIR>/raw/` with timestamps.
- Verdicts: CONFIRMED (reachable + reproduced twice), INCONCLUSIVE (evidence ambiguous, next step named), NEGATIVE (checked, not exploitable, reason quoted), BLOCKED (could not test, exact blocker documented).
- Static findings — version in affected range with no reachability proof — stay CANDIDATE. They are never reported as vulnerabilities.
- Secrets found in bundles are redacted in every report and never live-tested without the user's explicit approval.

## Step 10 – Finished artifact & handoff

Artifact: `<WORKDIR>/libraries.md`, three sections:
1. Library inventory table — package, pinned version, identification method, confidence, bundle file
2. Outdated table — pinned vs latest, drift, REVIEW flags, historical upgrade/downgrade deltas
3. CVE mappings — one row per CVE with reachability verdict (CONFIRMED / INCONCLUSIVE / NEGATIVE / BLOCKED) and the evidence or reason

Handoff: `report_output` consumes only reachable items — CONFIRMED verdicts. NEGATIVE rows stay in the file as audit trail, never as findings. `feature_map` consumes vulnerable-library usage as feature-level leads (e.g. "outdated rich-text renderer used by the comments feature → XSS lead on the comment submit endpoint").
