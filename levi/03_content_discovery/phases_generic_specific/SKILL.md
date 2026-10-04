---
name: phases-generic-specific
description: >
  Orchestrates Pipeline 2 with strict entry/exit gates: verifies JS-analysis artifacts exist, runs Generic discovery first (routes, files, baseline calibration), certifies the exit gate (tech_choices.md + writeup intel ready), then runs Specific discovery (tech-derived, pattern-driven, API surface), and closes with a completion checklist and phase_log.md. USE THIS SKILL whenever the user wants to run the full content-discovery pipeline or certify phase gates. Trigger on: "run content discovery", "generic then specific", "phase gate check", "orchestrate discovery", "certify generic phase", "start specific phase". This skill produces the certified phase_log.md and the complete discovery/ inventory – the report_output skill (Pipeline 1) consumes the final inventory when compiling report.md.
---

# Phases: Generic → Specific

You are operating as the world's best bug bounty hunter and red teamer. Your job is to run Pipeline 2 as a disciplined operation, not a pile of fuzzing runs: Generic first (broad, stack-agnostic, baseline-calibrated), Specific second (tech-derived, pattern-driven, API-mapped) — with entry gates that stop you from starting unready and exit gates that stop you from advancing unproven. Order is strategy: Generic finds what the stack doesn't matter for; Specific spends the stack knowledge where it pays.

## Step 1 – Gather Inputs (Entry Gate: Pipeline 2 May Start)

Verify EVERY item before any discovery probe. A missing item = the gate is closed:
- [ ] Work folder exists with Pipeline 1 artifacts: `02_js_analyze/report.md`
      (or at minimum `routes_params.md` + `api_map.md` + `tech_choices.md`)
- [ ] Analyzed JS corpus present: `normalized/` (or `raw/*.js` with a noted fallback)
- [ ] `<TARGET>` host confirmed in scope (scope check is a harness step, not this skill's —
      but the gate re-verifies: no scope note, no run)
- [ ] `discovery/` directory created; `discovery/phase_log.md` initialized with:
      target, date, scope reference, operator, pipeline-1 artifact inventory

If `tech_choices.md` is missing/inconclusive at entry: the pipeline still runs —
Generic is stack-agnostic — but the Specific phase is marked `DEFERRED (no stack
signal)` in the phase log until the fingerprint exists. You do not get to run
"Specific" on vibes.

## Step 2 – Run Generic (Phase 1: Generic)

Execute in order. Each skill's finished artifact must exist on disk before the next starts:
1. **generic-routes** → `discovery/generic_routes.txt`, `generic_routes_raw.md`,
   `discovery/baseline.txt` (the baseline is born here — everything downstream reuses it)
2. **generic-files** → `discovery/generic_files.txt`, `generic_files_raw.md`
   (extension-matched baselines added)
3. **js-to-wordlist** (first build) → `custom_list.txt` (ammunition manufactured
   early so the Specific phase can fire it immediately)
4. **ffuf-workflow** (calibrated directory pass) → `discovery/ffuf_dirs.json` + runlog
   (calibration record that `onelistforall-micro` will inherit)

Generic-phase rules: no framework-specific batteries (that's Specific), no writeup
patterns yet (that's Specific), plain GETs before any method tricks. If a skill
reports BLOCKED, log it in `phase_log.md` and continue the phase — one walled
skill doesn't cancel the others.

## Step 3 – Certify the Generic Exit Gate

The gate to Specific opens only when ALL hold:
- [ ] `discovery/baseline.txt` exists with extensionless + extension-matched baselines
- [ ] `generic_routes.txt` + `generic_files.txt` exist (with `NONE` lines if empty —
      empty files don't certify)
- [ ] `custom_list.txt` built (entry count logged)
- [ ] ≥1 calibrated ffuf runlog on disk (calibration inheritable)
- [ ] Every CONFIRMED item has 2× reproduction + raw pair (spot-check 3 per file)
- [ ] Negative logs exist (the next phase must not re-probe Generic's dead paths)

Write the gate verdict into `phase_log.md`:
`GATE GENERIC→SPECIFIC: PASS <date> (6/6 checks)` or `FAIL <date> (missing: …)`.
A FAIL blocks Specific — fix the missing items, re-certify. Advancing on a failed
gate is how Specific re-discovers Generic's negatives at 10× the request cost.

## Step 4 – Verify Specific-Phase Readiness

Specific needs its own inputs certified:
- [ ] `tech_choices.md` conclusive (framework named with evidence) — else Specific
      stays DEFERRED; only `bugbounty-report-intel`'s stack-agnostic patterns may run
- [ ] `discovery/writeup_patterns.md` exists with ≥1 UNTRIED pattern (or documented
      `NO-PATTERNS` with search trail)
- [ ] `api_map.md` re-read for version roots (Specific's `api-discovery` needs them)
- [ ] Baseline freshness re-check: one dead path, must match `baseline.txt` —
      a stale baseline voids Specific's calibrations before they start

## Step 5 – Run Specific (Phase 1: Specific)

Execute in order:
1. **bugbounty-report-intel** → `discovery/writeup_patterns.md` (+ search log)
   (if not built during Generic — patterns are Specific's targeting data)
2. **app-specific-files** → `discovery/app_specific.txt` (tech-derived battery;
   derivation table reviewed BEFORE probing)
3. **api-discovery** → `discovery/api_surface.md` (versions, specs, GraphQL,
   method matrix, well-known)
4. **onelistforall-micro** → merged breadth run with carried-over calibration
5. **ffuf-workflow** (recursion + extension passes on CONFIRMED dirs)
6. **js-to-wordlist** (rebuild: fold CONFIRMED hits back in via `--confirmed`)

Specific-phase rules: every battery cites its derivation (tech_choices line,
pattern ID, or CONFIRMED hit); pattern statuses updated to TRIED/CONFIRMED/
NEGATIVE on return; recursion only into CONFIRMED directories. The phase log
records per-skill: started/finished timestamps, artifact paths, counts
(probed/candidates/confirmed/negative), blocks.

## Step 6 – Maintain phase_log.md (The Operation's Ledger)

`discovery/phase_log.md` is append-only. Sections:
```markdown
# Phase log — <target> — <date>
## Entry gate (checks + verdict)
## Generic phase
### generic-routes — started/finished, artifacts, counts, notes
### generic-files — ...
### js-to-wordlist (build 1) — ...
### ffuf-workflow (dirs) — ...
## Gate GENERIC→SPECIFIC — verdict + checks
## Specific readiness — verdict + checks
## Specific phase
### bugbounty-report-intel — ...
### app-specific-files — ...
### api-discovery — ...
### onelistforall-micro — ...
### ffuf-workflow (recursion/ext) — ...
### js-to-wordlist (rebuild) — ...
## Final inventory (artifact paths + line counts)
## Blocks & anomalies
```
Every entry dated. The log is what makes the pipeline auditable — a reviewer
reconstructs the entire operation from this file alone.

## Step 7 – Exact Commands (Copy-Paste)

```bash
# 0. Initialize
mkdir -p discovery
cat > discovery/phase_log.md <<'EOF'
# Phase log — TARGET — DATE
## Entry gate
EOF

# 1. Entry-gate check (all must exist)
for f in 02_js_analyze/routes_params.md 02_js_analyze/api_map.md 02_js_analyze/tech_choices.md; do
  [ -f "$f" ] && echo "OK $f" || echo "MISSING $f"
done
ls normalized/ 2>/dev/null | wc -l  # JS corpus file count (or raw/*.js fallback)

# 2. Generic exit-gate check (all must exist + be non-empty of meaning)
for f in discovery/baseline.txt discovery/generic_routes.txt discovery/generic_files.txt custom_list.txt; do
  [ -s "$f" ] && echo "OK $f ($(wc -l < "$f") lines)" || echo "FAIL $f"
done
ls discovery/ffuf_*_runlog.md 2>/dev/null || echo "FAIL no ffuf runlog"

# 3. Baseline freshness re-check before Specific
curl -sk -o /dev/null -w "freshness: %{http_code} %{size_download}\n" "$TARGET/levi-dead-$RANDOM"
# Compare against discovery/baseline.txt — must match, else recalibrate.

# 4. Final inventory
wc -l discovery/*.txt custom_list.txt 2>/dev/null
grep -h '^CONFIRMED' discovery/*.txt 2>/dev/null | wc -l  # total confirmed hits
```

## Step 8 – Completion Checklist

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
      independently, and spot-verifies 2 artifacts per phase exist at their exact
      paths with the logged line counts. Any mismatch = failed review.
- Nudge prompts:
  - "The Generic gate shows 5/6. Which check failed — and did you fix it or just proceed? Be honest."
  - "Specific is running but tech_choices.md was inconclusive. What exactly is 'Specific' about this run? Defer it properly."
  - "The phase log's last entry is from two skills ago. The log is append-as-you-go, not write-at-the-end. Catch up now."

## Step 9 – Evidence Standard (No False Positives)

- Gate verdicts are claims: a PASS requires the check commands' output pasted or
  referenced in the phase log — "gate passed" with no check trail is INCONCLUSIVE.
- This skill certifies process, not findings. Finding-level evidence bars belong
  to the probing skills; this skill's bar is: every certified artifact exists at
  its exact path with the logged content.
- A DEFERRED Specific phase is a valid terminal state (documented reason), not a
  failure — but it must say DEFERRED, not silently end after Generic.
- BLOCKED skills don't fail gates; undocumented blocks do.

## Step 10 – Finished Artifact & Handoff

Done = `discovery/phase_log.md` exists and is complete per the Step 6 structure,
both gate verdicts recorded, final inventory written, and every artifact it names
exists at its exact path. The `discovery/` inventory at close:
`baseline.txt`, `generic_routes.txt`, `generic_routes_raw.md`, `generic_files.txt`,
`generic_files_raw.md`, `app_specific.txt`, `app_specific_raw.md`,
`writeup_patterns.md`, `writeup_search_log.md`, `api_surface.md`,
`api_surface_raw.md`, `ffuf_*.json`, `ffuf_*_runlog.md`, `olfa_*.txt`,
`olfa_*.json`, `olfa_*_runlog.md`, `custom_list.txt`, `custom_list_freq.md`,
`wordlist_build_log.md`, `phase_log.md`.

Handoff: the **report_output** skill (Pipeline 1, Phase 2) consumes the final
`discovery/` inventory + `phase_log.md` when compiling `report.md` — every
CONFIRMED item arrives with its raw pair and reproduction record, so the report
inherits the evidence bar instead of re-verifying it. Version-downgrade hits,
introspection-on GraphQL, and unadvertised write methods go to the next track's
lead queue as the pipeline's highest-value output.
