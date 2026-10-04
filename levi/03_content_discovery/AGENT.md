# AGENT.md — 03_content_discovery (Pipeline 2: Content Discovery)

## Purpose

Turn analyzed JS into discovered live surface. Pipeline 1 (JS Analyze) produced
intelligence — routes, params, API maps, tech fingerprints, a custom wordlist.
This pipeline converts that intelligence into a verified inventory of what is
actually reachable and exposed on the target, unauthenticated: admin routes,
exposed files, API versions, spec docs, GraphQL endpoints, method anomalies.
Every item in `discovery/*.txt` earned its place through baseline divergence and
reproduction. Nothing here is a guess.

## Ordering: Generic → Specific (and why)

**Generic first** (generic-routes, generic-files, first wordlist build, calibrated
ffuf directory pass): stack-agnostic, baseline-calibrated. It finds what the tech
stack doesn't matter for — `/.env`, `/admin`, backup files — and, critically, it
**births the baseline** (`discovery/baseline.txt`) that every later skill reuses.
Running Specific first would mean calibrating blind and re-probing Generic's
negatives at 10× the request cost.

**Specific second** (bugbounty-report-intel, app-specific-files, api-discovery,
onelistforall-micro, recursion/extension ffuf, wordlist rebuild): tech-derived,
pattern-driven, API-mapped. It spends the stack knowledge where it pays —
framework batteries from `tech_choices.md`, writeup TRICKs translated to this
stack, version-downgrade tests on real API roots. The exit gate between them is
certified by `phases-generic-specific`, not assumed.

## Division of labor

**Consumes** (from Pipeline 1 + harness):
- `02_js_analyze/report.md` — the compiled analysis report (context)
- `02_js_analyze/api_map.md` — API calls grouped by functionality + old versions
- `02_js_analyze/routes_params.md` — routes, admin hints, params, feature flags
- `02_js_analyze/tech_choices.md` — framework fingerprint (Specific's blueprint)
- Analyzed JS corpus: `normalized/` (preferred) or `raw/*.js` + `raw/chunks/*.js`
- `<TARGET>` scope confirmation from the harness

**Produces** (all under `discovery/`, plus work root):
- `discovery/baseline.txt` — per-host 404 baseline (extensionless + extension-matched)
- `discovery/generic_routes.txt` / `generic_routes_raw.md`
- `discovery/generic_files.txt` / `generic_files_raw.md`
- `discovery/app_specific.txt` / `app_specific_raw.md`
- `discovery/writeup_patterns.md` / `writeup_search_log.md`
- `discovery/api_surface.md` / `api_surface_raw.md`
- `discovery/ffuf_*.json` / `discovery/ffuf_*_runlog.md`
- `discovery/olfa_*.txt` / `discovery/olfa_*.json` / `discovery/olfa_*_runlog.md`
- `custom_list.txt` (work root) / `discovery/custom_list_freq.md` / `discovery/wordlist_build_log.md`
- `discovery/phase_log.md` — the operation's ledger (entry/exit gates, per-skill counts)
- `discovery/block_note.md` — only if the host walled the run

**Helpers**: `bin/wordlist_builder.py` (JS corpus → `custom_list.txt`; stdlib only).

## Skill execution order

1. `phases-generic-specific` — Step 1: verify entry gate, init `phase_log.md`
2. `generic-routes` → routes + baseline
3. `generic-files` → files + extension baselines
4. `js-to-wordlist` → first `custom_list.txt` build
5. `ffuf-workflow` → calibrated directory pass (calibration record born here)
6. `phases-generic-specific` — Steps 3–4: certify Generic exit gate + Specific readiness
7. `bugbounty-report-intel` → pattern playbook
8. `app-specific-files` → tech-derived battery
9. `api-discovery` → API surface map
10. `onelistforall-micro` → merged breadth run (inherits ffuf calibration)
11. `ffuf-workflow` → recursion + extension passes on CONFIRMED dirs
12. `js-to-wordlist` → rebuild with `--confirmed` (compounding)
13. `phases-generic-specific` — Steps 6–10: close phase log, final inventory, handoff

One skill's finished artifact must exist on disk before the next starts. A skill
reporting BLOCKED is logged in `phase_log.md`; the pipeline continues — one walled
skill never cancels the operation.

## Non-negotiable rules (all skills)

- **Baseline first.** No probing skill runs without a calibrated per-host baseline.
  A hit = baseline divergence, never status code alone.
- **CANDIDATE vs CONFIRMED.** Probing output is CANDIDATE until: baseline divergence
  + content understood + 2× reproduction + raw pair saved.
- **Negative logs are artifacts.** Every dead path is logged so no skill re-probes it.
- **No cross-skill re-probing.** Batteries dedupe against all `discovery/*.txt` first.
- **Secrets are handled, not tested.** Exposure verified, values redacted, escalated
  per program rules. Live-testing credentials needs explicit user approval.
- **Rate discipline.** Default 20 threads / 20 req/s; back off at the first 429;
  stop and go manual on the second wave. Getting the program's range banned is a
  failed operation.
- **Blocked is documented.** `discovery/block_note.md` with observed behavior —
  never silently skipped, never bypassed by imagination.

## Review checklist (pipeline-level)

- [ ] `discovery/phase_log.md` complete: entry gate, both gate verdicts with check
      trails, every skill with timestamps/artifacts/counts, final inventory, blocks section
- [ ] `discovery/baseline.txt` present with extensionless + extension-matched records
- [ ] Every `discovery/*.txt` in its exact line format (or a documented `NONE` line —
      empty files don't certify)
- [ ] Spot-check: 2 CONFIRMED items per file re-probed with plain curl vs baseline —
      any match = the file's verdicts are void, re-triage
- [ ] No `discovery/*.txt` contains a path that another file already covered
      (dedupe held across skills)
- [ ] `custom_list.txt`: one token per line, no comments/blanks, ≤50k, build log
      shows the final `--confirmed` rebuild
- [ ] `writeup_patterns.md`: every pattern has a status; no UNTRIED pattern that a
      probing skill should have fired
- [ ] Raw pairs exist for every CONFIRMED item claimed in the final inventory
- [ ] Counts reconcile: phase log totals == sum of file line counts
- [ ] Handoff ready: `report_output` (Pipeline 1) can compile `report.md` from this
      inventory without re-verifying anything; lead queue (version-downgrade hits,
      introspection-on GraphQL, unadvertised write methods) listed in `api_surface.md`
