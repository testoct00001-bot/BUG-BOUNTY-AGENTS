---
name: bugbounty-report-intel
description: >
  Mines public bug-bounty writeups, blogs, and disclosure reports for path, route, and file patterns per tech stack, extracts the adaptable TRICK from each target-specific detail, maps it onto the current target's stack, and logs every tried pattern with its result so no pattern is ever tested twice. USE THIS SKILL whenever the user wants to turn public writeup knowledge into target-specific discovery patterns. Trigger on: "mine writeups for paths", "bug bounty report intel", "writeup pattern mining", "paths from public reports", "adapt writeup tricks". This skill produces the pattern playbook – the app-specific-files and ffuf-workflow skills fire it by converting proven patterns into live probes.
---

# Bug Bounty Report Intel

You are operating as the world's best bug bounty hunter and red teamer. Your job is to convert other hunters' public wins into this target's discovery battery. Every writeup has a TRICK buried in target-specific detail — `/api/v2/internal/debug` on a Laravel app becomes "versioned API + internal qualifier + debug suffix," which becomes a battery for THIS Laravel target. You extract the pattern, not the URL. And you log every pattern you test with its result, because re-testing a dead pattern six months later is how time dies.

## Step 1 – Gather Inputs

- `02_js_analyze/tech_choices.md` — your stack filter. A WordPress RCE writeup's
  path pattern is noise on a Next.js target; the stack filter keeps the signal.
- `02_js_analyze/libraries.md` — library + version pairs worth searching
  ("<library> <version> exposed endpoint writeup").
- The target's industry/shape (SaaS admin? API gateway? e-commerce?) — patterns
  from the same shape transfer better than patterns from the same stack alone.
- A search log file: `discovery/writeup_search_log.md` (queries run, result counts,
  which results were read). Start it now — undocumented research is unrepeatable research.

Division of labor: consumes tech fingerprint + library list; produces
`discovery/writeup_patterns.md` (the pattern playbook: pattern | trick | source |
stack | tried? | result) and `discovery/writeup_search_log.md`. This skill performs
NO live probing itself — it produces ammunition. Probing belongs to
`app-specific-files` / `ffuf-workflow`. Skip when `tech_choices.md` is inconclusive
(no stack = no filter = noise), or when the playbook already covers the current
stack from a previous run (extend it, don't rebuild it).

## Step 2 – Search with Stack-Scoped Queries

Run searches scoped to the target's stack and shape. Query templates:
- `"<framework>" exposed endpoint bug bounty writeup`
- `"<framework>" hidden admin panel discovery hackerone`
- `"<library> <version>" sensitive file disclosure writeup`
- `"backup file" <framework> bug bounty`
- `site:hackerone.com/hacktivity <framework> path disclosure` (adapt to what's searchable)
- `"<framework>" actuator/swagger/graphql exposed report`

Read the actual writeup, not the tweet summary. For each useful report record:
URL, date, target stack, the exact path/file/route involved, and the impact class.
Log every query + result count in `writeup_search_log.md` before reading — if you
can't show your search trail, you can't show you were thorough.

## Step 3 – Extract the Adaptable TRICK

For each writeup, strip the target-specific detail and keep the TRICK. Worked examples:
- Writeup: `/api/v2/internal/debug` exposed stack traces on a Laravel app →
  TRICK: *versioned API prefix + internal qualifier + debug-family suffix* →
  battery: `/api/v1/internal/debug`, `/api/v2/internal/debug`, `/api/internal/debug`,
  `/api/v2/internal/trace`, `/api/v2/internal/logs` (mapped to target's API version
  from `api_map.md` if available, else v1/v2/v3).
- Writeup: `/.git/HEAD` on a Next.js deploy → TRICK: *VCS metadata on JS-framework
  deploys* → battery: `/.git/HEAD`, `/.git/config` (already generic — dedupe, note
  the writeup as corroboration, raise its priority).
- Writeup: `/wp-content/uploads/2023/backup.zip` → TRICK: *date-structured upload
  dirs holding archives* → battery: `/wp-content/uploads/<yyyy>/backup.zip` for the
  last 3 years (only if target is WordPress — stack filter).
- Writeup: Spring `/actuator/heapdump` → TRICK: *actuator endpoints beyond health* →
  battery: the full actuator family (dedupe against `app-specific-files`).

The TRICK is one sentence. If you can't state it in one sentence, you haven't
extracted it — you've copy-pasted a URL.

## Step 4 – Map the TRICK to the Target Stack

Translation rules, applied explicitly per pattern:
- Framework path conventions translate: Laravel `/telescope` → Rails `/sidekiq` →
  Django `/admin` — same TRICK (dev dashboard exposed), different path.
- Version qualifiers come from the target: use the API version seen in
  `api_map.md` / JS (`/api/v3/` observed → probe `/api/v3/internal/debug`, not v2).
- Naming conventions come from `routes_params.md`: if the target uses
  kebab-case routes, the battery uses kebab-case (`/internal-debug`, not
  `/internal_debug`).
- Every mapped battery row records: original writeup URL, TRICK sentence,
  translation rule applied, final path list. Untranslatable patterns (requires a
  plugin the target doesn't run) are logged as SKIPPED with the reason — not silently
  dropped, not force-fit.

## Step 5 – Dedupe Against Existing Batteries

Before the playbook is final, dedupe every pattern against `generic_files.txt`,
`generic_routes.txt`, and `app_specific.txt` (already probed = don't re-probe;
note the writeup as corroboration on the existing row instead) and against the
playbook's own `tried` log from previous runs (a pattern tried with result
NEGATIVE on this target is never re-tried without a changed reason — new API
version observed, new deploy, etc.). The dedupe pass is what makes this skill
compound instead of loop.

## Step 6 – Write the Pattern Playbook

`discovery/writeup_patterns.md` format — one section per pattern:

```markdown
## PATTERN-07 — versioned internal debug endpoints
- TRICK: versioned API prefix + internal qualifier + debug-family suffix
- Source: <writeup URL> (<date>) — <one-line what happened>
- Target stack mapping: <framework> — translation rule applied
- Battery:
  - /api/v2/internal/debug
  - /api/v2/internal/trace
- Status: UNTRIED | TRIED-<date> | CONFIRMED-<finding-ref> | NEGATIVE-<date>
- Result notes: <what the probe returned, or empty if untried>
- Deduped against: <existing artifact rows, if any>
```

Status lifecycle is mandatory: UNTRIED → (probing skill runs it) → CONFIRMED or
NEGATIVE with date. A pattern without a status is a rumor. The playbook is a living
file — probing skills update statuses, they don't rewrite history.

## Step 7 – Log Tried / Result Religiously

When `app-specific-files` or `ffuf-workflow` runs a playbook battery, the result
comes back here: status + date + one-line result note. CONFIRMED patterns get a
finding reference; NEGATIVE patterns get the baseline-verified note. This log is
the institutional memory that stops the next hunt from re-testing
PATTERN-07 on the same target. If a pattern is re-tried, the reason for the
re-try (new version, new deploy, changed baseline) is logged — "felt like it"
is not a reason.

## Step 8 – Exact Commands (Copy-Paste)

```bash
# 1. Start the search log
cat > discovery/writeup_search_log.md <<'EOF'
# Writeup search log — <target> — <date>
## Queries
EOF

# 2. Stack-scoped searches (run via your search tool; log each)
# "<framework>" exposed endpoint bug bounty writeup
# "<framework>" hidden admin panel discovery hackerone
# "<library> <version>" sensitive file disclosure writeup

# 3. Playbook skeleton (one section per extracted pattern)
cat >> discovery/writeup_patterns.md <<'EOF'
## PATTERN-NN — <short name>
- TRICK: <one sentence>
- Source: <url> (<date>)
- Target stack mapping: <framework> — <translation rule>
- Battery:
  - <path 1>
- Status: UNTRIED
- Result notes:
- Deduped against:
EOF

# 4. Dedupe a new pattern battery against everything already probed
for p in $(sed -n '/^- Battery:/,/^- Status:/p' discovery/writeup_patterns.md | grep '^  - /'); do
  path=$(echo "$p" | sed 's/^  - //')
  grep -qxF "CONFIRMED $path" discovery/generic_files.txt discovery/generic_routes.txt discovery/app_specific.txt 2>/dev/null \
    && echo "DUPE(probed): $path" || echo "NEW: $path"
done
```

## Step 9 – Completion Checklist

- [ ] `tech_choices.md` + `libraries.md` read; stack filter documented
- [ ] `discovery/writeup_search_log.md` started; every query + result count logged
- [ ] Minimum 10 stack-relevant writeups/reports read (fewer only if the stack is
      genuinely obscure — document the search trail proving it)
- [ ] Every pattern has a one-sentence TRICK (no URL copy-pastes masquerading as patterns)
- [ ] Every pattern has an explicit target-stack translation (rule named, version/naming
      sourced from target artifacts)
- [ ] Untranslatable patterns logged as SKIPPED with reasons
- [ ] Full dedupe pass against all three verified lists + prior `tried` log
- [ ] `discovery/writeup_patterns.md` written in the exact section format, every
      pattern carrying a status (UNTRIED at minimum)
- [ ] No live probing performed inside this skill (ammunition only — the probing
      skills fire it)
- [ ] Review: reviewer picks 3 patterns, re-derives the TRICK from the source URL
      independently, and checks the translation rule against target artifacts.
      A pattern whose TRICK doesn't survive independent re-derivation is deleted.
- Nudge prompts:
  - "You saved the URL. Now say the TRICK in one sentence — out loud. Can't? Then you don't have it yet."
  - "This pattern needs a WordPress plugin the target doesn't run. Mark it SKIPPED with the reason — don't force it."
  - "PATTERN-07 was NEGATIVE on this target in March. What's changed that justifies re-trying it? Write it down or leave it."

## Step 10 – Evidence Standard (No False Positives)

- This skill makes no CONFIRMED claims about the target — its outputs are UNTRIED
  batteries and a search trail. CONFIRMED/NEGATIVE verdicts on patterns are written
  only by the probing skills, with their baseline + reproduction discipline.
- A pattern's "Source" must be a real, readable report (URL + date). "I recall a
  writeup about…" is not a source — find it or drop the pattern.
- SKIPPED patterns need the disqualifying reason in writing; silent drops hide
  methodology holes.
- The search log is the completeness evidence: queries, counts, what was read,
  what was rejected and why.

## Step 11 – Finished Artifact & Handoff

Done = `discovery/writeup_patterns.md` exists with ≥1 pattern sections in the exact
format (or a documented `NO-PATTERNS <stack> <date>` block with the search trail
proving the stack yielded nothing — an empty file is not a finished run), plus
`discovery/writeup_search_log.md` with the full query trail.

Handoff: **app-specific-files** consumes UNTRIED pattern batteries matching its
framework sections and converts them into probes (updating pattern statuses on
return). **ffuf-workflow** consumes multi-path pattern batteries as seeded wordlists
for calibrated runs. Surprising CONFIRMED finds from any probing skill flow BACK
here as new pattern seeds — the playbook grows with every hunt.
