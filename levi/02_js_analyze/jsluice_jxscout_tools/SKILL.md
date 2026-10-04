---
name: jsluice-jxscout-tools
description: >
  Canonical AST-based JS extraction for <TARGET>: jsluice urls/secrets/tree/query over normalized bundles, producing the deduped endpoint, param, and secret inventories that feed every other analysis skill. USE THIS SKILL whenever the user wants to extract endpoints, params, or secrets from JS bundles at scale. Trigger on: "run jsluice on the bundles", "extract endpoints from JS", "jsluice workflow". This skill produces the extraction ammunition – the api_analysis fires it.
---

# JSLuice / jxscout Extraction

You are operating as the world's best bug bounty hunter and red teamer. Your job is to run the canonical AST-based extraction workflow over the target's JS — the single pass that feeds endpoints, parameters, and secrets to every other analysis skill, at a depth generic regex greps will never touch.

## Step 1 – Gather inputs
1. Read `<WORKDIR>/inventory_final.json`: confirm `<WORKDIR>/normalized/` holds the deduped, de-obfuscated bundles and note per-file line counts (the biggest app bundles go first; vendor libs go last and are tagged so their endpoints can be filtered).
2. Verify `jsluice` is installed: `which jsluice || go install github.com/BishopFox/jsluice/cmd/jsluice@latest`. If the install fails or `go` is absent, skip to the python fallback in Step 7 — do not invent flags to work around it.
3. Confirm `jq` is available (`which jq`) — jsluice output is JSONL and every downstream step parses it with jq.
4. Create the output dir: `mkdir -p <WORKDIR>/jsluice_out`.
5. Decide the target base URL: `https://<TARGET>` — used with `-R` to resolve relative paths. Get `<TARGET>` from the work folder name or the phase-1 config; never guess a different host.
6. Check whether `jxscout` is installed (`which jxscout`). If yes, run `jxscout --help` first and adapt — its flags are NOT verified, so nothing below assumes them.

## Step 2 – Run jsluice urls over all normalized bundles
7. Run the full extraction: `find <WORKDIR>/normalized -name '*.js' | jsluice urls -c 5 -S > <WORKDIR>/jsluice_out/urls.jsonl`. The `-S/--include-source` flag keeps the source line for every URL — mandatory for later triage.
8. If any bundle fails to parse, jsluice skips it with an error on stderr — capture stderr to `<WORKDIR>/jsluice_out/urls_errors.log` and note which files were skipped so they can go through the python fallback.
9. Sanity-check the JSONL: `wc -l <WORKDIR>/jsluice_out/urls.jsonl` and `head -c 2000` — confirm lines are JSON objects with `.url` fields before piping anything downstream.
10. Extract and dedupe raw endpoints: `jq -r '.url' <WORKDIR>/jsluice_out/urls.jsonl | sort -u > <WORKDIR>/jsluice_out/endpoints_raw.txt`.
11. If X do Y: if a single bundle dominates the output (>50% of lines from one vendor file), re-run excluding it (`find ... ! -name 'vendor*.js'`) into a separate `urls_app.jsonl` so app-code endpoints aren't buried — then merge with vendor-tagged provenance. If Z pivot: if total lines are suspiciously low (<20 for a multi-bundle app), the bundles may be packed in a way tree-sitter can't parse — fall back to the python parser for those files and diff the counts.

## Step 3 – Split paths vs query params
12. Split on `?`: everything before it is a path, everything after is query material.
13. Write paths: `grep -v '?' endpoints_raw.txt | sort -u > endpoints_paths.txt` — but keep param-less full URLs too; a path with no query is still an endpoint.
14. Extract param keys from the query side (unfurl-style key extraction): take each query string, split on `&`, cut each pair on `=` and keep the key — `sort -u` into `params.txt`.
15. If X do Y: if a URL contains the `EXPR` placeholder (jsluice replaces unknown concatenated expressions with `EXPR`; changeable with `-P/--placeholder`), keep the line as-is in `endpoints_raw.txt` but also emit a normalized variant with `EXPR` → `{param}` into `endpoints.txt` — these are your injection-shaped leads. If Z pivot: if >30% of lines contain EXPR, the bundle is heavily dynamic — re-run with `-S` and read the source lines to recover the concatenation logic manually instead of treating EXPR lines as dead.

## Step 4 – Resolve relative paths against the target
15. Re-run urls mode with path resolution: `find <WORKDIR>/normalized -name '*.js' | jsluice urls -R https://<TARGET> -c 5 > <WORKDIR>/jsluice_out/urls_resolved.jsonl`.
16. Merge: `jq -r '.url' urls_resolved.jsonl >> endpoints_raw.txt`, then `sort -u` everything again.
17. Filter to in-scope: keep only URLs whose host is `<TARGET>` or a relative path — third-party CDN/analytics URLs go to `thirdparty_urls.txt` (kept, not deleted; supply-chain leads matter, but they are not the target's attack surface).
18. If X do Y: if `-R` resolution produces URLs on unexpected sibling subdomains (e.g. `api.<TARGET>` or `cdn.<TARGET>`), do NOT discard them — move them to `sibling_hosts.txt` and flag for scope confirmation; sibling hosts are often where the unauthenticated API actually lives. If Z pivot: if resolution collapses hundreds of distinct relative paths into one URL, the `-R` base was wrong — re-check `<TARGET>` (apex vs www vs app subdomain) and re-run.

## Step 5 – Run jsluice secrets and cross-check
19. Run: `find <WORKDIR>/normalized -name '*.js' | jsluice secrets > <WORKDIR>/jsluice_out/secrets.jsonl`. Only verified option: `-p/--patterns <json-file>` for custom patterns — use it only if you have a target-specific pattern file; otherwise run bare.
20. Cross-check against the `secrets_analysis` engine-1 pattern list: any secret type jsluice flags that the regex engine missed (or vice versa) gets investigated — a divergence means one engine's pattern set has a gap.
21. Dedupe secrets: `jq -c '{type, value}' secrets.jsonl | sort -u` — but keep the file:line provenance in the full JSONL for the secrets skill.
22. If X do Y: if jsluice flags a high-value type (e.g. private key material or cloud credentials), immediately hand the file:line to `secrets_analysis` for CANDIDATE labeling — do not probe it yourself. If Z pivot: if the secrets pass returns nothing while engine 1 found hits, check whether the JSONL parsed at all (`jq empty secrets.jsonl`) — a truncated write from a crashed run looks identical to "no secrets".

## Step 6 – Optional jxscout pass and query-mode deep dives
23. jxscout is an OPTIONAL alternate extractor. Its flags are NOT verified: if installed, run `jxscout --help` first and adapt the command to its actual interface; the jsluice + python fallback above covers the same ground, so jxscout is never load-bearing.
24. Use `jsluice query` for targeted AST questions once you know what you're hunting, e.g. `jsluice query -q '(string) @matches' <file>`; add `-r/--raw-output` to disable JSON encoding when you want raw strings.
25. If X do Y: if the secrets pass surfaces a token assigned in an unusual AST shape (e.g. inside a computed property), write a tree-sitter query for that shape and run it across all bundles — one weird assignment pattern usually repeats. If Z pivot: if query mode returns nothing, the shape you guessed is wrong — go back to `-S` source lines and read the actual code instead of guessing more queries.
26. Also useful: `jsluice tree <file>` dumps the AST for one file — use it to learn the exact node shapes before writing a query, not after guessing three that fail.
27. Record every custom query that worked in `<WORKDIR>/jsluice_out/queries_used.txt` with a one-line note of what it found — the next target reuses them.

## Step 7 – Exact commands
```bash
# BASELINE: run urls mode on one small known bundle, confirm .url output shape
echo '<WORKDIR>/normalized/app.main.js' | jsluice urls -S | head -3 | jq .
# Expected: JSON objects each containing a "url" field and a "source" field.

# PROBE: full extraction workflow
mkdir -p <WORKDIR>/jsluice_out
find <WORKDIR>/normalized -name '*.js' | jsluice urls -c 5 -S \
  > <WORKDIR>/jsluice_out/urls.jsonl 2> <WORKDIR>/jsluice_out/urls_errors.log
jq -r '.url' <WORKDIR>/jsluice_out/urls.jsonl | sort -u > <WORKDIR>/jsluice_out/endpoints_raw.txt

# Split paths vs params (unfurl-style key extraction)
grep -v '?' <WORKDIR>/jsluice_out/endpoints_raw.txt | sort -u > <WORKDIR>/jsluice_out/endpoints_paths.txt
grep '?' <WORKDIR>/jsluice_out/endpoints_raw.txt | cut -d'?' -f2- | tr '&' '\n' | cut -d'=' -f1 | \
  grep -v '^EXPR$' | sort -u > <WORKDIR>/jsluice_out/params.txt
# EXPR-normalized endpoint variants
grep 'EXPR' <WORKDIR>/jsluice_out/endpoints_raw.txt | sed 's/EXPR/{param}/g' | sort -u >> <WORKDIR>/jsluice_out/endpoints_paths.txt
sort -u <WORKDIR>/jsluice_out/endpoints_paths.txt -o <WORKDIR>/jsluice_out/endpoints.txt

# Triage: surface the interesting endpoints first (auth/admin/upload/payment/debug)
grep -iE 'auth|login|token|session|admin|upload|payment|billing|debug|internal|api/v[0-9]' \
  <WORKDIR>/jsluice_out/endpoints.txt | sort -u > <WORKDIR>/jsluice_out/endpoints_hot.txt
# Auth-shaped param keys for params_routes
grep -iE 'token|session|api[_-]?key|auth|sign|secret|password|otp' \
  <WORKDIR>/jsluice_out/params.txt | sort -u > <WORKDIR>/jsluice_out/params_auth_shaped.txt
wc -l <WORKDIR>/jsluice_out/endpoints_hot.txt <WORKDIR>/jsluice_out/params_auth_shaped.txt

# VERIFY: resolve relative paths + secrets pass, then counts
find <WORKDIR>/normalized -name '*.js' | jsluice urls -R https://<TARGET> -c 5 \
  > <WORKDIR>/jsluice_out/urls_resolved.jsonl 2>> <WORKDIR>/jsluice_out/urls_errors.log
jq -r '.url' <WORKDIR>/jsluice_out/urls_resolved.jsonl | sort -u >> <WORKDIR>/jsluice_out/endpoints_raw.txt
find <WORKDIR>/normalized -name '*.js' | jsluice secrets > <WORKDIR>/jsluice_out/secrets.jsonl
sort -u <WORKDIR>/jsluice_out/endpoints_raw.txt -o <WORKDIR>/jsluice_out/endpoints_raw.txt
echo "endpoints: $(wc -l < <WORKDIR>/jsluice_out/endpoints.txt)  params: $(wc -l < <WORKDIR>/jsluice_out/params.txt)  secrets: $(wc -l < <WORKDIR>/jsluice_out/secrets.jsonl)"
echo "EXPR-obscured lines needing manual review: $(grep -c 'EXPR' <WORKDIR>/jsluice_out/endpoints_raw.txt)"
echo "duplicate check (must be empty):"; sort <WORKDIR>/jsluice_out/endpoints.txt | uniq -d | head
```

Python fallback parser (when jsluice is unavailable — regex for `fetch("/...")` and axios):
```python
#!/usr/bin/env python3
"""Fallback endpoint extractor: fetch/axios/XHR regex. Use only if jsluice is missing."""
import sys, os, re, json
PATS = [
    (r"""fetch\(\s*['"`]([^'"`]+)['"`]""", "fetch"),
    (r"""axios\.(?:get|post|put|patch|delete|head)\(\s*['"`]([^'"`]+)['"`]""", "axios"),
    (r"""\$\.(?:get|post|ajax)\(\s*['"`]([^'"`]+)['"`]""", "jquery"),
    (r"""\.open\(\s*['"`](?:GET|POST|PUT|PATCH|DELETE)['"`]\s*,\s*['"`]([^'"`]+)['"`]""", "xhr"),
]
out = []
for root, _, files in os.walk(sys.argv[1]):
    for fn in sorted(files):
        if not fn.endswith(".js"): continue
        src = open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read()
        for pat, kind in PATS:
            for m in re.finditer(pat, src):
                line = src.count("\n", 0, m.start()) + 1
                out.append({"file": fn, "line": line, "kind": kind, "url": m.group(1)})
print(json.dumps(out, indent=2))
```

## Step 8 – Completion checklist
- [ ] `jsluice` verified installed (or documented fallback to the python parser above)
- [ ] `<WORKDIR>/jsluice_out/urls.jsonl` exists; `.url` field shape confirmed with the baseline probe
- [ ] `endpoints_raw.txt` extracted via jq and `sort -u` deduped
- [ ] Paths vs query params split: `endpoints.txt` and `params.txt` both exist and are deduped
- [ ] EXPR-placeholder lines kept raw AND emitted as `{param}`-normalized variants
- [ ] Relative paths resolved with `-R https://<TARGET>`; out-of-scope hosts moved to `thirdparty_urls.txt`
- [ ] `jsluice secrets` run → `secrets.jsonl`; cross-checked against secrets_analysis engine 1
- [ ] jxscout handled correctly: `--help` first if present, never assumed flags
- [ ] Parse errors captured in `urls_errors.log`; skipped files routed to the python fallback
- [ ] `endpoints_hot.txt` (auth/admin/upload-shaped) and `params_auth_shaped.txt` triage subsets built
- [ ] Custom tree-sitter queries that worked recorded in `queries_used.txt`
- [ ] `sibling_hosts.txt` created if `-R` surfaced unexpected subdomains (else noted as none found)
- [ ] EXPR-obscured line count recorded; manual source-read queued for the auth/admin-shaped ones

### Review
A reviewer must verify: (1) `endpoints.txt` and `params.txt` contain no duplicates (`sort -u` proof: `sort file | uniq -d` returns empty); (2) the baseline probe output shows `.url` and `.source` fields, proving `-S` worked; (3) EXPR lines were not silently dropped — count them in `endpoints_raw.txt`; (4) no jsluice flag was used that is not in the verified list above (urls | secrets | tree | query | format; `-S -R -I -c -C -H -w -p -q -r`); (5) `thirdparty_urls.txt` and `sibling_hosts.txt` were actually populated or explicitly marked empty — out-of-scope is a decision, not an accident.
*Are the highest-value endpoints (auth, admin, upload, payment) present in endpoints.txt — or did they hide behind EXPR concatenation that needs manual source reading?*
*Does params.txt contain the auth-shaped keys (token, session, api_key) that params_routes will mutate?*
*Did the secrets cross-check surface any divergence between jsluice and engine 1 — and was the gap investigated, not just noted?*

"Done" = `<WORKDIR>/jsluice_out/` exists with `urls.jsonl`, `secrets.jsonl`, `endpoints.txt`, `params.txt` (all deduped), plus `urls_errors.log` and `thirdparty_urls.txt`, at those exact paths.

## Step 9 – Evidence standard (no false positives)
- Baseline: the single-bundle probe proves the jsluice version on this machine emits the expected `.url`/`.source` shape before the bulk run — a version that changes output shape invalidates downstream parsing.
- Every endpoint in `endpoints.txt` traces to a JSONL line with a source reference (`-S`); an endpoint with no provenance is INCONCLUSIVE, not an endpoint.
- Static = CANDIDATE: extraction finds candidate endpoints, not live ones — liveness is proven later by `api_analysis` with baseline-vs-known-dead-path checks.
- Blocked = BLOCKED: if a bundle fails to parse (logged in `urls_errors.log`) and the fallback also fails, that file is marked BLOCKED in the handoff, never silently skipped.
- Verdicts on extracted items: CANDIDATE (extracted with source) / INCONCLUSIVE (EXPR-obscured, needs manual read) / NEGATIVE (third-party/out-of-scope, moved aside with reason).

## Step 10 – Finished artifact & handoff
- Finished artifact: `<WORKDIR>/jsluice_out/` — `urls.jsonl`, `urls_resolved.jsonl`, `secrets.jsonl`, `endpoints_raw.txt`, `endpoints.txt`, `params.txt`, `thirdparty_urls.txt`, `urls_errors.log` — all deduped.
- Handoff: three consumers, each with exact needs —
  - `api_analysis` consumes `endpoints.txt` (needs the EXPR-normalized `{param}` variants flagged, plus the `-S` source lines for the top 50 auth/admin/upload-shaped endpoints).
  - `params_routes` consumes `params.txt` (needs the raw count and the auth-shaped subset: token/session/key/auth/sign).
  - `secrets_analysis` consumes `secrets.jsonl` (needs file:line provenance for cross-check against its engine-1 hits; divergences listed explicitly).
- Triage subsets ride along: `endpoints_hot.txt` lets `api_analysis` probe auth/admin/upload first without re-grepping; `params_auth_shaped.txt` is the `params_routes` starter mutation list.
- `queries_used.txt` and `sibling_hosts.txt` are shared context: the next target's extraction run starts from the queries that worked here, and sibling hosts may expand scope after user confirmation.
