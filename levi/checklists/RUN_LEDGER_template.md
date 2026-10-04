# RUN LEDGER — <TARGET> — <YYYY-MM-DD>

> Copy this template per target. One row per skill. A row is ticked only when the skill's
> phase-file boxes are ALL ticked and its finished artifact exists on disk.
> **No checkmark = not finished = re-run the skill.**

## Run info

- **Target:**
- **Scope note:**
- **Started:**
- **Operator (agent):**

## Phase 1 — Discover / Download (`checklists/<target>_phase1.md`)

| Done | Skill | Finished artifact on disk | Verdict / notes |
|------|-------|---------------------------|-----------------|
| [ ] | spider_harvest | `js_inventory/manifest.json`, `raw/*.js` | |
| [ ] | lazy_loaded_chunks | `raw/chunks/*.js`, `chunk_manifest.json` | |
| [ ] | historical_js | `historical/*.js`, `diff_old_new.md` | |
| [ ] | sourcemap_harvest | `sourcemaps/*.map`, `sourcemap_sources/` | |
| [ ] | anti_automation_fetch | `fetch_log.md` (per-rung results) | |
| [ ] | store_normalize | `normalized/`, `inventory_final.json` | |

**Phase Gate 1:** [ ] PASS / [ ] FAIL — notes:

## Phase 2 — Analyze (`checklists/<target>_phase2.md`)

| Done | Skill | Finished artifact on disk | CONFIRMED / INCONCLUSIVE / NEGATIVE |
|------|-------|---------------------------|-------------------------------------|
| [ ] | jsluice_jxscout_tools | `jsluice_out/` | |
| [ ] | waymore_tools | `waymore_out/` | |
| [ ] | chrome_devtools_tools | `devtools_notes.md` | |
| [ ] | dangerous_functions_gadgets | `gadgets.json` | |
| [ ] | params_routes | `routes_params.md` | |
| [ ] | api_analysis | `api_map.md` | |
| [ ] | library_analysis | `libraries.md` | |
| [ ] | framework_tech | `tech_choices.md` | |
| [ ] | feature_map | `feature_map.md` | |
| [ ] | secrets_analysis | `secrets_candidates.json` (redacted outside `secrets_work/`) | |
| [ ] | report_output | `report.md`, `curl_commands.sh` | |

**Phase Gate 2:** [ ] PASS / [ ] FAIL — notes:

## Pipeline 2 — Content Discovery (`checklists/<target>_discovery.md`)

| Done | Skill | Finished artifact on disk | Hits CONFIRMED |
|------|-------|---------------------------|----------------|
| [ ] | generic_routes | `discovery/generic_routes.txt` | |
| [ ] | generic_files | `discovery/generic_files.txt` | |
| [ ] | app_specific_files | `discovery/app_specific.txt` | |
| [ ] | bugbounty_report_intel | `discovery/writeup_patterns.md` | |
| [ ] | api_discovery | `discovery/api_surface.md` | |
| [ ] | ffuf_workflow | `discovery/ffuf_*.json` + runlogs | |
| [ ] | onelistforall_micro | `discovery/olfa_*.txt` + runlogs | |
| [ ] | js_to_wordlist | `custom_list.txt` | |
| [ ] | phases_generic_specific | `discovery/phase_log.md` | |

**Pipeline Gate:** [ ] PASS / [ ] FAIL — notes:

## Final review

- **Total CONFIRMED findings:**
- **Kill-pass done (below-bar items removed, not softened):** [ ]
- **Evidence appendix complete (raw pairs for every CONFIRMED):** [ ]
- **Reviewer sign-off:**
- **Unticked boxes remaining:** <count> — each one is a re-run order, not a footnote
