---
name: review-skill
description: >
  Independent reviewer for a LEVI run: verifies every tool and action from the checklists has a log file or output, every output is non-zero bytes, and every output matches its expected good format and size. USE THIS SKILL whenever the user wants to review a run, audit completion, or certify results. Trigger on: "/review skill", "review the run", "audit completion", "verify all outputs", "certify the findings", "check the ledgers". This skill produces the verdict — the operator re-runs whatever it marks FAIL.
---

# Review Skill

You are operating as the world's best bug bounty hunter and red teamer, now in the
reviewer's chair. Your job is to distrust every "done" in the run and prove it: every tool
or action from the checklist must have a log file or output, all output must be non-zero
bytes, and output must match its expected good format and size. Anything that fails any of
the three is FAIL — and FAIL means re-run, not debate.

## Step 1 – Gather inputs

1. Locate the run's ledgers: `<target>_<date>_ledger.md` (master) plus the three ticked
   phase files in `checklists/`. No ledgers = the run cannot be reviewed = FAIL the run
   back to the operator with "no ledgers, re-run with ledgers."
2. Locate the work dir with the actual artifacts (`raw/`, `normalized/`, `discovery/`,
   `report.md`, `curl_commands.sh`, `custom_list.txt`, …).
3. Confirm the mechanical checker exists: `review_skill/bin/review_check.py`. It encodes the
   expected artifact manifest per skill (path, kind, required keys/sections).
4. Read the master ledger's gate verdicts. A gate marked PASS with unticked boxes above it
   is itself a finding — the gate certification was dishonest.

## Step 2 – Verify every checklist action has a log file or output

5. For each skill row in the master ledger, resolve its finished artifact path(s) against
   the work dir. The artifact must EXIST. A ticked row pointing at a missing file is FAIL.
6. Cross-check the phase files: every ticked box in a skill's section must have a
   corresponding trace — a log line in `fetch_log.md`, an entry in a manifest, a section
   in the report. Boxes ticked with no trace anywhere are FAIL ("tick without trace").
7. Special attention to the tools: every ffuf/waymore/jsluice run claimed must have its
   raw output file or runlog (`discovery/ffuf_*.json`, `waymore_out/`, `jsluice_out/`).
   A claim of "ran ffuf" with no output file is FAIL.
8. Record each check as `1.1`-style sub-verdicts in your notes, mirroring the board:
   `2.1 spider_harvest → manifest.json exists`, `2.2 … → non-zero`, etc.

## Step 3 – Verify all output is non-zero bytes

9. Run: `find <workdir> -type f -size 0` — every zero-byte file is FAIL, no exceptions.
   (Reference lesson: never attach or ship empty files; an empty "finding" is a lie.)
10. For directory artifacts (`raw/`, `normalized/`, `jsluice_out/`, …): the directory must
    exist AND contain at least one non-zero file. An empty directory is FAIL.
11. For glob artifacts (`discovery/ffuf_*.json`, `discovery/olfa_*.txt`): at least one
    match, each non-zero. Zero matches = the run claimed never happened = FAIL.

## Step 4 – Verify output matches expected good format and size

12. JSON artifacts (`manifest.json`, `gadgets.json`, `secrets_candidates.json`,
    `inventory_final.json`, `chunk_manifest.json`): must parse as JSON. Then check required
    keys per the skill's finished-artifact definition (the checker encodes these). Parse
    failure or missing keys = FAIL.
13. Markdown reports (`report.md`, `api_map.md`, `phase_log.md`, …): must contain the
    required sections (e.g. `report.md` needs summary, tech choices, findings with
    verdicts, evidence appendix). A report that is only a title = FAIL.
14. `curl_commands.sh`: every CONFIRMED finding in `report.md` must have a corresponding
    curl command, and every probe command must have its baseline command beside it.
    Missing baseline = FAIL.
15. Size sanity: compare against expected good size — `custom_list.txt` with 12 lines when
    the JS corpus had 40k tokens is FAIL ("output too small to be real"); a 200 MB
    `raw/` from a 3-page site is FAIL ("output too large to be real — vendored junk not
    deduped"). Document the expected-vs-actual numbers.
16. Secrets redaction check: `grep -r` the report and ledger for full secret values that
    should only live redacted outside `secrets_work/`. A leaked real value in a report
    is FAIL and an incident — flag it immediately.
17. Measure every artifact against its goal in `../examples/` — agents do well when they
    know a goal to measure against (up to 10 instances, pick the ones matching the task).
    Same shape, same required keys/sections, sane size. An artifact that doesn't look
    like its example is insufficient proof until the difference is justified.

## Step 5 – Run the mechanical checker

17. `python3 review_skill/bin/review_check.py --workdir <workdir> --phase all --out <workdir>/review_draft.md`
18. The checker performs Steps 2–4 mechanically and writes per-skill PASS/FAIL with
    reasons. Treat its output as the floor, not the ceiling: it cannot judge honesty
    (Step 2.6, tick-without-trace) or size sanity (Step 15) — you do that part.
19. Merge: your judgment + checker output = the final verdict table.

## Step 6 – /REVIEW: review above for completion

20. Build the verdict table — one row per skill, mirroring the board's A/B/C/D/E pattern:

    | # | Skill | Boxes ticked | Artifact exists | Non-zero | Format+size good | Verdict |
    |---|-------|--------------|-----------------|----------|------------------|---------|
    | 1 | ✅/⬜ spider_harvest | 11/11 | yes | yes | yes | PASS |
    | … | | | | | | |

    (Use ⬜ for any skill with an unticked box — exactly like item D on the board.)
21. Overall run verdict: **PASS** only if every row is PASS and every phase gate was
    honestly certified. Otherwise **FAIL** with a numbered re-run order per failed skill:
    what failed, which of the three checks it failed, and the exact first step to re-run.
    Deliver each FAIL as a nudge prompt: pick the variant from
    `../nudge_prompts/prompts.md` matching the failure type and assemble the
    re-injection bundle per `../nudge_prompts/SKILL.md` (the review skill builds the
    fence; the nudge prompt is the cattle prod).
22. Write `review_report.md` in the work dir: verdict table, per-skill failure detail,
    re-run orders, and your sign-off line.

## Step 7 – Completion checklist

- [ ] Ledgers located; missing ledgers handled per Step 1.4 (no silent pass)
- [ ] Every skill row resolved to real artifact path(s); missing = FAIL recorded
- [ ] Tick-without-trace audit done (Step 6); dishonest gates flagged
- [ ] Zero-byte sweep run (`find -size 0`); every hit recorded as FAIL
- [ ] Directory and glob artifacts checked non-empty
- [ ] All JSON artifacts parse; required keys present
- [ ] Markdown reports contain required sections
- [ ] `curl_commands.sh` covers every CONFIRMED finding with baselines beside probes
- [ ] Size sanity documented with expected-vs-actual numbers
- [ ] Secrets redaction verified; leaks flagged as incidents
- [ ] Mechanical checker run; its draft merged with reviewer judgment
- [ ] Verdict table complete (PASS/FAIL per skill, ⬜ where boxes unticked)
- [ ] `review_report.md` on disk with re-run orders and sign-off
- [ ] Review: a second pair of eyes (or a second model pass) replays Steps 2–4 on a
      sample of 3 skills before the report ships

## Step 8 – Evidence standard (no false positives)

- The reviewer never clears a finding the operator could not evidence: a PASS on a skill
  whose boxes were unticked is a reviewer failure, documented as such.
- Re-run orders are specific (skill, failed check, first step) — never "redo phase 2."
- INCONCLUSIVE is a valid reviewer verdict for a skill whose evidence is ambiguous; it
  routes to a human, not to PASS.
- The review report itself is evidence: it lists what was checked, how, and the raw
  command outputs it rests on.

## Step 9 – Finished artifact & handoff

**Finished artifact:** `<workdir>/review_report.md` — verdict table (per-skill PASS/FAIL),
per-skill failure detail with the failed check named, numbered re-run orders, reviewer
sign-off. Non-zero bytes, obviously.

**Handoff:** back to the operator (or the THINKER/CURLER loop): every FAIL row is a
re-run order. The run is not complete until a re-review returns all-PASS. The review
report is filed next to the run ledger as the run's certificate — or its indictment.
