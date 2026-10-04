# .MD Checklist — Pipeline 2 — Content Discovery

> Generic first, then Specific. Calibrated baselines, no invented hits.

> **Iron rule:** a box with no checkmark means the agent has NOT finished that step.
> Not finished means the skill gets **re-run** — not argued with, not summarized, re-run.
> Copy this file per target as `<target>_<date>.md` and tick boxes as you go.
**Skills in this phase:** 9 | **Total boxes:** 102

## API Discovery (`api-discovery`)

**Finished artifact:** Done = `discovery/api_surface.md` exists in the exact section format (roots/versions, specs, GraphQL, method matrix, well-known, leads) with every CONFIRMED item carrying status + size + marker, plus `discovery/api_surfa

- [ ] Per-root baselines calibrated (`/api/*` JSON-404 vs `/` HTML-404 distinguished)
- [ ] Version battery run on every API root from `api_map.md` + JS-observed roots
- [ ] Version-downgrade test executed on ≥3 known-good endpoints
- [ ] Spec-doc battery probed; every hit verified to parse as a spec (not a UI shell)
- [ ] Spec-extracted paths fed back as new candidates (documented count)
- [ ] GraphQL discovered (or documented absent after the full probe set); fingerprint
- [ ] Method matrix completed for every CONFIRMED endpoint; `Allow` headers captured
- [ ] `/.well-known/` sweep done; `openid-configuration`/`jwks.json` mapped as auth-leads
- [ ] Every CONFIRMED item reproduced 2×; raw pairs in `discovery/api_surface_raw.md`
- [ ] `discovery/api_surface.md` compiled in the exact section format
- [ ] Review: reviewer re-probes 2 spec hits (verifies JSON parses), 1 GraphQL

## App-Specific Files Discovery (`app-specific-files`)

**Finished artifact:** Done = `discovery/app_specific.txt` exists, one line per hit: `CONFIRMED <path> <status> <size_bytes> <framework> <marker>` — e.g. `CONFIRMED /actuator/env 200 48210 spring propertySources-present`. Or the single `NONE <

- [ ] `tech_choices.md` read; framework sections selected and documented (or skill
- [ ] Derivation table written in `discovery/app_specific_raw.md` BEFORE probing —
- [ ] Battery deduped against `generic_files.txt` (no double-probes; dedupes noted)
- [ ] Every probe compared against the extension-matched baseline
- [ ] Response-intelligence table applied to every result (no framework favoritism)
- [ ] Every CONFIRMED hit reproduced 2× with matching status + size + hash
- [ ] Raw pairs saved (secrets redacted; heapdumps truncated at 64KB verification)
- [ ] CONFIRMED manifests mined for follow-up routes/versions; follow-ups logged as
- [ ] NEGATIVE paths logged as one-liners
- [ ] `discovery/app_specific.txt` written in the exact finished-artifact format
- [ ] Review: reviewer reads the derivation table, strikes 3 rows at random, and the

## Bug Bounty Report Intel (`bugbounty-report-intel`)

**Finished artifact:** Done = `discovery/writeup_patterns.md` exists with ≥1 pattern sections in the exact format (or a documented `NO-PATTERNS <stack> <date>` block with the search trail proving the stack yielded nothing — an empty file is no

- [ ] `tech_choices.md` + `libraries.md` read; stack filter documented
- [ ] `discovery/writeup_search_log.md` started; every query + result count logged
- [ ] Minimum 10 stack-relevant writeups/reports read (fewer only if the stack is
- [ ] Every pattern has a one-sentence TRICK (no URL copy-pastes masquerading as patterns)
- [ ] Every pattern has an explicit target-stack translation (rule named, version/naming
- [ ] Untranslatable patterns logged as SKIPPED with reasons
- [ ] Full dedupe pass against all three verified lists + prior `tried` log
- [ ] `discovery/writeup_patterns.md` written in the exact section format, every
- [ ] No live probing performed inside this skill (ammunition only — the probing
- [ ] Review: reviewer picks 3 patterns, re-derives the TRICK from the source URL

## ffuf Workflow (`ffuf-workflow`)

**Finished artifact:** Done = `discovery/ffuf_<name>.json` (raw ffuf output) + `discovery/ffuf_<name>_runlog.md` (calibration block, wordlist provenance, filter justifications, rate notes, triage summary with counts: probed / candidates / conf

- [ ] Wordlist recorded: exact path, entry count, source (derived battery / SecLists / custom_list)
- [ ] 3-dead-path baseline calibrated in THIS run (timestamped in runlog)
- [ ] Canary run executed: 5 known-dead strings → 0 results after filters (or manual
- [ ] Every `-f*`/`-m*` flag justified in one runlog line each
- [ ] Directory pass → file-extension pass on CONFIRMED dirs → seeded pass, in order
- [ ] Baseline re-checked between passes (one dead path; moved = recalibrated)
- [ ] EVERY ffuf result manually triaged with curl vs baseline (no JSON-to-finding pipeline)
- [ ] SPA-costume / WAF-block / size-jitter kills documented as NEGATIVE with reasons
- [ ] Survivors understood, reproduced 2×, raw pairs saved, promoted to `discovery/*.txt`
- [ ] Rate behavior documented (`-t`/`-rate` values + why; any 429 backoff noted)
- [ ] `discovery/ffuf_<name>.json` + `discovery/ffuf_<name>_runlog.md` on disk
- [ ] Review: reviewer replays the calibration block, re-runs the canary, and

## Generic Files Discovery (`generic-files`)

**Finished artifact:** Done = `discovery/generic_files.txt` exists, one line per file: `CONFIRMED <path> <status> <size_bytes> <content_type> <marker>` — marker examples: `KEY=VALUE-lines`, `ref:-refs/heads/`, `PK-magic`, `composer-json`. Or t

- [ ] `discovery/baseline.txt` has BOTH extensionless and extension-matched baselines
- [ ] Full battery probed (env, VCS, backups, manifests, OS artifacts, debug) + JS-derived filename variants, each with a documented source
- [ ] Every probe compared against the extension-matched baseline, not a single global one
- [ ] Every CANDIDATE verified through the 5 content checks (markers, content-type, baseline diff, magic bytes, secret handling)
- [ ] Response-intelligence table applied to every result — no verdict without a table row
- [ ] Every CONFIRMED file reproduced 2× with matching status + size + hash
- [ ] Raw pairs saved in `discovery/generic_files_raw.md` (secrets redacted)
- [ ] NEGATIVE paths logged as one-liners; `robots.txt`/`sitemap.xml` logged as INFO
- [ ] No live credential was tested — exposure verified, secrets redacted, escalated per program rules
- [ ] `discovery/generic_files.txt` written in the exact finished-artifact format
- [ ] Review: reviewer re-runs baseline, spot-checks 3 CONFIRMED files with curl,

## Generic Routes Discovery (`generic-routes`)

**Finished artifact:** Done = `discovery/generic_routes.txt` exists, every line matches `CONFIRMED <path> <status> <size_bytes> <title_or_marker>` — or the single line `NONE <host> <date> baseline=<status>/<size>` when zero routes confirmed (a

- [ ] `discovery/baseline.txt` exists with status/size/words/sha1 of 3 dead paths
- [ ] Baseline shape classified (classic 404 / SPA-fallback / WAF-block) and recorded
- [ ] Framework-default battery chosen from `tech_choices.md` (or generic set, with the reason documented)
- [ ] Every JS-derived custom guess traces to a source token in `routes_params.md`
- [ ] Every candidate probed with plain GET, ~1s spacing, no exotic headers
- [ ] Every CANDIDATE judged by baseline divergence, not status alone
- [ ] Every CANDIDATE understood (title/marker/JSON keys noted; SPA-costume trap checked)
- [ ] Every CONFIRMED route reproduced 2× with matching status + size + hash
- [ ] Raw request/response pairs saved in `discovery/generic_routes_raw.md`
- [ ] NEGATIVE paths logged so they are never re-probed
- [ ] `discovery/generic_routes.txt` written in the exact finished-artifact format
- [ ] Review: re-run the baseline command, spot-check 3 CONFIRMED routes with plain

## JS to Wordlist (`js-to-wordlist`)

**Finished artifact:** Done = `custom_list.txt` exists at the work root: one lowercase token per line, no comments, no blanks, deduped, priority-ordered, ≤50k entries; plus `discovery/custom_list_freq.md` (top-200 frequencies) and `discovery/w

- [ ] Corpus inventoried: file count + total bytes logged (normalized/ preferred, fallback noted)
- [ ] All 4 token sources extracted (endpoints, params, route fragments, bare tokens)
- [ ] All 6 splitting rules applied (camelCase, snake_case, kebab, path-split, digits, case)
- [ ] Framework noise stripped via `NOISE_WORDS` (extensions logged)
- [ ] Mutations limited to the 4 allowed families; every family's output count in the build log
- [ ] Forbidden mutations absent (spot-check: no leet-speak, no blind affix storms)
- [ ] Deduped; `custom_list.txt` has zero comment/blank lines (ffuf-ready)
- [ ] `discovery/custom_list_freq.md` holds the top-200 frequency annotations
- [ ] Priority ordering applied (API paths → routes → params → splits → mutations)
- [ ] 50k cap enforced with cut-logging (or documented under-cap)
- [ ] Rebuilds merge, never overwrite; each rebuild dated in the build log
- [ ] `bin/wordlist_builder.py` compiles clean (`python3 -m py_compile`)
- [ ] Review: reviewer reads the build log, checks the top-20 tokens trace to real

## OneListForAll Micro (`onelistforall-micro`)

**Finished artifact:** Done = `discovery/olfa_<name>.txt` (merged wordlist), `discovery/olfa_<name>.json` (results), `discovery/olfa_<name>_runlog.md` (provenance, calibration citation, filter justifications, triage summary with counts) on dis

- [ ] Wordlist provenance recorded: micro line count + date, tech short list (or
- [ ] Merged wordlist saved as `discovery/olfa_<name>.txt` (the exact fuzzed input)
- [ ] Calibration carried over from the ffuf runlog (source runlog named) OR fresh
- [ ] Baseline re-checked immediately before the run (one dead path; moved = recalibrated)
- [ ] Filter flags copied from calibration, each justified in the runlog
- [ ] Candidates sorted by size divergence; batch-kill rules documented with counts
- [ ] EVERY survivor manually curled vs baseline — no JSON-to-finding pipeline
- [ ] Survivors reproduced 2×, raw pairs saved, promoted to `discovery/*.txt`
- [ ] Rate behavior documented; any 429 backoff followed the same de-escalation as ffuf-workflow
- [ ] `discovery/olfa_<name>.json` + `discovery/olfa_<name>_runlog.md` on disk
- [ ] Review: reviewer inspects the merged list composition, replays the calibration

## Phases: Generic → Specific (`phases-generic-specific`)

**Finished artifact:** Done = `discovery/phase_log.md` exists and is complete per the Step 6 structure, both gate verdicts recorded, final inventory written, and every artifact it names exists at its exact path. The `discovery/` inventory at c

- [ ] Entry gate: all Pipeline 1 artifacts verified present; scope confirmed; phase log initialized
- [ ] Generic skills ran in order; each finished artifact on disk before the next started
- [ ] Baseline born in Generic, reused everywhere (no duplicate calibrations without cause)
- [ ] Generic exit gate certified PASS with all 6 checks (or FAIL documented + fixed + re-certified)
- [ ] Specific readiness verified (stack conclusive or Specific correctly DEFERRED)
- [ ] Specific skills ran in order; derivation cited per battery; pattern statuses updated
- [ ] `js-to-wordlist` rebuilt at the end with `--confirmed` (compounding)
- [ ] `discovery/phase_log.md` complete: every skill with timestamps, artifacts, counts
- [ ] Final inventory section written with artifact paths + line counts + total CONFIRMED
- [ ] Blocks & anomalies section written (or explicitly "none")
- [ ] Review: reviewer reads `phase_log.md` end-to-end, replays both gate checks

---

## Pipeline Gate — certify before the final report ships

- [ ] 404 baseline calibrated PER HOST before any fuzzing; calibration logged with the dead path used
- [ ] Generic phase exit certified (all 6 checks in `phases_generic_specific`, or FAIL documented + fixed + re-certified)
- [ ] Every Specific battery cites its derivation (`tech_choices.md` row or writeup pattern ID)
- [ ] Every discovered hit diverged from baseline AND was manually curled (no JSON-to-finding pipeline)
- [ ] CONFIRMED hits reproduced 2x with raw pairs saved
- [ ] `custom_list.txt` rebuilt at the end with `--confirmed` (compounding)
- [ ] `discovery/phase_log.md` complete: timestamps, artifacts, counts, blocks/anomalies section
- [ ] Tool syntax: every tool invocation in this phase is written as the full explicit command (flags, inputs, output paths) — never a generic "probe with X"; the model must not infer tool syntax
- [ ] **Gate verdict:** PASS / FAIL — if FAIL, name the skill, re-run it, re-certify
