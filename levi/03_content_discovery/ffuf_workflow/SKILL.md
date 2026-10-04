---
name: ffuf-workflow
description: >
  Runs fast, calibrated ffuf fuzzing with mandatory 404-baseline calibration before every run, documented match/filter rules per host, recursion on confirmed directories, and JSON output into discovery/. USE THIS SKILL whenever the user wants to fuzz directories, files, or parameters with ffuf at scale. Trigger on: "run ffuf", "fuzz directories", "ffuf workflow", "directory brute force", "fuzz with recursion", "calibrated ffuf run". This skill produces calibrated ffuf result sets with zero baseline-noise – the onelistforall-micro skill fires the same discipline with the combined micro wordlist for breadth.
---

# ffuf Workflow

You are operating as the world's best bug bounty hunter and red teamer. Your job is to run ffuf like a sniper, not a firehose: every run opens with baseline calibration, every filter is documented per host, every "hit" is a baseline divergence — and recursion only descends into directories you confirmed, never into 200-for-everything noise. An uncalibrated ffuf run doesn't find bugs; it manufactures false positives at 500 requests per second.

## Step 1 – Gather Inputs

- `<TARGET>` base URL. One host per ffuf run. (Multi-host runs get multi-host baselines — don't.)
- The wordlist for this run: a derived battery (`/tmp/route_candidates.txt`,
  pattern battery from `writeup_patterns.md`), `custom_list.txt`, or a curated list
  (SecLists `raft-medium-directories.txt` etc.). Record the exact wordlist path +
  entry count + source in the run log. A run whose wordlist you can't name didn't happen.
- `discovery/baseline.txt` — existing baseline if fresh; otherwise you calibrate now.
- Rate policy: default `-t 20 -rate 20` (20 threads, 20 req/s). Raise only with
  evidence the host tolerates it (no 429s in the calibration pass); lower to
  `-t 10 -rate 10` at the first 429. Document the chosen values and why.

Division of labor: consumes target + wordlist + baseline; produces
`discovery/ffuf_<name>.json` (ffuf JSON output), `discovery/ffuf_<name>_runlog.md`
(calibration record, filters used, why), and verified-hit extractions into the
relevant `discovery/*.txt`. Skip when the baseline is a WAF block page (ffuf
against a wall = noise at speed — log BLOCKED), or when the wordlist is a dup of
a previous run on the same host (check runlogs first).

## Step 2 – Calibrate Before Every Run (Mandatory)

No exceptions, no "I calibrated this morning":
1. Run the 3-dead-path baseline curls (see `generic-routes` Step 11). Record
   status/size/words/sha1.
2. Run ffuf's auto-calibration (`-ac`) on a tiny canary wordlist of 5 known-dead
   random strings FIRST: `ffuf -u <TARGET>/FUZZ -w /tmp/canary.txt -ac`. Read what
   `-ac` decided to filter — if it filtered nothing on a 200-for-everything host,
   `-ac` failed you and you must set manual `-fs`/`-fw` filters from the baseline.
3. Write the calibration block into the runlog: baseline values, `-ac` behavior,
   final filter set, and the canary result (canary hits must be ZERO after filters —
   if a canary string "hits," your filters are wrong and the run is void).

## Step 3 – Choose Match/Filter Rules Per Host (Documented)

Default posture: **filter OUT the baseline, match everything else** — then verify.
- Classic 404 host: `-fc 404` (+ `-fs <baseline_size>` if the 404 body is
  suspiciously stable).
- SPA-fallback host (200-everything): `-fs <baseline_size> -fw <baseline_words>`.
  Verify with the canary run: 5 dead strings must produce 0 results. If sizes
  jitter ±few bytes, widen carefully and note why — or switch to manual probing
  for the high-signal subset instead of trusting fuzzy filters.
- JSON-404 API root: `-fc 404 -mr '"error"'`? No — `-mr` matches regex on the
  response; prefer `-fs` on the stable error-body size. Use `-mr` only for
  positive markers you understand (e.g. `-mr 'swagger|openapi'` when hunting specs).
- NEVER `-mc 200` alone on an uncalibrated host. NEVER trust default output
  without the canary check. Every filter flag in the command gets one line in the
  runlog explaining what it excludes and why that exclusion is safe.

## Step 4 – Run: Directories First, Then Files, Then Recursion

Order matters — recursion multiplies requests:
1. **Directory pass** (no extensions): wordlist of directories, `-recursion
   -recursion-depth 2`. ffuf recurses only into responses that passed YOUR filters
   (with `-recursion-strategy default` it recurses into non-404-ish hits — which is
   why Step 3 must be right first).
2. **File pass** on interesting roots: `-e .bak,.old,.json,.zip,.env` extensions
   against CONFIRMED directories only — not the whole host. Extension fuzzing the
   entire host is how you burn 100k requests on favicon variants.
3. **Seeded pass**: `custom_list.txt` / pattern batteries as `-w`, same calibration.
4. **Parameter pass** (if in scope for this run): `-w <params> -X POST -d 'FUZZ=test'`
   or GET `?FUZZ=test`, matching on response divergence — parameters are
   `js-to-wordlist` output territory; don't fuzz params with a directory wordlist.

Between passes, re-check the baseline once (one dead path). If it moved, stop,
recalibrate, note it.

## Step 5 – Triage Every Result Against the Baseline

ffuf output is CANDIDATE until you triage it:
1. For each result: curl it manually, compare status/size/sha1/content-type/title
   against the baseline. ffuf said 200 — the manual check decides.
2. Kill SPA-costume hits (title == homepage title), WAF-block hits (block markers),
   and size-jitter survivors (within baseline ±10% with identical content markers).
3. Survivors get the understand treatment (Step 7 of `generic-routes`): what IS this?
4. Reproduce 2×, save raw pairs, promote to the relevant `discovery/*.txt`.
   A ffuf result that never got a manual curl is not a finding — it's a rumor
   with JSON formatting.

## Step 6 – Rate Limiting, Timeouts, and Being a Good Citizen

- `-rate 20 -t 20` default; `-timeout 20`; `-maxtime 1800` on big lists so a run
  can't sprawl forever unattended.
- First 429/503: drop to `-rate 10 -t 10`, note it in the runlog. Second wave:
  stop the run, log BLOCKED-or-throttled, switch the remainder to manual probing
  of the high-signal subset. Hammering through rate limits is how you get the
  whole program's IP range banned — and the data past the throttle is garbage anyway.
- `-r` (follow redirects) OFF by default — you want to SEE the 301/302 and its
  target, not silently land on the homepage and log a false 200.

## Step 7 – Exact Commands (Copy-Paste)

```bash
TARGET="https://target.example.com"

# 1. Canary wordlist (5 known-dead strings) + calibration run
printf 'levi-canary-%s\n' $RANDOM $RANDOM $RANDOM $RANDOM $RANDOM > /tmp/canary.txt
ffuf -u "$TARGET/FUZZ" -w /tmp/canary.txt -ac -t 10 -rate 10 -v
# EXPECTED: 0 results after -ac filtering. If >0, set manual filters:

# 2. Directory pass (classic 404 host example — ADAPT filters to YOUR baseline)
ffuf -u "$TARGET/FUZZ" -w /path/to/raft-medium-directories.txt \
  -fc 404 -t 20 -rate 20 -timeout 20 -maxtime 1800 \
  -recursion -recursion-depth 2 \
  -o discovery/ffuf_dirs.json -of json -v 2>&1 | tee /tmp/ffuf_dirs.log

# 3. SPA-fallback host example (size/word filters from YOUR baseline numbers)
ffuf -u "$TARGET/FUZZ" -w /path/to/raft-medium-directories.txt \
  -fs 15342 -fw 812 -t 20 -rate 20 -timeout 20 \
  -o discovery/ffuf_dirs_spa.json -of json -v

# 4. Extension pass on a CONFIRMED directory only
ffuf -u "$TARGET/CONFIRMED_DIR/FUZZ" -w /path/to/raft-medium-files.txt \
  -e .bak,.old,.json,.zip,.env -fc 404 -fs 15342 \
  -t 20 -rate 20 -o discovery/ffuf_ext.json -of json

# 5. Seeded pass with custom_list.txt
ffuf -u "$TARGET/FUZZ" -w custom_list.txt -ac -ic \
  -t 20 -rate 20 -o discovery/ffuf_custom.json -of json

# 6. Triage one ffuf result manually (do this for EVERY result)
R="suspicious-path"
curl -sk -o /tmp/tri -D /tmp/trih -w "status=%{http_code} size=%{size_download}\n" "$TARGET/$R"
echo "sha1=$(sha1sum /tmp/tri | cut -d' ' -f1)"; grep -oi '<title>[^<]*' /tmp/tri | head -1
# Compare against discovery/baseline.txt. Diverges? Understand it. Matches? NEGATIVE.

# 7. Extract verified hits from ffuf JSON (after manual triage, not before)
python3 -c "
import json
d = json.load(open('discovery/ffuf_dirs.json'))
for r in d['results']:
    print(r['input']['FUZZ'], r['status'], r['length'], r['url'])
" | tee /tmp/ffuf_candidates.txt
```

## Step 8 – Completion Checklist

- [ ] Wordlist recorded: exact path, entry count, source (derived battery / SecLists / custom_list)
- [ ] 3-dead-path baseline calibrated in THIS run (timestamped in runlog)
- [ ] Canary run executed: 5 known-dead strings → 0 results after filters (or manual
      filters set and canary re-run to 0 — documented)
- [ ] Every `-f*`/`-m*` flag justified in one runlog line each
- [ ] Directory pass → file-extension pass on CONFIRMED dirs → seeded pass, in order
- [ ] Baseline re-checked between passes (one dead path; moved = recalibrated)
- [ ] EVERY ffuf result manually triaged with curl vs baseline (no JSON-to-finding pipeline)
- [ ] SPA-costume / WAF-block / size-jitter kills documented as NEGATIVE with reasons
- [ ] Survivors understood, reproduced 2×, raw pairs saved, promoted to `discovery/*.txt`
- [ ] Rate behavior documented (`-t`/`-rate` values + why; any 429 backoff noted)
- [ ] `discovery/ffuf_<name>.json` + `discovery/ffuf_<name>_runlog.md` on disk
- [ ] Review: reviewer replays the calibration block, re-runs the canary, and
      spot-triages 3 promoted hits with manual curl. Any promoted hit matching
      baseline = run fails review.
- Nudge prompts:
  - "The canary returned 2 hits. Your filters are wrong. Fix them before the real run — not after."
  - "ffuf found 40 '200s'. How many have you manually curled? Zero is not triage."
  - "You raised the rate to 200/s because it was slow. Did the host agree, or did you just decide? Check for 429s."

## Step 9 – Evidence Standard (No False Positives)

- **CONFIRMED** = ffuf result + manual curl vs baseline divergence + understand +
  2× reproduction + raw pair. The JSON is a lead list, never evidence.
- **INCONCLUSIVE** = ffuf hit that diverges weakly or flaps on re-curl.
- **NEGATIVE** = manual curl matches baseline (regardless of what ffuf printed).
- **BLOCKED** = throttled/walled mid-run; documented with the observed signals.
- An uncalibrated run's output is inadmissible — no baseline record, no verdicts,
  re-run it properly.

## Step 10 – Finished Artifact & Handoff

Done = `discovery/ffuf_<name>.json` (raw ffuf output) + `discovery/ffuf_<name>_runlog.md`
(calibration block, wordlist provenance, filter justifications, rate notes, triage
summary with counts: probed / candidates / confirmed / negative) on disk, and every
CONFIRMED hit promoted into the relevant `discovery/*.txt` in its exact format.

Handoff: **onelistforall-micro** consumes the calibration record + filter set — the
same baseline/filters apply to the micro-wordlist breadth run, so calibration work
is never repeated. **js-to-wordlist** consumes CONFIRMED ffuf hits as new token
sources. **phases-generic-specific** consumes runlogs to certify fuzzing coverage
for the phase gate.
