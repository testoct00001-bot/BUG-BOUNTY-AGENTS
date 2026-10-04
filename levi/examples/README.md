# Example Good Output

> "Agent do well when they know a goal to measure against."

This folder holds up to 10 instances of **good output** — one per key artifact type. They are
the goal the review skill's Step 4 ("output matches expected good format and size") measures
against, and the target the nudge prompts point at ("measure it against
`examples/<file>`").

**How to use them:** not every task needs all 10 — pick the instances matching the task
(up to 10 depending on task). When reviewing, diff the run's artifact against the matching
example: same shape, same required keys/sections, sane size. A run artifact that doesn't
look like its example is insufficient proof until the difference is justified.

All data below is synthetic (`shop-example.com`, truncated hashes, redacted secrets).

| # | File | The goal it sets (which skill's output) |
|---|------|------------------------------------------|
| 1 | `manifest.json` | `spider_harvest` — complete inventory: url, sha256, bytes, kind, found_on, failures logged |
| 2 | `chunk_manifest.json` | `lazy_loaded_chunks` — bundler named, every chunk has a `trigger`, fallbacks discarded counted |
| 3 | `diff_old_new.md` | `historical_js` — removed paths tabulated, retired API versions listed, live-probe verdicts |
| 4 | `gadgets.json` | `dangerous_functions_gadgets` — sinks with source traces; CONFIRMED only with a trace |
| 5 | `api_map.md` | `api_analysis` — calls grouped by functionality, old versions flagged |
| 6 | `secrets_candidates.json` | `secrets_analysis` — redacted values, CANDIDATE/NEGATIVE verdicts, no live-testing |
| 7 | `report.md` | `report_output` — summary, tech choices, verdict table, evidence appendix with raw pairs |
| 8 | `curl_commands.sh` | `report_output` — every probe beside its baseline |
| 9 | `custom_list.txt` | `js_to_wordlist` — deduped tokens, compounds kept, noise dropped |
| 10 | `review_report.md` | `review-skill` — verdict table with a FAIL row, numbered re-run order, sign-off |
| 11 | `out_app_target_com/` | **The completed-run directory** — one directory per site, matching the canonical `## Output` structure exactly (see below) |

All data below is synthetic (`shop-example.com`, truncated hashes, redacted secrets).

## Output — one directory per site

A completed run produces one directory per site. This is what good output looks like —
match this structure exactly. Full working instance: `out_app_target_com/`.

```
out/app.target.com/
├── raw/
│   ├── inline/        one file per <script> block: {page-slug}.{index}.js
│   ├── external/      every .js fetched, original bytes, unmodified
│   └── sourcemaps/    .map files + restored original sources
├── beautified/
│   ├── inline/        same filenames as raw/inline/
│   └── external/      same filenames as raw/external/
├── ast/
│   ├── external/      {name}.ast.json per file
│   └── symbols.json   globals, exports, and where each is defined
├── analysis/
│   ├── inline/        {name}.md — one note per inline block
│   ├── external/      {name}.md — one note per JS file
│   └── site-summary.md  cross-file picture: auth flow, API surface, stack
└── findings/
    └── endpoints.jsonl
```

**How LEVI's artifacts map into it:** `raw/` is the immutable byte-exact harvest
(`spider_harvest`); `beautified/` is the working-copy layer (`store_normalize`'s
normalized set — same content, content-hash names with `.meta.json` recording the
original); `ast/` comes from the AST-aware tooling (`jsluice_jxscout_tools`);
`analysis/` is the per-file notes from the 11 analyze skills; `site-summary.md` is the
cross-file picture (`tech_choices` + `feature_map` + `api_map`); `findings/` holds the
verdicts (`report.md`, `curl_commands.sh`, redacted `secrets_candidates.json`) with
`endpoints.jsonl` as the machine-readable route index from `params_routes`.
