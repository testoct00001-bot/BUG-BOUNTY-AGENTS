# Nudge Prompt Library

Pick the variant matching the diagnosis in `SKILL.md` Step 1. Fill the `<PLACEHOLDERS>`.
Never use the generic master nudge when a specific variant fits.

---

## The board's master nudge (verbatim, typos preserved)

> "Your work was just reviewed by the review skill and it was found that you either
> missed a step of analysis, or didnt generate an artifact of sufficient proof. Look at
> the markdown based checklist and the output for each step, find what you missed, and
> comeplete that step."

## Polished master nudge (default when no variant fits exactly)

> "Your work was just reviewed by the review skill. It found that you either missed a
> step of the analysis or did not generate an artifact of sufficient proof. Open the
> markdown checklist for your skill and the output of each step, find exactly what you
> missed, and complete that step. Do not report done until the checklist box is ticked
> AND the artifact exists on disk with non-zero bytes."

---

## Variant 1 — missed-step

**When:** checklist boxes were never attempted.

> "Your work on `<SKILL>` was reviewed. These checklist steps were never attempted:
> `<BOXES>`. Review excerpt: `<REVIEW_EXCERPT>`. Re-read the procedure in
> `<SKILL_PATH>/SKILL.md`, execute each missed step in order, and produce the finished
> artifact at `<ARTIFACT_PATH>`. Reply with the artifact path and the boxes you are now
> ticking — 'done' without both is not accepted."

## Variant 2 — insufficient-proof

**When:** the artifact exists but is below the bar (too small, missing keys/sections,
no baseline beside the probe, no raw pairs).

> "Your work on `<SKILL>` was reviewed. The artifact at `<ARTIFACT_PATH>` exists but is
> not sufficient proof: `<REVIEW_EXCERPT>`. Strengthen it to the expected good format —
> measure it against `examples/<EXAMPLE_FILE>` — then reply with what changed and why it
> now meets the bar. 'It looks fine' is not a change."

## Variant 3 — zero-byte

**When:** the output file exists but is empty.

> "Your work on `<SKILL>` was reviewed. The output at `<ARTIFACT_PATH>` is ZERO BYTES —
> an empty file is not output. Re-run the step that produces it and verify with `ls -la`
> before replying. If the tool genuinely produced nothing, that is a finding about the
> target — document it as such. It is not a pass."

## Variant 4 — dishonest-tick

**When:** boxes are ticked but no trace exists in any log or artifact.

> "Your work on `<SKILL>` was reviewed. These boxes are ticked but have no trace in any
> log or artifact: `<BOXES>`. A ticked box without evidence is a failed box. Either
> produce the trace (log lines, manifest entries, report sections — with paths and line
> numbers) or untick the boxes and do the work. Reply with the trace locations."

## Variant 5 — stalled-loop

**When:** the same skill failed 3+ nudge cycles.

> "This is the third nudge on `<SKILL>` for the same failure: `<REVIEW_EXCERPT>`. Stop
> repeating the same approach. Either (a) narrow the scope to the smallest failing unit
> and fix that first, or (b) hand to a human with the three bundles attached:
> `<BUNDLE_PATHS>`. Do not attempt a fourth identical run."

## Variant 6 — gate-fail

**When:** a phase gate failed (or was certified PASS dishonestly).

> "Phase gate `<GATE>` was certified `<PASS|FAIL>`, but the review found:
> `<REVIEW_EXCERPT>`. The next phase is BLOCKED until this gate honestly passes. Fix the
> failed skills (`<SKILLS>`), re-certify each gate check with evidence, and reply with
> the corrected gate verdict and the evidence behind each check."
