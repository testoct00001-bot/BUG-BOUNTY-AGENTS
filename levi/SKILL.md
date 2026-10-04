---
name: levi
description: JS Analyze + Content Discovery skill pack (from the "Skills Design" boards — JS Analyze: Discover/Download all JS, then Analyze; Content Discovery: Generic → Specific). Covers spidering JS (inline, lazy-loaded, historical, sourcemaps), anti-automation fetch ladders, un-obfuscation, gadget/dangerous-function mapping, params/routes, API grouping, library CVE checks, framework fingerprinting, feature mapping, secrets (known-regex vs high-entropy), then ffuf / OneListForAll content discovery with JS-derived custom wordlists. Every skill ships with a no-false-positive evidence bar and a completion-bias checklist.
---

# LEVI — JS Analyze + Content Discovery skill pack

## Purpose

LEVI turns the "Skills Design" boards into an executable skill pack with two pipelines:

**Pipeline 1 — JS Analyze** (two phases):
1. **Discover / Download** — find and download *all* JS: inline and files (spider), lazy loaded, historical, sourcemaps — climbing an anti-automation ladder (webfetch → curl → interceptor → Chrome DevTools MCP → Puppeteer) when the target fights back. Then store and un-obfuscate (minified, obfuscated).
2. **Analyze** — map gadgets and dangerous functions; params and route analysis (admin, feature flags, interesting comments); API analysis (old versions, all calls grouped by functionality); library analysis (outdated, security); framework and tech analysis; feature map; secrets (known regex vs high-entropy strings). Tools: JSLuice / jxscout, Waymore, Chrome DevTools. Output: MD report + curl commands.

**Pipeline 2 — Content Discovery** (two phases: Generic → Specific):
- Generic content discovery of **routes** (admin panels — custom and server/framework defaults)
- Generic content discovery of **files** (config files, backups, exposed artifacts)
- App-specific discovery of files (derived from the tech stack)
- Paths, routes, and files mined from public bug-bounty reports
- APIs
- Tools: **ffuf**, **OneListForAll micro**. Input: JS files. Output: **custom_list**.

## Folder map

```
~/workspace/levi/
  SKILL.md                      ← this file (pack entry point)
  START.md                      ← master guide: harness loop, anti-completion-bias, output contract
  01_js_discover_download/      ← Pipeline 1, Phase 1 (6 skills + AGENT.md + bin/js_spider.py)
  02_js_analyze/                ← Pipeline 1, Phase 2 (11 skills + AGENT.md + bin/secrets_scan.py, bin/gadget_mapper.py)
  03_content_discovery/         ← Pipeline 2 (9 skills + AGENT.md + bin/wordlist_builder.py)
  checklists/                   ← .MD checklists: ledgers of completion (300 boxes + phase gates + per-target RUN_LEDGER template)
  review_skill/                 ← the Review Skill: /REVIEW for completion (3 board rules + bin/review_check.py)
  nudge_prompts/                ← re-injection prompts: board's master nudge + 6 variants, 5-part context bundle protocol
  examples/                     ← Example Good Output: up to 10 goal instances to measure against
```

## How to run

1. Read `START.md` for the master harness loop and review gates.
2. Run Pipeline 1 Phase 1 → Phase 2, each skill producing its finished artifact on disk.
3. Feed the analyzed endpoints, params, secrets, and tech choices into Pipeline 2.
4. Run Content Discovery: Phase 1 Generic first, then Phase 1 Specific.
5. Compile the final MD report + curl commands + `custom_list`.

## Division of labor

- **Consumes:** a target in scope (host or app URL).
- **Produces:** `report.md` (MD report), `curl_commands.sh` (curl command per verified item), `custom_list.txt` (JS-derived wordlist) — all under the target's work folder.

## Evidence standard (binds every skill in this pack)

- **Static findings are CANDIDATE until verified.** Nothing is CONFIRMED without: (a) baseline comparison against a known-dead path on the same host, (b) 2× independent reproduction, (c) raw request/response pairs saved to disk.
- **Verdicts:** `CONFIRMED` (meets all three) / `INCONCLUSIVE` (needs another run or a human) / `NEGATIVE` (dead end — documented so nobody re-tests it).
- **Blocked is BLOCKED.** If anti-automation defeats every ladder rung, document it as blocked. Never fabricate results to fill the gap.
- **Secrets:** format-valid matches are CANDIDATE. Never live-test a real secret without explicit user approval. Redact secret values in reports.

## Handoffs

Pipeline 1's analyzed surface feeds Pipeline 2. The final MD report, curl commands, and `custom_list` feed the deep-hunt-loop agents (THINKER, CURLER) and the per-target recon folders (`TECHSTACK/`, `KNOWLEDGE/`, `LEAD/`, `raw/`).
