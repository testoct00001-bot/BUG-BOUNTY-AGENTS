# LEVI — START (master guide)

## What LEVI is

LEVI is the executable form of the "Skills Design" boards: a two-pipeline skill pack for
**JS Analyze** (Discover/Download → Analyze) and **Content Discovery** (Generic → Specific),
built for bug-bounty recon where the doctrine is: *skip time-pass public surface — hunt what
leaks, is sensitive, and is reachable unauthenticated.*

## The master pipeline

### Pipeline 1 — JS Analyze

**Phase 1: Discover / Download** — `01_js_discover_download/`

| # | Skill | Job | Finished artifact |
|---|-------|-----|-------------------|
| 1 | `spider_harvest` | Crawl the app; collect every `<script src>` + inline script | `js_inventory/manifest.json`, `raw/*.js` |
| 2 | `lazy_loaded_chunks` | Catch lazy-loaded/route-split chunks (webpack, Vite, Next) | `raw/chunks/*.js` + chunk manifest |
| 3 | `historical_js` | Pull historical bundles via Wayback / Waymore; diff old vs new | `historical/*.js`, `diff_old_new.md` |
| 4 | `sourcemap_harvest` | Probe `*.map` for every JS file; extract `sourcesContent` | `sourcemaps/*.map`, `sourcemap_sources/` |
| 5 | `anti_automation_fetch` | Escalation ladder when blocked: curl → interceptor → DevTools MCP → Puppeteer | `fetch_log.md` (per-rung results) |
| 6 | `store_normalize` | Content-hash dedupe, per-run versioning, un-obfuscate minified/obfuscated | `normalized/`, `inventory_final.json` |

Helper: `bin/js_spider.py` (spider + download + `.map` probe + manifest).

**Phase 2: Analyze** — `02_js_analyze/`

| # | Skill | Job | Finished artifact |
|---|-------|-----|-------------------|
| 1 | `dangerous_functions_gadgets` | Map sinks/sources → gadgets (eval, innerHTML, postMessage, location…) | `gadgets.json` (+ `bin/gadget_mapper.py`) |
| 2 | `params_routes` | Routes, admin paths, feature flags, interesting comments, vuln-prone params | `routes_params.md` |
| 3 | `api_analysis` | All API calls grouped by functionality; old API versions | `api_map.md` |
| 4 | `library_analysis` | Library + version ID; outdated/security check | `libraries.md` |
| 5 | `framework_tech` | Framework/build-tooling fingerprint → tech choices | `tech_choices.md` |
| 6 | `feature_map` | Features → attack surface per feature | `feature_map.md` |
| 7 | `secrets_analysis` | Known-regex vs high-entropy string scan | `secrets_candidates.json` (+ `bin/secrets_scan.py`) |
| 8 | `jsluice_jxscout_tools` | JSLuice / jxscout extraction workflow | `jsluice_out/` |
| 9 | `waymore_tools` | Waymore historical-URL workflow | `waymore_out/` |
| 10 | `chrome_devtools_tools` | DevTools workflow: Coverage, HAR, Sources search, Overrides | `devtools_notes.md` |
| 11 | `report_output` | Compile the MD report + curl commands | `report.md`, `curl_commands.sh` |

### Pipeline 2 — Content Discovery — `03_content_discovery/`

**Phase 1: Generic** first, **Phase 1: Specific** second. Input: JS files. Output: `custom_list`.

| # | Skill | Job | Finished artifact |
|---|-------|-----|-------------------|
| 1 | `generic_routes` | Admin panels — custom + server/framework defaults | `discovery/generic_routes.txt` (verified) |
| 2 | `generic_files` | Config files, backups, exposed artifacts | `discovery/generic_files.txt` (verified) |
| 3 | `app_specific_files` | Tech-derived paths (from `tech_choices.md`) | `discovery/app_specific.txt` (verified) |
| 4 | `bugbounty_report_intel` | Paths/routes/files mined from public writeups | `discovery/writeup_patterns.md` |
| 5 | `api_discovery` | Versioned APIs, swagger/openapi, GraphQL, method enum | `discovery/api_surface.md` |
| 6 | `ffuf_workflow` | ffuf runs: baseline calibration, filters, recursion | `discovery/ffuf_*.json` |
| 7 | `onelistforall_micro` | OneListForAll micro combined-wordlist runs | `discovery/olfa_*.txt` |
| 8 | `js_to_wordlist` | JS → tokens → `custom_list.txt` | `custom_list.txt` |
| 9 | `phases_generic_specific` | Orchestrates Generic → Specific with entry/exit gates | `discovery/phase_log.md` |

Helper: `bin/wordlist_builder.py` (JS → `custom_list.txt`).

## Harness loop (how to execute a target)

1. **Scope check.** Confirm the host/app is in scope. Create the work folder.
2. **Phase 1 — Discover/Download.** Run skills 1–6 in order. Each must leave its finished
   artifact on disk before the next starts. If a rung of the anti-automation ladder fails,
   log it in `fetch_log.md` and climb — never skip to fabrication.
3. **Review gate 1.** Inventory complete? Chunks caught? Historical diff done? Sourcemaps
   attempted for every file? If any answer is no, the phase is not done.
4. **Phase 2 — Analyze.** Run skills 1–11. Gadgets need a data-flow trace (source → sink)
   before they are more than CANDIDATE. Secrets stay CANDIDATE unless format + context both
   check out — and are never live-tested without explicit user approval.
5. **Review gate 2.** Every finding carries a verdict: CONFIRMED / INCONCLUSIVE / NEGATIVE.
   NEGATIVEs are documented so nobody re-tests them.
6. **Pipeline 2 — Generic, then Specific.** Calibrate the 404 baseline *per host* before any
   ffuf/OLFA run. A hit counts only if it diverges from baseline. Then derive app-specific
   paths from `tech_choices.md` and writeup intel.
7. **Compile.** `report_output` builds `report.md` + `curl_commands.sh`; `js_to_wordlist`
   builds `custom_list.txt`.
8. **Final review pass — the Review Skill.** Run `review_skill/SKILL.md` (`/REVIEW`):
   every checklist action must have a log file or output, all output non-zero bytes,
   output matching expected good format and size. Mechanical first:
   `python3 review_skill/bin/review_check.py --workdir <dir> --phase all`, then reviewer
   judgment on top. Re-read the evidence appendix. Kill anything that does not meet
   the bar — a short honest report beats a long padded one. The run is not complete
   until a re-review returns all-PASS.

## Anti-completion-bias system

- Every skill has a tick-the-box **completion checklist** — the executing agent ticks each
  step, no skipping, no "looks done".
- **"Done" = the finished artifact exists on disk** in the exact path the skill names.
  A summary in chat is not done.
- **Nudge prompts** (say these to yourself before declaring a phase complete):
  - "Keep going until you have tested every parameter, not just the first one that responded."
  - "Do not report done before the finished artifact exists on disk."
  - "If you stopped because it got boring, that is exactly where the bugs live — continue."
  - "One more pass: what did the historical JS have that the current bundle removed?"
  - Board master nudge (when the review skill finds missed steps or insufficient proof):
    "Your work was just reviewed by the review skill and it was found that you either
    missed a step of analysis, or didnt generate an artifact of sufficient proof. Look
    at the markdown based checklist and the output for each step, find what you missed,
    and comeplete that step." — full variant library in `nudge_prompts/prompts.md`,
    re-injection protocol in `nudge_prompts/SKILL.md` (diagnose → select variant →
    assemble the 5-part context bundle → verify).

## Completion ledgers (.MD Checklists) — `checklists/`

Every methodology in this pack has a checkbox ledger. They are the proof of work:

- `checklists/phase1_discover_download.md` — all 65 boxes from the 6 Phase 1 skills + Phase Gate 1
- `checklists/phase2_analyze.md` — all 133 boxes from the 11 Phase 2 skills + Phase Gate 2
- `checklists/pipeline2_content_discovery.md` — all 102 boxes from the 9 discovery skills + Pipeline Gate
- `checklists/RUN_LEDGER_template.md` — compact per-target master ledger (one row per skill)
- `checklists/README.md` — the ledger doctrine

**The iron rule:** no checkmark = the agent has NOT finished = the skill gets **re-run**
from Step 1. A phase gate answered FAIL blocks the next phase. Copy the ledgers per target
(`<target>_<date>.md`), tick boxes only when the step is verifiably done (artifact on
disk, evidence saved), and let the review agent's first act be counting unticked boxes.

## Example Good Output — `examples/`

Agents do well when they know a goal to measure against. `examples/` holds up to 10
instances of good output — one per key artifact type (`manifest.json`,
`chunk_manifest.json`, `diff_old_new.md`, `gadgets.json`, `api_map.md`,
`secrets_candidates.json`, `report.md`, `curl_commands.sh`, `custom_list.txt`,
`review_report.md`; index in `examples/README.md`). The review skill's format-and-size
check measures the run's artifacts against these; the nudge prompts point the failed
agent at the matching example. Not every task needs all 10 — pick the instances matching
the task. All example data is synthetic.

**The completed-run directory:** a finished run produces one directory per site —
`examples/out_app_target_com/` is the working instance, and `examples/README.md` carries
the canonical `## Output` tree (raw → beautified → ast → analysis → findings) plus how
LEVI's artifacts map into it. Match that structure exactly.

## Tool Runs — never count on the model to infer tool syntax

Binding rule for every skill in this pack: a tool invocation is written as the **full
explicit command** — every flag, every output path, every input — never as a generic
instruction. The model must not infer tool syntax.

GENERIC (forbidden): "Probe the subdomain list with httpx."
→ the model will run `httpx -l subs.txt` and lose everything that matters.

EXACT (required) — the same task, fully specified:

```bash
httpx -l out/$TARGET/subdomains.txt \
  -p http:80,8080,8000,8888,3000 -p https:443,8443,9443 \
  -sc -cl -title -td -server -ip -cdn -location -favicon \
  -fr -maxr 3 -fep \
  -rl 50 -t 25 -timeout 8 -retries 2 -random-agent \
  -j -o out/$TARGET/02-probe/httpx.jsonl \
  -sr -srd out/$TARGET/02-probe/responses/ \
  -stats -silent
```

Ports, fields captured, rate limits, JSONL output, response-body storage, output paths —
all in the command, nothing left to inference. Every skill's tool steps follow this
standard, and every phase gate certifies it (see the last box of each gate).

## No-false-positive doctrine

1. **Baseline discipline.** Every live probe is compared against a known-dead path on the
   same host. Wildcard DNS and SPA fallbacks (`200 index.html` for everything) are the
   classic traps — only HTTP answers that diverge from baseline count.
2. **CANDIDATE vs CONFIRMED.** Static analysis produces CANDIDATEs. CONFIRMED requires
   baseline + 2× reproduction + raw pairs saved.
3. **Blocked is documented, not bypassed by imagination.** Log the block, move to the next
   rung or the next skill.
4. **Secrets are handled, not "verified" by use.** Format + context → CANDIDATE. Redact in
   reports. Live-testing needs explicit user approval.

## Output contract

- `report.md` — summary, tech choices, endpoint tables, secrets table (redacted),
  gadget/vuln-function findings with verdicts, evidence appendix with raw pairs.
- `curl_commands.sh` — one reproducible curl per CONFIRMED item, with the baseline
  command beside it.
- `custom_list.txt` — JS-derived tokens: endpoints, params, route fragments, one per line,
  deduped, frequency-annotated.

## Folder map

```
~/workspace/levi/
  SKILL.md                    pack entry point
  START.md                    this file
  checklists/                 .MD checklists — ledgers of completion
    README.md                 the ledger doctrine + iron rule
    RUN_LEDGER_template.md    per-target master ledger (copy per target)
    phase1_discover_download.md   65 boxes, 6 skills + Phase Gate 1
    phase2_analyze.md             133 boxes, 11 skills + Phase Gate 2
    pipeline2_content_discovery.md 102 boxes, 9 skills + Pipeline Gate
  review_skill/               the Review Skill — /REVIEW for completion
    SKILL.md                    reviewer methodology (3 board rules + verdict table)
    bin/review_check.py         mechanical checker (exists? non-zero? format+size good?)
  nudge_prompts/              re-injection prompts for review-failed agents
    SKILL.md                    diagnose → select variant → 5-part context bundle → verify
    prompts.md                  the board's master nudge + 6 variants (missed-step, proof, zero-byte, tick, stall, gate)
  examples/                   Example Good Output — up to 10 goal instances to measure against
    README.md                   doctrine + index of the 10 examples
  01_js_discover_download/
    AGENT.md
    bin/js_spider.py
    spider_harvest/SKILL.md
    lazy_loaded_chunks/SKILL.md
    historical_js/SKILL.md
    sourcemap_harvest/SKILL.md
    anti_automation_fetch/SKILL.md
    store_normalize/SKILL.md
  02_js_analyze/
    AGENT.md
    bin/secrets_scan.py
    bin/gadget_mapper.py
    dangerous_functions_gadgets/SKILL.md
    params_routes/SKILL.md
    api_analysis/SKILL.md
    library_analysis/SKILL.md
    framework_tech/SKILL.md
    feature_map/SKILL.md
    secrets_analysis/SKILL.md
    jsluice_jxscout_tools/SKILL.md
    waymore_tools/SKILL.md
    chrome_devtools_tools/SKILL.md
    report_output/SKILL.md
  03_content_discovery/
    AGENT.md
    bin/wordlist_builder.py
    generic_routes/SKILL.md
    generic_files/SKILL.md
    app_specific_files/SKILL.md
    bugbounty_report_intel/SKILL.md
    api_discovery/SKILL.md
    ffuf_workflow/SKILL.md
    onelistforall_micro/SKILL.md
    js_to_wordlist/SKILL.md
    phases_generic_specific/SKILL.md
```
