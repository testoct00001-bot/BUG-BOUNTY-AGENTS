---
name: report-output
description: >
  Compiles every phase-2 artifact into the two final deliverables — report.md and curl_commands.sh — with an honest evidence appendix, a redacted secrets table, and nothing below the bar. USE THIS SKILL whenever the user wants to compile the report, generate re-verification curl commands, or finalize findings for handoff to the next phase. Trigger on: "compile the report", "generate curl commands", "finalize findings". This skill produces the battle-tested field report — the deep-hunt-loop agents fire it.
---

# Report & Curl Output

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn a pile of phase-2 artifacts into two files a hunter can actually use: a report that tells the truth about what was found and what was ruled out, and a curl kit that re-verifies every CONFIRMED item from a cold start. A short honest report beats a long padded one — your final act is to kill anything that does not meet the bar.

## Step 1 – Gather inputs

- `<TARGET>`: the target host/URL. `<WORKDIR>`: the target work folder.
- Every phase-2 artifact on disk — check each exists before you start, and note which are missing (a missing artifact is a gap in the report, never an excuse to invent its content):
  - `inventory_final.json` (N files / M KB normalized — the scope line)
  - `tech_choices.md` (framework_tech output)
  - `api_map.md` (api_analysis output, merged with runtime list from devtools_notes.md)
  - `feature_map.md` (feature_map output)
  - gadget findings (dangerous_functions_gadgets: sink, source trace, verdict per gadget)
  - secrets findings (secrets_analysis: file | line | pattern — values stay REDACTED)
  - library findings (library_analysis: outdated libs + CVEs + reachability verdicts)
  - `devtools_notes.md` (chrome_devtools_tools: coverage, HAR runtime list, overrides log)
  - raw request/response pairs for every CONFIRMED item (saved under `<WORKDIR>/raw/`)
- The verdict ledger: every item must already carry CONFIRMED / INCONCLUSIVE / NEGATIVE / CANDIDATE / BLOCKED. If an item has no verdict, it is CANDIDATE by default and gets no curl block.
- The known-dead baseline path on `<TARGET>` (status + body size recorded) — every curl block compares against it.

## Step 2 – Build report.md section by section

1. **Header + scope.** `# Target report — <TARGET>`, then one line: date (YYYY-MM-DD), scope (host + what was in scope), inventory size (`N` files / `M` KB normalized, copied from inventory_final.json — recompute, do not guess). If inventory size is unknown, write "unknown" rather than a number.
2. **## Summary — 3 to 6 bullets, no more.** Bullet 1: what the app IS (one line, from tech_choices.md). Bullets 2-4: headline findings, CONFIRMED items only, each one line with impact. Final bullet: what was ruled out (the strongest negative result — e.g. "all 14 gadget sinks either dead-code or server-side validated; no client-side-only filter found"). Never put a CANDIDATE in the Summary.
3. **## Tech choices.** Condensed from tech_choices.md: framework, bundler, auth model observed, hosting/CDN, notable client-side libraries. Five lines maximum — this section orients the reader, it does not re-teach the stack.
4. **## Endpoints.** Tables from api_map.md grouped by functionality (auth, user/profile, admin, internal/debug, telemetry), columns: `endpoint | method | auth observed | verdict`. Auth observed must say what you SAW (cookie sent, no auth header, 401 without token) — never what you assume. Every runtime-confirmed endpoint (from the HAR delta) is marked `runtime-confirmed`; static-only endpoints are marked `static-only`.
5. **## Routes & params.** Admin paths, feature flags (from devtools_notes.md Application panel), and vuln-prone params with suspected class — one line each: `param | where seen | suspected class | verdict`. A param with no verdict is listed as CANDIDATE, never implied as vulnerable.
6. **## Gadget findings.** One block per gadget: sink (function + file:line), source trace (the 3-5 line chain from input to sink), a 10-line context snippet, verdict in bold. CANDIDATEs are clearly marked "CANDIDATE — unverified" and the block states exactly what verification would require. INCONCLUSIVE blocks state what blocked the verdict. No gadget appears without a verdict.
   Evidence appendix entry format (repeat per CONFIRMED item — keep it tight, excerpt bodies to the relevant 20 lines):
   ```
   ### E1 — <finding short name> — CONFIRMED
   Baseline: GET /this-path-definitely-does-not-exist-9f3k2 → 200, 48210 bytes (SPA fallback)
   Probe 1 (2026-10-04 14:02 IST): GET /api/v1/admin/users → 200, 3120 bytes, JSON array of 41 users
   Probe 2 (2026-10-04 14:19 IST): identical result (raw pair: raw/E1_probe2.txt)
   ```
7. **## Secrets, ## Libraries, ## Feature leads, ## Evidence appendix, ## Blocked.** Secrets: REDACTED table ONLY — `file | line | pattern_name | value_redacted | verdict`; full values NEVER appear in report.md, and the pattern_name must be generic (e.g. `aws-access-key`, not the key). Example row: `config.bundle.js | 1182 | stripe-publishable-key | pk_live_REDACTED | NEGATIVE (publishable, expected client-side)`. Libraries: one line per outdated lib — `lib@version | CVE | reachable from user input? (yes/no/unknown) | verdict`; a CVE on an unreachable lib is a note, not a finding. Feature leads: ranked lead table copied from feature_map.md, highest first. Evidence appendix: raw request/response pairs for every CONFIRMED item (request line + headers minus secrets, status, body excerpt), the baseline command, and the 2x reproduction notes with timestamps. Blocked: every BLOCKED item with its reason (anti-automation wall, auth wall, rate limit) — blocked is documented, never silently dropped.

## Step 3 – Generate curl_commands.sh

8. Start the file with the EXACT template header:
   ```bash
   #!/usr/bin/env bash
   # Re-verification kit for <TARGET> — generated YYYY-MM-DD.
   # Each block: BASELINE (known-dead path) then PROBE (the finding).
   # Usage: bash curl_commands.sh  (or run blocks individually)
   set -euo pipefail
   ```
9. One block per CONFIRMED item, in this exact shape — comment naming the finding + verdict, then the BASELINE curl, then the PROBE curl:
   ```bash
   # FINDING: <short name> — verdict: CONFIRMED
   # BASELINE: known-dead path on the same host
   curl -sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n' \
     "https://<TARGET>/this-path-definitely-does-not-exist-9f3k2"
   # PROBE: <what this request demonstrates>
   curl -sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n' \
     -H 'Accept: application/json' \
     "https://<TARGET>/<probed-path>?<param>=<canary>"
   ```
10. Curl flags are fixed: `-sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n'`. `-D -` dumps response headers to stdout (that is where Set-Cookie, CORS, and cache headers live — do not drop it). `-o /dev/null` discards the body; when the body IS the evidence, use `-o <WORKDIR>/raw/<finding>_body.txt` instead and say so in the comment. Verify any other flag with `curl --help` before using it — never invent flags.
11. `<TARGET>` placeholders stay literal in the committed file (the kit must work for whoever picks it up against any deployment of the same target). NEVER embed real secret values: use `$SECRET_FROM_VAULT` or the placeholder `<REDACTED — insert at runtime>`. If a probe needs an auth token to reproduce, the comment says so explicitly and the header line reads `-H "Authorization: Bearer $TOKEN"`.
12. CANDIDATE-only items get NO curl block — or, if the hunter explicitly wants the probe preserved, a block whose first comment line reads `# UNVERIFIED CANDIDATE — do not cite as a finding` followed by the probe. After writing, run `chmod +x <WORKDIR>/curl_commands.sh` and syntax-check with `bash -n`.

## Step 4 – Final review: the kill pass

13. Re-read the Evidence appendix top to bottom and KILL anything that does not meet the bar: no baseline comparison → cut or demote to CANDIDATE; single reproduction → demote to INCONCLUSIVE with a note; verdict resting on "looks vulnerable" with no executed path → cut. The report gets shorter and more honest — that is the job.
14. Cross-check every CONFIRMED item has all three: a gadget/endpoints section entry, an evidence-appendix raw pair, and a curl block. Any CONFIRMED item missing one of the three is demoted until the missing piece exists. No exceptions, no "I'll add it later".
15. Redaction sweep: grep report.md and curl_commands.sh for anything matching secret patterns (tokens, keys, `Authorization:`, `Cookie:` values, emails beyond the hunter's own). The secrets table shows `value_redacted` and nothing else; the HAR-derived evidence uses the `.redacted` HAR copy. One leaked value fails the whole review — fix and re-sweep.
16. Read the Summary once more and ask: would a hunter picking this up cold know exactly what to test next and what to skip? If a bullet could mean two things, rewrite it. If the Blocked section would surprise the next phase, it is incomplete. Then write both files to disk — report.md first, curl_commands.sh second, chmod +x, bash -n.
17. Fresh-eyes rule: after the kill pass, step away (or hand the draft to another agent) and re-read the Summary plus one random CONFIRMED block cold, asking "would I bet a bounty submission on this evidence?" Anything that makes you hesitate gets one more verification run or one more demotion — hesitation is data.
18. Deliverable hygiene: `<WORKDIR>/report.md` and `<WORKDIR>/curl_commands.sh` are the only top-level deliverables. Move superseded drafts, scratch notes, and half-built tables into `<WORKDIR>/raw/` or delete them — a work folder with three competing "final" reports is how the next agent cites the wrong one.

## Step 5 – Exact commands

```bash
# BASELINE — record the known-dead path signature every curl block compares against.
curl -sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n' \
  "https://<TARGET>/this-path-definitely-does-not-exist-9f3k2"

# PROBE — inventory size for the report header (recompute, never guess).
python3 -c "
import json,os
inv=json.load(open('<WORKDIR>/inventory_final.json'))
files=inv.get('files',[])
kb=sum(os.path.getsize(f) for f in files if os.path.exists(f))//1024
print(f'{len(files)} files / {kb} KB normalized')"

# VERIFY — every CONFIRMED item has evidence + curl block; redaction sweep.
grep -c '^# FINDING' <WORKDIR>/curl_commands.sh
grep -nE 'Authorization:|Cookie: [^$]|sk-live|AKIA|xox[bap]-' <WORKDIR>/report.md <WORKDIR>/curl_commands.sh \
  && echo 'REDACTION FAILURE — fix before shipping' || echo 'redaction sweep clean'
bash -n <WORKDIR>/curl_commands.sh && echo 'curl_commands.sh syntax OK'
chmod +x <WORKDIR>/curl_commands.sh && ls -la <WORKDIR>/report.md <WORKDIR>/curl_commands.sh
```

## Step 6 – Completion checklist

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

### Review

A reviewer must verify: (a) the Summary contains zero CANDIDATEs; (b) every CONFIRMED item appears in all three places — body section, evidence appendix, curl block; (c) the secrets table contains no value longer than `value_redacted` placeholders; (d) `bash -n` passes and the file is executable; (e) the Blocked section explains every gap a downstream agent might trip over.

*Which finding survived the kill pass that you most wanted to keep — and what evidence saved it?*
*What did you demote, and would you defend that demotion to the hunter?*
*If the next agent runs only curl_commands.sh cold, what breaks first?*

Done = `<WORKDIR>/report.md` and `<WORKDIR>/curl_commands.sh` (executable, `bash -n` clean) exist on disk at their exact paths, redaction sweep clean, kill pass documented.

## Step 7 – Evidence standard (no false positives)

- Every CONFIRMED item in report.md is backed by: a baseline comparison against the known-dead path on the same host, 2x independent reproduction with timestamps, and the raw request/response pair saved under `<WORKDIR>/raw/`. Missing any one → demote, no exceptions.
- Static findings are CANDIDATE until verified: a gadget, endpoint, or secret that was never executed or probed live is marked CANDIDATE with the exact verification step written out — never upgraded on prose.
- Verdicts use exactly CONFIRMED / INCONCLUSIVE / NEGATIVE / CANDIDATE / BLOCKED. "Likely", "probably", "seems" do not appear in verdict positions.
- Blocked = BLOCKED documented with the reason (anti-automation wall, auth wall, rate limit) — never fabricated around, never silently dropped.
- Secrets are never live-tested without explicit user approval: a candidate secret is reported REDACTED with its pattern and location; you do not curl it, decode it, or use it to authenticate. Secret values are redacted in every report, log, and curl block.

## Step 8 – Finished artifact & handoff

Finished artifacts:
- `<WORKDIR>/report.md` — the full report in the exact section template above.
- `<WORKDIR>/curl_commands.sh` — executable re-verification kit: `#!/usr/bin/env bash` + `set -euo pipefail`, one BASELINE+PROBE block per CONFIRMED item, fixed flags `-sS -D - -o /dev/null -w 'HTTP %{http_code} size %{size_download}\n'`, `<TARGET>` placeholders, zero real secret values.

Handoff:
- **deep-hunt-loop / THINKER agents** consume `report.md`: the Summary tells them what is already proven, the Endpoints and Gadget sections tell them where to dig deeper, and the Blocked section tells them what walls to plan around. CANDIDATE items are their starting leads — each carries its required verification step.
- **Pipeline 2 (03_content_discovery)** consumes `report.md`'s Endpoints and Routes & params sections as seed input for content discovery — runtime-confirmed endpoints first.
- `curl_commands.sh` is the standalone re-verification kit: any agent re-runs it cold to confirm the findings still hold before citing them.

---
