---
name: store-normalize
description: >
  Stores every harvested file in a content-hash-deduped, per-run-versioned layout (raw / normalized / manifest), then un-minifies and carefully deobfuscates the code for analysis. USE THIS SKILL whenever the user wants to organize harvested JS, after all other Phase-1 skills, or says "normalize the js", "dedupe", "deobfuscate", "unminify". Trigger on: "store and normalize", "dedupe js", "unminify", "deobfuscate js", "js-beautify", "finalize inventory". This skill produces normalized/ plus inventory_final.json – the entire Phase-2 analysis pipeline fires it as its input.
---

# Store & Normalize

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn the raw harvest into a CLEAN, deduped, readable corpus — one canonical copy of every unique file, un-minified where possible, honestly deobfuscated where feasible. Analysis on a messy corpus double-counts findings and misses renamed duplicates; analysis on minified soup misses logic.

## Step 1 – Gather Inputs

Collect everything before starting:

- **Consumes:** `<RUN_DIR>/js_inventory/raw/` (entry bundles), `raw/chunks/` (lazy chunks), `raw/inline/` (inline scripts), `raw/maps/` (sourcemaps), `sourcemap_sources/` (extracted originals), `historical/` (old bundles), plus `manifest.json`, `chunk_manifest.json`, `sourcemap_report.md`, `diff_old_new.md`.
- Output home: `<RUN_DIR>/js_inventory/normalized/` + `<RUN_DIR>/js_inventory/inventory_final.json` + `<RUN_DIR>/js_inventory/normalize_failures.md`.
- Check tools: `npx prettier --version` (or a local prettier install), `python3`. If prettier is missing: `npm i -g prettier` — if npm is unavailable, fall back to a documented manual step, not a skipped step.
- Assign this run an ID now: `run_id = <TARGET_HOST>_<YYYYMMDD>_<HHMM>` — every artifact from here carries it, so reruns never collide.

## Step 2 – Decide When to Use vs When to Skip

**USE when:** any Phase-1 harvest produced files; before Phase 2 begins; rerunning on a target whose bundles changed (new run_id, old runs kept for diffing).

**SKIP when (time-pass filter):**
- The harvest produced zero files (all BLOCKED / NEGATIVE) — there is nothing to store. Document the empty corpus and stop; do not manufacture a layout around nothing.
- A previous run's `inventory_final.json` already covers byte-identical files (compare sha256 sets) — rerunning prettier on identical bytes is time-pass. Record "no change since run <id>" and stop.

## Step 3 – Enforce the Storage Layout

Final on-disk layout — exact, no improvisation:

```
<RUN_DIR>/js_inventory/
  raw/                  # byte-exact harvest (entry bundles, chunks/, inline/, maps/)
  sourcemap_sources/    # extracted originals (already clean — copied, not re-processed)
  historical/           # old bundles
  normalized/
    <sha16>.js          # un-minified / deobfuscated working copies
    <sha16>.meta.json   # per-file: original path, transforms applied, failures
  manifest.json         # spider-harvest output (kept as-is)
  chunk_manifest.json   # lazy-loaded-chunks output (kept as-is)
  inventory_final.json  # THE canonical index (Step 8)
  normalize_failures.md # honest failure log (Step 7)
  fetch_log.md          # anti-automation-fetch output (kept as-is)
```

Move (do not copy) harvest outputs into this layout if they are not already there. `raw/` is IMMUTABLE after this step — every transform writes to `normalized/` and records itself in the `.meta.json`. If you cannot tell which file is the original of a normalized copy, the layout is broken.

## Step 4 – Dedupe by sha256 Across All Sources

The same bundle hides in four places (entry, chunk, historical re-download, sourcemap sibling). Collapse them:

```bash
python3 - <<'EOF'
import hashlib, json, os, glob
seen, dupes = {}, []
for f in glob.glob('<RUN_DIR>/js_inventory/raw/**/*.js', recursive=True) + \
         glob.glob('<RUN_DIR>/js_inventory/historical/*.js') + \
         glob.glob('<RUN_DIR>/js_inventory/sourcemap_sources/**/*.js', recursive=True):
    h = hashlib.sha256(open(f,'rb').read()).hexdigest()
    if h in seen:
        dupes.append((f, seen[h]))   # duplicate -> canonical mapping
    else:
        seen[h] = f
json.dump({'unique': seen, 'duplicates': dupes},
          open('<RUN_DIR>/js_inventory/dedupe_map.json','w'), indent=1)
print('unique:', len(seen), 'dupes:', len(dupes))
EOF
```

- `dedupe_map.json` records every duplicate → canonical mapping. Downstream analysis reads the CANONICAL set only — a finding in a dupe is the same finding, and double-reporting it is a false-positive factory.
- Historical files that hash-match current files are marked `superseded_by_current: true` — kept on disk, excluded from the analysis set.

## Step 5 – Detect Minified vs Obfuscated vs Readable

Classify each unique file BEFORE transforming — the transform depends on the class:

```bash
python3 - <<'EOF'
import glob
for f in glob.glob('<RUN_DIR>/js_inventory/raw/*.js'):
    lines = open(f, encoding='utf-8', errors='ignore').read().splitlines()
    nonblank = [l for l in lines if l.strip()]
    if not nonblank: print(f, 'EMPTY'); continue
    avg = sum(len(l) for l in nonblank) / len(nonblank)
    cls = 'minified' if avg > 500 else 'readable'
    print(f, cls, 'avg_line_len=%.0f' % avg)
EOF
# Obfuscation markers (checked separately — a file can be minified AND obfuscated):
grep -l "_0x[a-f0-9]\{4,\}\|\\x[0-9a-f]\{2\}.\{0,20\}_0x\|obfuscator" <RUN_DIR>/js_inventory/raw/*.js
```

- `readable` → copy to `normalized/` unchanged, note `transform: none`.
- `minified` (long lines, short names, no string-array tricks) → Step 6a.
- `obfuscated` (hex identifiers `_0x...`, string-array IIFE, control-flow flattening) → Step 6b.
- `EMPTY` → record in `normalize_failures.md`, exclude from analysis.

## Step 6a – Un-Minify With Prettier (Minified Files)

Minified ≠ obfuscated: names are shortened but the logic is intact. Prettier restores readability:

```bash
npx --yes prettier --parser babel --write "<RUN_DIR>/js_inventory/normalized/<sha16>.js" < /tmp/minified_input.js
# Verify the transform did not corrupt: re-parse both with node
node --check <RUN_DIR>/js_inventory/normalized/<sha16>.js && echo "PARSE-OK"
```

- If prettier fails to parse, try `--parser meriyah` as fallback; if both fail, log to `normalize_failures.md` and keep the minified original as the analysis copy — a corrupt "normalized" file is worse than an ugly original.
- Record in `<sha16>.meta.json`: `{"transform": "prettier", "parser": "babel", "parse_ok": true}`.
- Honest limit: prettier restores FORMATTING, not original names. Do not claim "deobfuscated" for a prettified file — mark it `readability: formatted-minified`.

## Step 6b – Deobfuscate With Documented Limits (Obfuscated Files)

For obfuscator.io-style code (string-array + `_0x` accessors), apply the mechanical, verifiable transforms ONLY:

```bash
# 1. Format first (same as 6a) so the patterns are visible
# 2. String-array recovery: the array IIFE + decoder function — extract and evaluate the DECODER ONLY in isolation:
python3 - <<'EOF'
import re
src = open('<RUN_DIR>/js_inventory/normalized/<sha16>.js', encoding='utf-8', errors='ignore').read()
# Find the string-array definition: var _0xabc1=["...","...",...];
m = re.search(r'var (_0x[0-9a-f]+)=\[(.*?)\];', src, re.S)
print('array var:', m.group(1) if m else 'NOT-FOUND', '| entries:', m.group(2).count(',')+1 if m else 0)
# Find the decoder: function _0x1234(_0xabcd,_0xef){...}
d = re.search(r'function (_0x[0-9a-f]+)\([^)]*\)\{[^}]{0,400}\}', src)
print('decoder fn:', d.group(1) if d else 'NOT-FOUND')
EOF
```

Rules for this step, non-negotiable:
- Recover string literals by evaluating the decoder function in a SANDBOXED node `vm` context with NO network, NO fs, NO timers — never `eval()` the whole bundle.
- Replace `_0x...(0x1a)` call sites with recovered literals ONLY where the decoder output is deterministic across 2 runs.
- What you may NOT claim: full variable renaming, control-flow unflattening, or "fully deobfuscated". Those need manual RE work beyond this skill.
- Record in the `.meta.json`: `{"transform": "string-array-recovery", "literals_recovered": N, "call_sites_replaced": M, "residual_obfuscation": ["control-flow-flattening", "renamed-identifiers"]}`.
- If the array/decoder pattern is NOT FOUND (custom obfuscator, wasm, packed `eval`): log to `normalize_failures.md` with the observed markers and STOP transforming that file — the formatted-minified copy stands. Never force a deobfuscation that is not there.

## Step 7 – Log Every Failure Honestly

`normalize_failures.md` gets an entry for EVERY file that did not reach clean normalized state:

```markdown
## <sha16>.js — <original filename>
- Class: obfuscated (custom packer, no _0x string array found)
- Attempted: prettier format OK; string-array recovery NOT APPLICABLE (pattern absent)
- Residual: full custom obfuscation intact
- Analysis guidance: treat as opaque; mine only string literals via `strings` output below
- strings sample: <first 20 interesting strings>
```

A file in this log is not a failure of the run — it is a documented boundary. Phase 2 reads this file FIRST so nobody wastes hours re-attempting your dead ends, and nobody mistakes an opaque blob for analyzed code.

## Step 8 – Build inventory_final.json

The canonical index every Phase-2 skill reads. Exact schema:

```json
{
  "run_id": "app.example.com_20261004_1430",
  "target": "https://app.example.com",
  "files": [
    {
      "sha256": "<full hex>",
      "sha16": "<first 16>",
      "raw_path": "raw/<sha16>.js",
      "normalized_path": "normalized/<sha16>.js",
      "origin": "spider-harvest | chunk | inline | historical | sourcemap",
      "class": "readable | formatted-minified | partially-deobfuscated | opaque",
      "size": 482103,
      "in_analysis_set": true,
      "superseded_by_current": false
    }
  ],
  "counts": {"unique": 0, "in_analysis_set": 0, "opaque": 0},
  "blocked": ["<urls from fetch_log.md BLOCKED entries>"]
}
```

Validate: `python3 -c "import json; d=json.load(open('<RUN_DIR>/js_inventory/inventory_final.json')); assert d['counts']['in_analysis_set']>0 or d['blocked']; print('OK')"`. An empty analysis set with no BLOCKED entries means the harvest failed silently — go back, do not proceed.

## Step 9 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

- [ ] Storage layout enforced exactly (`raw/`, `normalized/`, manifests at the named paths); `raw/` immutable after this step
- [ ] `run_id` assigned and stamped on all new artifacts
- [ ] sha256 dedupe run across raw + chunks + historical + sourcemap_sources; `dedupe_map.json` written
- [ ] Duplicates mapped to canonical files; historical hash-matches marked `superseded_by_current`
- [ ] Every unique file classified (readable / minified / obfuscated / empty)
- [ ] Minified files prettified; parse-verified with `node --check`; parser recorded in `.meta.json`
- [ ] Obfuscated files: string-array recovery attempted in sandboxed `vm` only; literals replaced only when deterministic 2x
- [ ] No claim of "fully deobfuscated" anywhere — residual obfuscation listed per file
- [ ] Every un-normalizable file logged in `normalize_failures.md` with analysis guidance
- [ ] `inventory_final.json` written, schema-valid, non-empty analysis set (or BLOCKED documented)
- [ ] BLOCKED URLs from `fetch_log.md` carried into `inventory_final.json`

**Nudge prompts:** "Did I dedupe the chunks against the entry bundles, or are duplicates inflating my counts?" — "Did I claim deobfuscation I cannot prove with the meta.json?" — "Do not report done before inventory_final.json exists on disk."

## Step 10 – Evidence Standard (No False Positives)

- **Baseline:** dedupe is hash-equality, not name-equality — two files with the same name but different hashes are DIFFERENT files. Name-based dedupe is how findings get silently dropped.
- **2x reproduction:** decoder determinism checked twice before any literal substitution; prettier output parse-checked with `node --check` every time.
- **Raw pairs saved:** `raw/` is the evidence — byte-exact, immutable, hash-indexed. Any dispute about "what did the original say" resolves against `raw/`, never against `normalized/`.
- **Verdicts:** per file: `readable` / `formatted-minified` / `partially-deobfuscated` / `opaque` — these are transform states, and the analysis set carries them so Phase 2 calibrates confidence accordingly. An opaque file contributes string literals only, never logic claims.
- **Blocked = BLOCKED:** carried forward from `fetch_log.md` into the final inventory. The analysis set is explicitly "everything except BLOCKED and superseded" — no silent exclusions.

## Step 11 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/normalized/` (working copies + `.meta.json` per file) + `<RUN_DIR>/js_inventory/inventory_final.json` (canonical index) + `<RUN_DIR>/js_inventory/normalize_failures.md` + `<RUN_DIR>/js_inventory/dedupe_map.json`.

**Handoff:** ALL of Phase 2 (`02_js_analyze/`) consumes `inventory_final.json` as its input manifest — `dangerous-functions-gadgets` traces the normalized copies, `params-routes` and `api-analysis` mine them, `secrets-analysis` scans them, `jsluice-jxscout-tools` parses them. Pipeline 2's `js-to-wordlist` tokenizes the normalized set. The single most valuable handoff line: "N files in the analysis set, M opaque (strings-only), K BLOCKED — start with the partially-deobfuscated admin chunks."
