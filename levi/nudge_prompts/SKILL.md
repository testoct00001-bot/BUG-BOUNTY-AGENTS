---
name: nudge-prompts
description: >
  Re-injection prompt library for stalled or review-failed LEVI agents: turns a review-skill FAIL into a context bundle that forces the agent to finish the missed step instead of stalling. USE THIS SKILL whenever an agent needs to be nudged back to work, context must be re-injected into the harness, or a review found missed steps or insufficient proof. Trigger on: "nudge the agent", "re-inject context", "the agent stalled", "review failed, make it finish", "push it to completion". This skill produces the nudge — the checklist decides where it lands.
---

# Nudge Prompts

You are operating as the world's best bug bounty hunter and red teamer, now driving the
harness. Your job: when the review skill marks FAIL — or the ledger shows unticked boxes
and the agent has stopped — re-inject exactly the context needed to finish the work. No
more, no less. A nudge is done when the review passes, not when the agent says "done."

## Step 1 – Diagnose why the agent stopped

1. Read `review_report.md` (or the ledger): classify the failure into exactly one type:
   - **missed-step** — checklist boxes never attempted
   - **insufficient-proof** — artifact exists but below the bar (too small, missing keys,
     no baseline beside the probe, no raw pairs)
   - **zero-byte** — output file exists but is empty
   - **dishonest-tick** — box ticked with no trace in any log or artifact
   - **stalled-loop** — same skill failed 3+ nudge cycles
   - **gate-fail** — phase gate certified FAIL (or PASS, dishonestly)
2. If it doesn't fit a type, it fits **missed-step**. Never invent a new type to avoid
   picking one.

## Step 2 – Select the nudge

3. Open `nudge_prompts/prompts.md` and pick the variant matching the diagnosis. Rule: never
   use the generic master nudge when a specific variant fits — specificity is what makes
   the agent move.
4. Fill the placeholders: `<SKILL>`, `<BOXES>` (verbatim from the phase file),
   `<REVIEW_EXCERPT>` (the failed checks with reasons), `<WORKDIR>`.

## Step 3 – Assemble the re-injection bundle

5. The bundle is ONE message with exactly these five parts, in order:
   1. The nudge prompt itself (from `prompts.md`).
   2. The exact failed checklist boxes, copied verbatim.
   3. The review excerpt: failed checks with reasons.
   4. Workdir state: `ls -la` of the artifact paths (proves what is actually on disk —
      the agent cannot argue with `ls`).
   5. Pointer to the skill's `SKILL.md` step that defines the correct procedure.
6. Trim ruthlessly: re-inject context, not the whole conversation. Depending on the
   harness, the agent may have limited context — the bundle must contain everything needed
   to finish THIS step and nothing else. When in doubt, cut history, keep the checklist.

## Step 4 – Deliver and verify

7. Send the bundle into the harness. Require the agent's reply to contain: the artifact
   path(s) produced AND the now-ticked boxes. A reply of "done" with neither is not
   accepted — re-send the bundle with the missing parts highlighted.
8. Re-run the mechanical check on the touched skill:
   `python3 review_skill/bin/review_check.py --workdir <dir> --phase <phase>`.
   Still FAIL → next nudge cycle (max 3) → then the **stalled-loop** nudge → human.
9. Only when the re-review returns PASS may the ledger boxes be ticked.

## Step 5 – Completion checklist

- [ ] Failure classified to exactly one nudge type (Step 1)
- [ ] Specific variant selected from `prompts.md` (not generic when specific fits)
- [ ] Placeholders filled: `<SKILL>`, `<BOXES>`, `<REVIEW_EXCERPT>`, `<WORKDIR>`
- [ ] Bundle has all five parts in order (Step 3)
- [ ] Bundle trimmed to the failed step — no whole-conversation dumps
- [ ] Agent replied with artifact paths + ticked boxes (not just "done")
- [ ] Mechanical re-check run on the touched skill
- [ ] Re-review returns PASS before ledger boxes are ticked
- [ ] Nudge cycles ≤ 3 per skill; 3rd failure → stalled-loop nudge → human
- [ ] Sent bundle saved to `<workdir>/nudges/nudge_<skill>_<n>.md`

## Step 6 – Evidence standard (no false positives)

- A nudge succeeds when the **review passes**, never when the agent declares done.
- The saved bundle is the evidence that the re-injection happened and what it contained.
- If the agent completes a *different* step than the nudged one, that is a new
  missed-step failure on the original step — nudge again, don't accept the swap.
- Three failed nudge cycles on one skill is data, not bad luck: escalate to human with
  the three bundles attached.

## Step 7 – Finished artifact & handoff

**Finished artifact:** `<workdir>/nudges/nudge_<skill>_<n>.md` — the exact bundle sent,
plus the agent's reply and the re-review result appended.

**Handoff:** back to the **review-skill** for re-review of the touched skill. The loop is
`review → nudge → re-review` until all-PASS. The nudge library (`prompts.md`) is the
ammunition for every re-run order the review skill issues.
