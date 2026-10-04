---
name: js-to-wordlist
description: >
  Tokenizes analyzed JS files into a deduplicated, frequency-annotated custom wordlist: endpoint strings, parameter names, and route fragments become custom_list.txt through camelCase/snake_case splitting, framework-noise stripping, and a conservative, fully-documented mutation policy. USE THIS SKILL whenever the user wants to convert JS analysis output into a target-specific fuzzing wordlist. Trigger on: "JS to wordlist", "build custom wordlist", "tokenize JS", "custom_list", "wordlist from JavaScript", "target-specific wordlist". This skill produces custom_list.txt, the ammunition – the ffuf-workflow and onelistforall-micro skills fire it.
---

# JS to Wordlist

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn the target's own JavaScript into its own worst enemy: every endpoint string, parameter name, and route fragment the developers wrote becomes a wordlist entry that generic lists will never contain. `custom_list.txt` is the highest-signal wordlist in the pipeline because it was written by the target itself. Your discipline: tokenize aggressively, mutate conservatively, document everything.

## Step 1 – Gather Inputs

- The analyzed JS corpus: `raw/*.js`, `raw/chunks/*.js`, `normalized/` (from
  Pipeline 1). Prefer `normalized/` (deduped, un-obfuscated) when it exists;
  fall back to raw with a note.
- `02_js_analyze/api_map.md` — API paths (highest-priority token source).
- `02_js_analyze/routes_params.md` — routes + params (second priority).
- `discovery/` CONFIRMED hits so far (from any probing skill) — confirmed paths
  are tokenized back in, so the list compounds across runs.
- Output path: `custom_list.txt` at the work root (per the pipeline contract).

Division of labor: consumes the JS corpus + analysis artifacts; produces
`custom_list.txt` (one token per line, deduped, frequency-annotated as comments)
and `discovery/wordlist_build_log.md` (corpus stats, rules applied, mutation log).
This skill does NO probing — it manufactures ammunition. Skip when the JS corpus
is empty (no JS = no tokens = say so), or rebuild incrementally when new JS or
new CONFIRMED hits arrive (never silently overwrite — merge).

## Step 2 – Extract Raw Token Sources

Run the extractor (Step 8 / `bin/wordlist_builder.py`) over the corpus. It harvests:
1. **Endpoint-ish strings**: quoted strings starting with `/` (`"/api/v3/users"`,
   `'/admin/panel'`) — path-split into fragments AND kept whole.
2. **Parameter names**: object keys in fetch/axios bodies, query-string keys,
   `URLSearchParams` / `searchParams.get("...")` arguments, form field names.
3. **Route fragments**: React-Router/Vue-Router/Next route definitions
   (`path: "/dashboard/settings"`), `router.push("...")` targets.
4. **Interesting bare tokens**: `admin`, `debug`, `internal`, `token`, `secret`,
   `config` appearing as standalone identifiers (flagged, lower priority).

Keep the source file + line per token in the build log (top tokens only — full
provenance for 50k tokens is noise; keep provenance for the top 200 by frequency).

## Step 3 – Tokenize: Split, Don't Smash

Splitting rules (applied in order, every one of them):
1. **camelCase → parts**: `internalConsole` → `internal`, `console`, `internalconsole`,
   `internal-console`, `internal_console`, `internal/console`. Keep the original too.
2. **snake_case → parts**: `api_key` → `api`, `key`, `apikey`, `api-key`, `api/key`.
3. **kebab-case → parts**: `user-profile` → `user`, `profile`, `userprofile`, `user_profile`.
4. **Path split**: `/api/v3/internal/debug` → `api`, `v3`, `internal`, `debug`,
   `api/v3`, `v3/internal`, `internal/debug`, plus the full path.
5. **Digit handling**: `v3` stays (`v1`/`v2`/`v3` are version qualifiers — also emit
   `v1`,`v2`,`v4` as version-mutation siblings, documented); `user123` → `user`
   (trailing digits stripped, original kept).
6. **Lowercase everything** for the split variants; keep ONE case-variant of the
   original only if the target proved case-sensitive (don't preemptively double
   the list).

## Step 4 – Strip Framework Noise

Delete tokens that are framework vocabulary, not target vocabulary:
`react`, `vue`, `angular`, `component`, `props`, `state`, `render`, `useEffect`,
`useState`, `div`, `span`, `button`, `className`, `onclick`, `function`, `return`,
`const`, `let`, `var`, `import`, `export`, `default`, `null`, `undefined`, `true`,
`false`, `webpack`, `chunk`, `runtime`, `manifest`, `polyfill`, `vendor`,
`node_modules`, `__webpack_require__`, `async`, `await`, `promise`, `then`,
`catch`, `error`, `data`, `item`, `index`, `key`, `value`, `name`, `type`, `id`
(keep `id` ONLY as part of compounds like `user_id` — bare `id` is noise),
`test`, `demo`, `example`, `sample`, `foo`, `bar`, `lorem`.

The noise list lives at the top of `bin/wordlist_builder.py` as `NOISE_WORDS` —
extend it when a new framework's vocabulary pollutes a run, and note the extension
in the build log. When in doubt, keep the token but flag it low-frequency rather
than deleting a possibly-real admin path named `config`.

## Step 5 – Mutate Conservatively (Document Every Mutation)

Allowed mutations — HIGH-SIGNAL ONLY, each logged with count in the build log:
1. **Separator swaps** on compounds: `internalconsole` → `internal-console`,
   `internal_console`, `internal/console` (and reverse: `internal-console` →
   `internalconsole`). These catch the naming-convention misses.
2. **Version siblings**: `v3` → `v1`, `v2`, `v4` (API rot lives in old versions).
3. **Admin-family expansion** (only for tokens containing admin-ish roots):
   `admin` → `administrator`, `administration`; `console` → `consoles`.
4. **Backup suffixes on file-ish tokens**: `config` → `config.bak`, `config.old`,
   `config.json`, `config.zip` (only when the token looks like a filename stem).

FORBIDDEN mutations (the list that keeps this skill honest): random leet-speak,
blind prefix/suffix dictionaries (`dev-`, `-prod`, `-test` on EVERY token),
double extensions, traversal strings, fuzzing payloads. Those are other skills'
jobs. If a mutation isn't in the allowed list, it doesn't ship — and every allowed
mutation's output count is in the build log so a reviewer can see the list didn't
balloon 10× on mutations.

## Step 6 – Dedupe, Frequency-Annotate, Emit

1. Dedupe exact lines (`sort -u` semantics, case-sensitive AFTER lowercasing pass).
2. Frequency: count source occurrences per token; write the top 200 as
   `# freq=<n> <token>` comment lines at the head of a SEPARATE
   `custom_list_freq.md` (keep `custom_list.txt` clean — one token per line,
   ffuf-ready; comments in wordlists break `-w` parsing).
3. Order `custom_list.txt`: API paths whole first, then route fragments, then
   params, then split tokens, then mutations — so a truncated run still fired
   the best ammunition first.
4. Cap: if the list exceeds 50k entries, keep the top 50k by (priority class,
   frequency) and log what was cut and why. A 500k "custom" list is a generic
   list wearing a costume.

## Step 7 – Merge on Rebuild (Never Silently Overwrite)

When new JS arrives or new CONFIRMED hits land: build the new token set, then
`sort -u` merge with the existing `custom_list.txt`, and append a dated section
to `discovery/wordlist_build_log.md` ("rebuild 2026-10-04: +312 tokens from
`chunks/19.js`, +48 from CONFIRMED hits, -0 removed"). Tokens are never deleted
on rebuild except exact dupes — a token that was NEGATIVE as a path may still be
gold as a param.

## Step 8 – Exact Commands (Copy-Paste)

```bash
# 1. Build from the JS corpus (stdlib only)
python3 /home/hatch/workspace/levi/03_content_discovery/bin/wordlist_builder.py \
  --js-dir /path/to/work/normalized \
  --api-map /path/to/work/02_js_analyze/api_map.md \
  --routes /path/to/work/02_js_analyze/routes_params.md \
  --out custom_list.txt \
  --freq-out discovery/custom_list_freq.md \
  --log discovery/wordlist_build_log.md
wc -l custom_list.txt && head -20 custom_list.txt

# 2. Fold CONFIRMED hits back in (compounding across runs)
python3 /home/hatch/workspace/levi/03_content_discovery/bin/wordlist_builder.py \
  --js-dir /path/to/work/normalized \
  --confirmed discovery/generic_routes.txt discovery/generic_files.txt \
              discovery/app_specific.txt \
  --merge custom_list.txt \
  --out custom_list.txt --log discovery/wordlist_build_log.md

# 3. Sanity checks before firing
grep -c '' custom_list.txt                 # total entries (<=50000?)
grep -E '^#' custom_list.txt | head -3      # must be EMPTY — no comments in the firing list
grep -xiE '^(react|vue|div|span|foo|bar)$' custom_list.txt | head # noise spot-check
```

## Step 9 – Completion Checklist

- [ ] Corpus inventoried: file count + total bytes logged (normalized/ preferred, fallback noted)
- [ ] All 4 token sources extracted (endpoints, params, route fragments, bare tokens)
- [ ] All 6 splitting rules applied (camelCase, snake_case, kebab, path-split, digits, case)
- [ ] Framework noise stripped via `NOISE_WORDS` (extensions logged)
- [ ] Mutations limited to the 4 allowed families; every family's output count in the build log
- [ ] Forbidden mutations absent (spot-check: no leet-speak, no blind affix storms)
- [ ] Deduped; `custom_list.txt` has zero comment/blank lines (ffuf-ready)
- [ ] `discovery/custom_list_freq.md` holds the top-200 frequency annotations
- [ ] Priority ordering applied (API paths → routes → params → splits → mutations)
- [ ] 50k cap enforced with cut-logging (or documented under-cap)
- [ ] Rebuilds merge, never overwrite; each rebuild dated in the build log
- [ ] `bin/wordlist_builder.py` compiles clean (`python3 -m py_compile`)
- [ ] Review: reviewer reads the build log, checks the top-20 tokens trace to real
      JS strings, and confirms a random sample of 10 tokens against the corpus
      with grep. Tokens with no corpus source = fabrication = failed review.
- Nudge prompts:
  - "That token — grep it in the JS corpus right now. Not there? Then where did it come from?"
  - "Your list grew 8× on mutations. Which allowed family did that? Show me the counts."
  - "You rebuilt and the count went DOWN. What got deleted, and who authorized it?"

## Step 10 – Evidence Standard (No False Positives)

- Every token must trace to the corpus, `api_map.md`, `routes_params.md`, or a
  CONFIRMED hit — or to a DOCUMENTED allowed mutation of such a token. Unsourced
  tokens are fabrication, not wordlist building.
- **CONFIRMED** (list quality): spot-sample of 10 tokens, all grep-verified in corpus.
- **INCONCLUSIVE**: corpus was obfuscated/minified beyond token recovery — log it,
  ship what extracted, note the limitation.
- Frequency annotations are descriptive (how often the token appeared), never
  claims about exploitability.
- `custom_list.txt` itself makes no findings — it's ammunition. Findings come
  from the skills that fire it, under their evidence bars.

## Step 11 – Finished Artifact & Handoff

Done = `custom_list.txt` exists at the work root: one lowercase token per line,
no comments, no blanks, deduped, priority-ordered, ≤50k entries; plus
`discovery/custom_list_freq.md` (top-200 frequencies) and
`discovery/wordlist_build_log.md` (corpus stats, rules, mutation counts, rebuild history).

Handoff: **ffuf-workflow** fires `custom_list.txt` as a seeded `-w` run under full
calibration. **onelistforall-micro** merges it into the combined breadth list
(highest-priority input). CONFIRMED hits from any probing skill flow BACK here
via `--confirmed` for compounding rebuilds.
