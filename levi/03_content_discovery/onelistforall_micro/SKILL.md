---
name: onelistforall-micro
description: >
  Runs breadth fuzzing with six2dez's OneListForAll micro wordlist (the curated low-hanging-fruit list) under the same calibration discipline as ffuf-workflow, merges it with tech-specific short lists and custom_list.txt into combined runs, and routes output into discovery/. USE THIS SKILL whenever the user wants broad wordlist coverage beyond a single curated list. Trigger on: "run onelistforall", "micro wordlist fuzz", "broad wordlist run", "combined wordlist fuzzing", "OLFA micro". This skill produces breadth coverage with calibrated filters – the js-to-wordlist skill fires next by folding confirmed micro-hits back into the custom list.
---

# OneListForAll Micro

You are operating as the world's best bug bounty hunter and red teamer. Your job is breadth: the OneListForAll micro list (`onelistforallmicro.txt`, six2dez's hand-curated low-hanging-fruit wordlist) plus the tech-specific short lists, merged with your target-derived `custom_list.txt`, fired through the same calibrated ffuf discipline as `ffuf-workflow`. Breadth without calibration is noise at scale — so the calibration from `ffuf-workflow` carries over, and every micro-hit gets the same manual triage as any other.

## Step 1 – Gather Inputs

- `<TARGET>` base URL. One host per run.
- `discovery/ffuf_<name>_runlog.md` from `ffuf-workflow` — the calibration record
  (baseline values, filter set, rate behavior). If no ffuf run exists yet, you
  calibrate from scratch using the identical procedure (canary + baseline).
- The wordlist files, verified present and counted:
  - `onelistforallmicro.txt` (micro — curated, ~small, high-signal)
  - Optional: `dict/<tech>_short.txt` per-category short lists matching
    `tech_choices.md` (e.g. `dict/laravel_short.txt`) — only the target's tech
  - `custom_list.txt` (target-derived tokens — highest priority)
- `~/wordlists/` layout recommended: `SecLists/`, `OneListForAll/`. Record the
  exact paths used.

Division of labor: consumes calibration record + wordlist files; produces
`discovery/olfa_<name>.txt` (merged wordlist used), `discovery/olfa_<name>.json`
(results), `discovery/olfa_<name>_runlog.md`. Skip when the micro list is a dup
of a previous run on the same host (check runlogs), or when the baseline is a
WAF wall (breadth against a wall = the most expensive way to get zero).

## Step 2 – Fetch and Verify the Wordlists

```bash
mkdir -p ~/wordlists/OneListForAll && cd ~/wordlists/OneListForAll
# Micro list (curated; this is the "micro" in the skill name)
curl -sL -o onelistforallmicro.txt \
  https://raw.githubusercontent.com/six2dez/OneListForAll/main/onelistforallmicro.txt
wc -l onelistforallmicro.txt   # record the count in the runlog
head -5 onelistforallmicro.txt # sanity: entries look like paths, one per line
```

Verify: entries are one-per-line, no leading `/` or `//` (the repo strips those —
if your copy has them, strip with `sed 's|^/*||'`), no blank-line floods.
Record the line count + download date in the runlog. A wordlist you didn't count
is a wordlist you can't reason about.

## Step 3 – Build the Combined List (Merge, Don't Just Concatenate)

The power move is the MERGED list: micro (curated breadth) + tech short list
(stack-specific depth) + `custom_list.txt` (target-specific precision).
Merge with dedupe, keeping provenance:

```bash
cd ~/wordlists/OneListForAll
cat onelistforallmicro.txt > /tmp/olfa_merge.txt
# tech-specific short list ONLY if it matches tech_choices.md:
cat dict/laravel_short.txt >> /tmp/olfa_merge.txt   # example — adapt to YOUR tech
cat /path/to/custom_list.txt >> /tmp/olfa_merge.txt # target-derived, highest value
# Dedupe, drop empties, drop overlong junk (>120 chars rarely a real path)
awk 'NF && length($0)<=120' /tmp/olfa_merge.txt | sort -u > discovery/olfa_combined.txt
wc -l discovery/olfa_combined.txt
```

Save the merged list as `discovery/olfa_<name>.txt` — it IS an artifact (a reviewer
must be able to see exactly what was fuzzed). Note the composition in the runlog:
"micro(N lines) + laravel_short(N) + custom_list(N) → merged(N) after dedupe."

## Step 4 – When to Prefer This Over Plain ffuf

Prefer the OLFA micro run when:
- The calibrated ffuf directory pass came back thin — breadth may catch what the
  curated directory list missed (micro is built from real bounty findings).
- The target's tech has a per-category short list and `tech_choices.md` confirms it.
- You want ONE run covering files+dirs+artifacts instead of three separate passes.

Prefer plain `ffuf-workflow` when:
- You need recursion (`-recursion`) — run micro WITHOUT recursion first (breadth),
  then recurse with ffuf on confirmed dirs (depth). Micro+recursion together =
  request-count explosion.
- You need extension fuzzing (`-e`) or method/param fuzzing — micro is a path list,
  not a mode.
- The host is slow or throttly — micro's breadth at 20/s still takes a while;
  a small seeded ffuf run finishes first and funds the bigger run's justification.

## Step 5 – Fire with the Carried-Over Calibration

Same engine as `ffuf-workflow`, same rules — the ONLY thing that changes is `-w`:

```bash
TARGET="https://target.example.com"
# Re-verify baseline freshness (one dead path) even when carrying calibration over:
curl -sk -o /dev/null -w "baseline recheck: %{http_code} %{size_download}\n" "$TARGET/levi-dead-$RANDOM"

ffuf -u "$TARGET/FUZZ" -w discovery/olfa_combined.txt \
  -fs <baseline_size> -fw <baseline_words> \
  -t 20 -rate 20 -timeout 20 -maxtime 3600 \
  -o discovery/olfa_broad.json -of json -v 2>&1 | tee /tmp/olfa.log
```

Filter flags come from the carried-over runlog — copy them exactly, cite the source
runlog name in the new runlog. If the baseline moved since the ffuf run, recalibrate
fully (new canary, new filters) — stale filters on a moved baseline manufacture hits.

## Step 6 – Triage at Breadth Scale

Micro runs return more candidates than curated runs — triage discipline scales:
1. Sort candidates by size divergence from baseline (biggest delta first) — the
   weirdest responses are usually the most interesting.
2. Batch-kill obvious noise FIRST with one-liners: same-title-as-homepage,
   block-page markers, baseline-hash matches. Document the kill count + rule.
3. Manual-curl every survivor vs baseline (same as `ffuf-workflow` Step 5).
   No exceptions for "it's just the micro list" — breadth doesn't lower the bar.
4. Promote survivors: reproduce 2×, raw pairs, into `discovery/*.txt`.

## Step 7 – Exact Commands (Copy-Paste)

```bash
TARGET="https://target.example.com"

# 1. Fetch + verify micro list
mkdir -p ~/wordlists/OneListForAll && cd ~/wordlists/OneListForAll
curl -sL -o onelistforallmicro.txt \
  https://raw.githubusercontent.com/six2dez/OneListForAll/main/onelistforallmicro.txt
wc -l onelistforallmicro.txt && head -3 onelistforallmicro.txt

# 2. Merge: micro + tech short + custom_list (adapt tech file to YOUR stack)
awk 'NF && length($0)<=120' onelistforallmicro.txt > /tmp/m1.txt
awk 'NF && length($0)<=120' dict/laravel_short.txt > /tmp/m2.txt 2>/dev/null || touch /tmp/m2.txt
awk 'NF && length($0)<=120' /path/to/custom_list.txt > /tmp/m3.txt
cat /tmp/m1.txt /tmp/m2.txt /tmp/m3.txt | sort -u > discovery/olfa_combined.txt
wc -l discovery/olfa_combined.txt /tmp/m1.txt /tmp/m2.txt /tmp/m3.txt

# 3. Baseline recheck + calibrated run (filters from YOUR ffuf runlog)
curl -sk -o /dev/null -w "recheck: %{http_code} %{size_download}\n" "$TARGET/levi-dead-$RANDOM"
ffuf -u "$TARGET/FUZZ" -w discovery/olfa_combined.txt \
  -fs <SIZE> -fw <WORDS> -t 20 -rate 20 -timeout 20 -maxtime 3600 \
  -o discovery/olfa_broad.json -of json -v 2>&1 | tee /tmp/olfa.log

# 4. Sort candidates by size divergence for triage order
python3 -c "
import json
base = <BASELINE_SIZE>
d = json.load(open('discovery/olfa_broad.json'))
rows = sorted(d['results'], key=lambda r: abs(r['length']-base), reverse=True)
for r in rows[:50]:
    print(r['input']['FUZZ'], r['status'], r['length'])
"
```

## Step 8 – Completion Checklist

- [ ] Wordlist provenance recorded: micro line count + date, tech short list (or
      "none — tech has no short list"), custom_list line count, merged count after dedupe
- [ ] Merged wordlist saved as `discovery/olfa_<name>.txt` (the exact fuzzed input)
- [ ] Calibration carried over from the ffuf runlog (source runlog named) OR fresh
      calibration with canary → 0
- [ ] Baseline re-checked immediately before the run (one dead path; moved = recalibrated)
- [ ] Filter flags copied from calibration, each justified in the runlog
- [ ] Candidates sorted by size divergence; batch-kill rules documented with counts
- [ ] EVERY survivor manually curled vs baseline — no JSON-to-finding pipeline
- [ ] Survivors reproduced 2×, raw pairs saved, promoted to `discovery/*.txt`
- [ ] Rate behavior documented; any 429 backoff followed the same de-escalation as ffuf-workflow
- [ ] `discovery/olfa_<name>.json` + `discovery/olfa_<name>_runlog.md` on disk
- [ ] Review: reviewer inspects the merged list composition, replays the calibration
      citation, spot-triages 3 promoted hits. Any promoted hit matching baseline =
      run fails review.
- Nudge prompts:
  - "You merged three lists. Can you show me the line counts of each input? No? Then rebuild it properly."
  - "The micro list found 60 candidates and you triaged 5. The other 55 are still rumors — finish or document why not."
  - "You ran micro WITH recursion and it made 400k requests. Was that the plan, or did you forget Step 4?"

## Step 9 – Evidence Standard (No False Positives)

- Identical bar to `ffuf-workflow`: **CONFIRMED** = manual curl vs baseline
  divergence + understand + 2× reproduction + raw pair. Breadth never lowers the bar.
- **INCONCLUSIVE** / **NEGATIVE** / **BLOCKED** per the same definitions.
- Batch-kill rules must be stated before killing (e.g. "killed 34: title ==
  homepage title") — post-hoc kill rules are how real hits die quietly.
- A carried-over calibration is only valid if the baseline re-check matched.
  Otherwise it's a fresh calibration or it's inadmissible.

## Step 10 – Finished Artifact & Handoff

Done = `discovery/olfa_<name>.txt` (merged wordlist), `discovery/olfa_<name>.json`
(results), `discovery/olfa_<name>_runlog.md` (provenance, calibration citation,
filter justifications, triage summary with counts) on disk, CONFIRMED hits promoted
to `discovery/*.txt`.

Handoff: **js-to-wordlist** consumes CONFIRMED micro-hits as new token sources —
every confirmed path gets tokenized back into `custom_list.txt`, so the custom
list compounds across runs. **ffuf-workflow** consumes CONFIRMED directories for
recursion passes. **phases-generic-specific** consumes runlogs for coverage certification.
