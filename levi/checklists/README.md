# .MD Checklists — ledgers of completion

## What these are

Markdown checkbox ledgers for every methodology in the LEVI pack. They exist for one
reason: **an agent's claim of "done" is worthless — the checkboxes are the proof.**

## The iron rule

1. **No checkmark = the agent has NOT finished.** Not "mostly finished." Not finished.
2. **Not finished = re-run.** The skill gets re-run from its Step 1, not argued with,
   not summarized, not hand-waved. Re-run until every box is ticked.
3. A phase gate answered FAIL blocks the next phase. No phase starts on a failed gate.

## Files in this folder

| File | What it is | When to use it |
|------|-----------|----------------|
| `phase1_discover_download.md` | Every box from all 6 Phase 1 skills + Phase Gate 1 | During JS discover/download |
| `phase2_analyze.md` | Every box from all 11 Phase 2 skills + Phase Gate 2 | During JS analysis |
| `pipeline2_content_discovery.md` | Every box from all 9 discovery skills + Pipeline Gate | During content discovery |
| `RUN_LEDGER_template.md` | Compact per-target master ledger (one row per skill) | Copy per target, track the whole run |

## How to run a target with ledgers

1. Copy `RUN_LEDGER_template.md` to `<target>_<YYYY-MM-DD>_ledger.md` in the target's
   work folder. Fill in the target and date. This is the master ledger.
2. Copy the three phase files alongside it (`<target>_phase1.md`, etc.).
3. Work each skill by ticking its boxes **in the phase file** as the step is truly done —
   artifact on disk, evidence saved, not "looks right."
4. When a skill's boxes are all ticked, tick its row in the master ledger and record the
   artifact path + verdict counts.
5. Certify each phase gate. FAIL = name the skill, re-run, re-certify.
6. At the end, the master ledger is the run's proof of work: every row ticked, every gate
   PASS, every artifact path filled in.

## Checkbox discipline

- Tick a box only when its step is **verifiably** done (file on disk, command output seen).
- Never tick ahead ("I'll do that next") and never tick a box you skipped.
- If a step is genuinely not applicable, don't tick it — write `N/A: <reason>` next to it.
  An N/A without a reason is an unticked box.
- Sub-lists (`- [ ]` indented under a box) are part of the box: the box is done only when
  its sub-items are done.

## For the review agent

Your first act on any LEVI run: open the ledgers. Count unticked boxes. Every unticked
box is a re-run order with the skill name attached. Do not accept a chat summary that
contradicts the ledger — the ledger wins.

Then run the **Review Skill** (`../review_skill/SKILL.md`) — the board's reviewer:

1. Every tool/action from the checklist has a log file or output — or FAIL.
2. All output is non-zero bytes — or FAIL.
3. Output matches expected good format and size — or FAIL.
4. `/REVIEW`: review above for completion → `review_report.md` with the per-skill
   PASS/FAIL table and numbered re-run orders.

Start mechanical: `python3 ../review_skill/bin/review_check.py --workdir <dir> --phase all`.
Then apply reviewer judgment on top (tick-without-trace audit, size sanity, secrets
redaction). The run is not complete until a re-review returns all-PASS.
