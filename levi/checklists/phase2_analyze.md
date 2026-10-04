# .MD Checklist — Phase 2 — Analyze

> Pipeline 1, Phase 2: the JS inventory becomes a verified attack surface.

> **Iron rule:** a box with no checkmark means the agent has NOT finished that step.
> Not finished means the skill gets **re-run** — not argued with, not summarized, re-run.
> Copy this file per target as `<target>_<date>.md` and tick boxes as you go.
**Skills in this phase:** 11 | **Total boxes:** 133

## API Analysis (`api-analysis`)

**Finished artifact:** `<WORKDIR>/api_map.md` — four sections: (1) base URLs + auth mechanics, (2) method-mapped endpoint tables grouped by functionality with params and rank, (3) old-version inventory (path/header/legacy), 

- [ ] Base URLs extracted and env vars resolved to literal values
- [ ] Auth-header mechanics documented per API client
- [ ] Method-mapped endpoint table built (METHOD | path | params | auth)
- [ ] Endpoints grouped by functionality and ranked auth > payment > admin > upload > profile > search > notifications
- [ ] Old-version inventory complete (path versions, header versions, legacy/internal paths)
- [ ] v1 twins constructed for v2 endpoints; live-vs-referenced status recorded
- [ ] Downgrade tests run: identical replay v2→v1, plus version-header variant
- [ ] Every claim verified baseline → probe → 2x repro; raw pairs in <WORKDIR>/raw/
- [ ] v1 twins that 404 identically to the dead baseline marked NEGATIVE (not retried endlessly)
- [ ] Method anomalies documented; no destructive action triggered without approval
- [ ] Verdicts assigned: CONFIRMED / INCONCLUSIVE / CANDIDATE / NEGATIVE / BLOCKED

## Chrome DevTools Workflow (`chrome-devtools-tools`)

**Finished artifact:** `<WORKDIR>/devtools_notes.md` — four sections, in this order: (1) coverage summary table (script URL | executed % | gadget sinks inside), (2) HAR-derived runtime API list (`METHOD status path`, deduped

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

## Dangerous Functions & Gadget Mapping (`dangerous-functions-gadgets`)

**Finished artifact:** `<WORKDIR>/gadgets.json` — one JSON array; each record has `file, line, sink, sink_class, source, chain (source → sink → trigger), context_snippet, filter_notes, payload, verdict (CANDIDATE|INCONCLUSIV

- [ ] gadget_mapper.py ran over normalized/ → <WORKDIR>/gadgets_raw.json exists
- [ ] Sink classes inventoried (code-exec > HTML > navigation > postMessage), vendor copies marked
- [ ] DOM-clobbering sources recorded alongside sinks
- [ ] Ranked triage list written to <WORKDIR>/gadgets_triage.md
- [ ] Reachability triage done: dead-code / auth-gated sinks marked NEGATIVE or BLOCKED
- [ ] Dynamic-argument check passed for every survivor (static strings → NEGATIVE)
- [ ] Backward source trace completed for every survivor; no-trace sinks stay CANDIDATE
- [ ] Gadget chains (source → sink → trigger) built for traced pairs
- [ ] Filter analysis per context done; minimal payloads crafted, canary-first
- [ ] Live verification: baseline + 2x repro, raw pairs saved to <WORKDIR>/raw/gadget_<sinkid>_probeN.txt
- [ ] postMessage listeners checked for origin validation; no-check listeners tested with the trigger harness
- [ ] Every CONFIRMED item's payload is the MINIMAL one for its context (no spray-and-pray lists in the evidence)
- [ ] No secret encountered during tracing was live-tested; all redacted in the triage notes
- [ ] gadgets.json verdict field reviewed record-by-record: no CANDIDATE promoted without 2x live repro
- [ ] Triage notes record the exact filter/sanitizer that killed each NEGATIVE sink (for the audit trail)
- [ ] Final verdicts recorded: CONFIRMED / INCONCLUSIVE / NEGATIVE / BLOCKED

## Feature Map (`feature-map`)

**Finished artifact:** Artifact: `<WORKDIR>/feature_map.md` — the feature table (`| Feature | Entry point | Data flow | Auth observed | THE LEAD |`) followed by the ranked hunt leads (P1 first), each lead naming the exact endpoint and paramete

- [ ] Inputs gathered: normalized bundles, sourcemap tree, inventory, tech_choices.md, libraries.md
- [ ] Feature-pattern sweep run for all seven clusters in Step 2
- [ ] Every hit recorded with exact string + file; rumor-features dropped
- [ ] Hits clustered per feature; entry points extracted with methods and params
- [ ] Cross-origin features recorded with their host and trust boundary
- [ ] One-hop data flow traced per entry point; auth observations recorded
- [ ] Lead table written; every row names the exact endpoint + param or it was deleted
- [ ] Leads ranked P1/P2/P3 by leak × sensitive × unauthenticated
- [ ] Time-pass surface excluded — no lead rows for marketing/static content
- [ ] `<WORKDIR>/feature_map.md` written at its exact path

## Framework & Tech Analysis (`framework-tech`)

**Finished artifact:** Artifact: `<WORKDIR>/tech_choices.md` — table `| Choice | Version | Evidence | Confidence | Why it matters for content discovery |`, one row per choice (framework, build tool, rendering mode, backend hints), no row witho

- [ ] Homepage HTML + headers fetched and saved to disk
- [ ] Framework marker sweep run across homepage, normalized bundles, and raw bundles
- [ ] Every marker scored STRONG / WEAK with the exact string quoted
- [ ] Conflicts resolved via the bootstrap test; embedded/legacy frameworks marked
- [ ] Build tooling fingerprinted and confirmed via the sourcemap prefix
- [ ] Rendering mode determined (SSR / CSR / hybrid) with evidence
- [ ] Backend hints recorded, or explicitly marked hidden behind the CDN
- [ ] Framework version pinned from evidence; buildId never mistaken for a version
- [ ] `<WORKDIR>/tech_choices.md` written, every row carrying its content-discovery annotation

## JSLuice / jxscout Extraction (`jsluice-jxscout-tools`)

**Finished artifact:** - Finished artifact: `<WORKDIR>/jsluice_out/` — `urls.jsonl`, `urls_resolved.jsonl`, `secrets.jsonl`, `endpoints_raw.txt`, `endpoints.txt`, `params.txt`, `thirdparty_urls.txt`, `urls_errors.log` — all deduped. - Handoff:

- [ ] `jsluice` verified installed (or documented fallback to the python parser above)
- [ ] `<WORKDIR>/jsluice_out/urls.jsonl` exists; `.url` field shape confirmed with the baseline probe
- [ ] `endpoints_raw.txt` extracted via jq and `sort -u` deduped
- [ ] Paths vs query params split: `endpoints.txt` and `params.txt` both exist and are deduped
- [ ] EXPR-placeholder lines kept raw AND emitted as `{param}`-normalized variants
- [ ] Relative paths resolved with `-R https://<TARGET>`; out-of-scope hosts moved to `thirdparty_urls.txt`
- [ ] `jsluice secrets` run → `secrets.jsonl`; cross-checked against secrets_analysis engine 1
- [ ] jxscout handled correctly: `--help` first if present, never assumed flags
- [ ] Parse errors captured in `urls_errors.log`; skipped files routed to the python fallback
- [ ] `endpoints_hot.txt` (auth/admin/upload-shaped) and `params_auth_shaped.txt` triage subsets built
- [ ] Custom tree-sitter queries that worked recorded in `queries_used.txt`
- [ ] `sibling_hosts.txt` created if `-R` surfaced unexpected subdomains (else noted as none found)
- [ ] EXPR-obscured line count recorded; manual source-read queued for the auth/admin-shaped ones

## Library Analysis (`library-analysis`)

**Finished artifact:** Artifact: `<WORKDIR>/libraries.md`, three sections: 1. Library inventory table — package, pinned version, identification method, confidence, bundle file 2. Outdated table — pinned vs latest, drift, REVIEW flags, historic

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

## Params & Route Analysis (`params-routes`)

**Finished artifact:** `<WORKDIR>/routes_params.md` — five sections: (1) route table (path | framework | lazy chunk | auth guard | unauth reachability), (2) admin paths with guard analysis + probe verdicts, (3) feature flags

- [ ] Router framework detected and documented
- [ ] Full route table extracted (including lazy-chunk routes) → normalized into path|framework|guard table
- [ ] Admin-path sweep done; every hit checked for client-side-only vs server-backed guards
- [ ] Each admin/feature route probed live vs the 404 baseline (baseline recorded first)
- [ ] Feature-flag SDK markers, query-param flags, storage flags, and config-embedded flags extracted
- [ ] Comments of interest harvested (TODO/FIXME/HACK/staging URLs/internal hostnames)
- [ ] Param inventory built with occurrence counts from jsluice + URLSearchParams + route params
- [ ] Every param annotated with suspected vuln class + reachability note
- [ ] Every inventory row has read-location AND flow-destination (no orphan rows)
- [ ] Raw evidence files saved under <WORKDIR>/raw/

## Report & Curl Output (`report-output`)

**Finished artifact:** Finished artifacts: - `<WORKDIR>/report.md` — the full report in the exact section template above. - `<WORKDIR>/curl_commands.sh` — executable re-verification kit: `#!/usr/bin/env bash` + `set -euo pipefail`, one BASELIN

- [ ] All phase-2 artifacts located; missing ones noted as gaps, not invented
- [ ] report.md header: date, scope, recomputed inventory size (N files / M KB)
- [ ] Summary: 3–6 bullets, CONFIRMED-only findings, one ruled-out bullet
- [ ] Tech choices condensed to ≤5 lines
- [ ] Endpoints table grouped by functionality with `auth observed` as seen, not assumed
- [ ] Routes & params with suspected class + verdict per item
- [ ] One gadget block per gadget: sink, source trace, context snippet, bold verdict
- [ ] Secrets table REDACTED (file | line | pattern_name | value_redacted | verdict) — no full values
- [ ] Libraries: outdated + CVE each with reachability verdict
- [ ] Feature leads ranked table from feature_map.md
- [ ] Evidence appendix: raw pairs for every CONFIRMED item + baseline command + 2x repro notes
- [ ] Blocked section: every BLOCKED item with reason
- [ ] curl_commands.sh: template header, one block per CONFIRMED item (baseline + probe), fixed flags, `<TARGET>` placeholders, no real secrets, chmod +x, `bash -n` clean
- [ ] Kill pass done: anything below the bar cut or demoted, with the demotion stated
- [ ] Fresh-eyes re-read done on Summary + one random CONFIRMED block
- [ ] Deliverable hygiene: no competing drafts at <WORKDIR> top level
- [ ] Redaction sweep clean on both files

## Secrets Analysis (`secrets-analysis`)

**Finished artifact:** - Finished artifact: `<WORKDIR>/secrets_candidates.json` — JSON array of `{file, line, type: "regex"|"entropy", pattern_name, value_redacted, verdict, reason}`. - Handoff: `report_output` consumes this next. It gets a RE

- [ ] `<WORKDIR>/inventory_final.json` read; scan order prioritized (app code before vendor libs)
- [ ] `02_js_analyze/bin/secrets_scan.py` present and executable
- [ ] Baseline scan of a known-clean vendor bundle run; noise level recorded
- [ ] ENGINE 1 (regex) run across `<WORKDIR>/normalized/`; hits have ±3-line context pulled
- [ ] ENGINE 2 (entropy) run; dictionary words, common tokens, and known-lib hashes excluded
- [ ] Every finding labeled CANDIDATE / INCONCLUSIVE / NEGATIVE with a reason string
- [ ] `<WORKDIR>/secrets_candidates.json` written, `chmod 600`
- [ ] No secret live-tested; approval asks drafted for each CANDIDATE

## Waymore Historical Harvest (`waymore-tools`)

**Finished artifact:** - Finished artifact: `<WORKDIR>/waymore_out/` — `waymore_urls.txt`, `historical_js_urls.txt`, `old_urls.jsonl`, `old_endpoints.txt`, `old_params.txt`, `removed_endpoints.txt`, `check_only.txt` — plus downloaded archived 

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

---

## Phase Gate 2 — certify before Content Discovery starts

- [ ] Every skill above has zero unticked boxes (unticked = re-run the skill)
- [ ] Every finding carries a verdict: CONFIRMED / INCONCLUSIVE / NEGATIVE
- [ ] NEGATIVEs documented with what was tried (so nobody re-tests them)
- [ ] Gadgets: no source→sink trace = stays CANDIDATE (no exceptions)
- [ ] Secrets: all values redacted outside `secrets_work/`; nothing live-tested without approval
- [ ] Library CVEs: each has a reachability verdict (no reachable trigger = no finding)
- [ ] `report.md` + `curl_commands.sh` compiled; kill-pass done (below-bar items removed, not softened)
- [ ] Tool syntax: every tool invocation in this phase is written as the full explicit command (flags, inputs, output paths) — never a generic "probe with X"; the model must not infer tool syntax
- [ ] **Gate verdict:** PASS / FAIL — if FAIL, name the skill, re-run it, re-certify
