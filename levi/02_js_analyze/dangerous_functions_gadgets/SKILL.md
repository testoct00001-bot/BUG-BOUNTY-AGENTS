---
name: dangerous-functions-gadgets
description: >
  Maps every dangerous sink in the <TARGET> JS inventory into a sink/source gadget map and builds verified gadget chains that end in real impact. USE THIS SKILL whenever the user wants to map the dangerous functions, find XSS gadgets in the JS, run a sink-source analysis. Trigger on: "map the dangerous functions", "find XSS gadgets in the JS", "sink source analysis". This skill produces the ammunition – the feature_map skill fires it.
---

# Dangerous Functions & Gadget Mapping

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn the JS inventory into a sink/source map and build gadget chains that end in real impact, not grep noise.

## Step 1 – Gather inputs

- <WORKDIR>/inventory_final.json — the full Phase 1 file inventory; note which files are entry bundles vs chunks vs vendors.
- <WORKDIR>/normalized/ — deduped, de-obfuscated bundles. Run all passes over these, never the minified raws for line accuracy.
- <WORKDIR>/raw/*.js — fallback for when normalized/ lost a string literal during de-obfuscation.
- `02_js_analyze/bin/gadget_mapper.py` — first-pass sink mapper. Verified CLI: `python3 gadget_mapper.py <js_dir> -o gadgets.json`. Output records: `{file, line, sink, context_snippet, verdict: "CANDIDATE"}`. Verify with `python3 gadget_mapper.py --help` first if the CLI rejects anything.
- `jsluice` — for extracting URLs that may be sinks or sources (`go install github.com/BishopFox/jsluice/cmd/jsluice@latest`; `find normalized/ -name '*.js' | jsluice urls`). Any other jsluice flag: verify with `jsluice --help` first.
- Baseline: a known-dead path on <TARGET> (a route that provably 404s with the app's standard 404 shape). Record its exact body/status before any probing.
- Decision rule before you begin: if gadget_mapper.py is missing or errors, do NOT hand-write a regex pass and call it equivalent — run `python3 gadget_mapper.py --help`, fix the invocation, and only fall back to manual passes with a note in the triage file explaining the gap.

Worked chain example (what "done" looks like for one gadget):

- Sink: `main.9f3a.js:4120` — `el.innerHTML = tpl;`
- Backward trace: `tpl` ← `renderCard(user.bio)` ← `user` ← `JSON.parse(localStorage.getItem("profile_cache"))` ← populated by `fetch("/api/v2/profile")` response. Source class: server response from the app's own API — attacker-controllable only if the bio field is user-editable AND rendered for other users.
- Decision: bio is self-editable and shown on public profile pages → chain is `attacker profile bio → /api/v2/profile → localStorage → innerHTML on victim's public-profile render`. Filter analysis: does renderCard sanitize? The bundle showed no DOMPurify import in that module → CANDIDATE for live canary test.
- If instead the trace had ended at a hardcoded template string with zero interpolation → NEGATIVE, one line, move on. This is the discipline: every sink gets a trace verdict, not a vibe.

## Step 2 – First-pass sink mapping with gadget_mapper.py

1. Run `python3 02_js_analyze/bin/gadget_mapper.py <WORKDIR>/normalized -o <WORKDIR>/gadgets_raw.json`. This is the machine's grep — it produces CANDIDATES only, never verdicts.
2. Inventory the sink classes the mapper found: `eval()`, `new Function()`, `setTimeout`/`setInterval` with string args, `innerHTML`/`outerHTML`, `document.write`/`writeln`, `insertAdjacentHTML`, `postMessage` message-event listeners, `location.href`/`assign`/`replace`, jQuery `.html()`/`.append()`, template sinks (`dangerouslySetInnerHTML`, `v-html`, `ng-bind-html`).
3. Map DOM-clobbering SOURCES alongside the sinks: named elements shadowing globals (`id="location"` overwriting `window.location`), `window.name`, `location.hash`/`location.search`, `document.referrer`, `document.URL`. DOM clobbering is often the missing gadget link, so record every named-element declaration as a candidate source.
4. Dedupe by (sink type + enclosing function). Vendor/framework copies (react-dom, jQuery itself) get marked `vendor: true` — they are noise unless the app passes unsanitized data INTO them.
5. Rank by sink power: code-execution sinks (`eval`, `new Function`, string-`setTimeout`) > HTML sinks (`innerHTML`, `insertAdjacentHTML`) > navigation sinks (`location.*`) > `postMessage` listeners (impact depends on origin checks).
6. Write the ranked list to <WORKDIR>/gadgets_triage.md before touching any data flow. Never jump from a grep hit to a payload — that is exactly how false positives are born.

## Step 3 – Triage by reachability (time-pass filter)

7. For each sink ask: is the containing code path reachable unauthenticated? Check route guards (`isAuthenticated`, `useAuth`, redirects to `/login`) around the component. If the path requires auth you do not have and cannot bypass — mark `BLOCKED` (documented, never fabricated) or `NEGATIVE`, move on.
8. Ask: is the code executed at all? Cross-check with Coverage data when available; dead exports, unused feature branches, and code behind permanently-false flags are NEGATIVE. A sink in dead code is a grep hit, not a finding.
9. Ask: does the sink receive anything dynamic? `innerHTML = "<div>static</div>"` with a literal string is NEGATIVE. Only continue when the argument is a variable, template literal with interpolation, or function return.
10. Apply Pulkit's time-pass filter to every survivor: does this lead leak something, touch something sensitive, or is it reachable unauthenticated? If no to all three — NEGATIVE, document the reason in one line, move on.

## Step 4 – Backward source tracing (source → sink)

11. For each surviving sink, trace data flow BACKWARD through the bundle: what feeds the sink argument? Follow assignments, function parameters, state/store reads (`useState`, redux selectors, `localStorage.getItem`), and prop drilling across component boundaries.
12. Classify the ultimate source: attacker-controllable (URL fragments/params via `location.hash`/`URLSearchParams`, `postMessage` data, `window.name`, `document.referrer`, WebSocket messages, fetch responses from attacker-influencable origins) vs internal-only (hardcoded constants, server responses from trusted APIs, user-typed input that the SAME user sees — self-XSS needs a second victim vector to matter).
13. No source trace = stays CANDIDATE, never reported as a vuln. A sink without a traced attacker-controllable source is not a finding. Write this down in the record or the next analyst will re-triage it from scratch.
14. When tracing crosses file boundaries, follow the import chain (`import {x} from './y'` resolved against normalized/ paths). When the trail goes through a minified vendor chunk, note the trail end as `INCONCLUSIVE` with the last observed frame — partial trails are evidence, not blockers.
15. Build the gadget CHAIN for each traced pair: `source → sink → trigger` (e.g. `location.hash` → `innerHTML` on page load; `postMessage` → `eval` on message event; `window.name` → `document.write` via cross-page navigation). The chain — not the single sink — is the unit of verification.

## Step 5 – Filter analysis and minimal payload crafting

16. Before crafting any payload, map the exact reflection context: HTML body, attribute, JS string, URL, CSS. Use canary-first probing (`aaaaabbbb<cccc>ddddd`) to observe where and how input reflects — never guess the context.
17. Analyze what the filter actually does: which characters are stripped, encoded, or rejected? Read the sanitizer function in the bundle (DOMPurify configs, custom regexes, `.replace()` chains). Document the filter rules verbatim — this is the evidence the payload must respect.
18. Craft the MINIMAL payload for that context only: the shortest string that escapes this filter in this context. One payload per context, not a spray list. If the filter neutralizes everything — NEGATIVE for this sink, document the filter that killed it.
19. Verify live against <TARGET>: BASELINE (known-dead path, record 404 shape) → PROBE (trigger the gadget chain with the canary payload) → VERIFY (second independent reproduction with a different canary). Only 2x-reproduced, baseline-differentiated results become CONFIRMED.
20. Save every raw request/response pair to <WORKDIR>/raw/gadget_<sinkid>_probeN.txt. No saved pairs = no CONFIRMED verdict. Secrets encountered during tracing are redacted in reports and never live-tested without explicit user approval.

## Step 6 – Exact commands

Baseline — record the known-dead path shape (do this once per session):
```bash
curl -sk -o /tmp/baseline.txt -w "HTTP %{http_code} | %{size_download} bytes\n" \
  "https://<TARGET>/this-path-probably-does-not-exist-xyz123"
head -c 400 /tmp/baseline.txt
```

First-pass sink map (verified CLI):
```bash
cd 02_js_analyze/bin && python3 gadget_mapper.py --help   # verify flags first if unsure
python3 gadget_mapper.py <WORKDIR>/normalized -o <WORKDIR>/gadgets_raw.json
python3 -c "import json; d=json.load(open('<WORKDIR>/gadgets_raw.json')); \
  print(len(d)); [print(x['sink'], x['file'], x['line']) for x in d[:40]]"
```

Probe — URL inventory that may feed sinks/sources (verified jsluice usage):
```bash
find <WORKDIR>/normalized -name '*.js' | jsluice urls | jq -r '.url' | sort -u > <WORKDIR>/raw/jsluice_urls.txt
```

Verify — trigger the gadget chain twice with different canaries, then compare against baseline:
```bash
# Example: hash-fed innerHTML gadget; replace with the actual chain's trigger
curl -sk -o /tmp/probe1.txt -w "HTTP %{http_code} | %{size_download} bytes\n" \
  "https://<TARGET>/app#canaryAAABBB<svg>"
curl -sk -o /tmp/probe2.txt -w "HTTP %{http_code} | %{size_download} bytes\n" \
  "https://<TARGET>/app#canaryXXXYYY<img>"
diff /tmp/baseline.txt /tmp/probe1.txt && echo "NO-DIFF-VS-BASELINE"
cp /tmp/probe1.txt /tmp/probe2.txt <WORKDIR>/raw/ 2>/dev/null; true
# then rename the copies: gadget_<sinkid>_probe1.txt, gadget_<sinkid>_probe2.txt
```

postMessage-gadget trigger harness (save, then open in the live browser against <TARGET>):
```html
<!-- /tmp/pm_trigger.html — replace origin, payload, and expected sink behavior -->
<script>
const w = window.open("https://<TARGET>/vulnerable-page", "_blank");
setTimeout(() => w.postMessage({canary: "PMCANARY1", data: "INJECT"}, "https://<TARGET>"), 2000);
</script>
```
```bash
# Repeat with a second canary (PMCANARY2) for the 2x rule; screenshot/record both runs.
# Check the listener's origin validation in the bundle FIRST: no `e.origin` check = lead;
# strict `e.origin === location.origin` = likely NEGATIVE unless you find a gadget that
# forges the origin (e.g. a subdomain you control posting to the page).
```

## Step 7 – Completion checklist

- [ ] gadget_mapper.py ran over normalized/ → <WORKDIR>/gadgets_raw.json exists
- [ ] Sink classes inventoried (code-exec > HTML > navigation > postMessage), vendor copies marked
- [ ] DOM-clobbering sources recorded alongside sinks
- [ ] Ranked triage list written to <WORKDIR>/gadgets_triage.md
- [ ] Reachability triage done: dead-code / auth-gated sinks marked NEGATIVE or BLOCKED
- [ ] Dynamic-argument check passed for every survivor (static strings → NEGATIVE)
- [ ] Backward source trace completed for every survivor; no-trace sinks stay CANDIDATE
- [ ] Gadget chains (source → sink → trigger) built for traced pairs
- [ ] Filter analysis per context done; minimal payloads crafted, canary-first
- [ ] Live verification: baseline + 2x repro, raw pairs saved to <WORKDIR>/raw/gadget_<sinkid>_probeN.txt
- [ ] postMessage listeners checked for origin validation; no-check listeners tested with the trigger harness
- [ ] Every CONFIRMED item's payload is the MINIMAL one for its context (no spray-and-pray lists in the evidence)
- [ ] No secret encountered during tracing was live-tested; all redacted in the triage notes
- [ ] gadgets.json verdict field reviewed record-by-record: no CANDIDATE promoted without 2x live repro
- [ ] Triage notes record the exact filter/sanitizer that killed each NEGATIVE sink (for the audit trail)
- [ ] Final verdicts recorded: CONFIRMED / INCONCLUSIVE / NEGATIVE / BLOCKED

### Review

A reviewer must verify: (a) every CONFIRMED item has two independent reproductions with different canaries saved as raw pairs on disk; (b) every sink without a traced attacker-controllable source is still CANDIDATE or lower, never CONFIRMED; (c) vendor/framework sink copies are marked `vendor: true` and none were claimed as app findings; (d) NEGATIVE/BLOCKED items carry a one-line reason; (e) the baseline dead-path shape was recorded before the first probe and every verdict references it. *Which sink has the shortest source→sink path — and is that path reachable without logging in?* *For your top chain: what does the filter actually strip, verbatim — and does your minimal payload survive it?* *Did any gadget require credentials? If yes, is it BLOCKED-documented or falsely CONFIRMED?* "Done" = <WORKDIR>/gadgets.json exists with every record carrying a verdict field, and no record was promoted to CONFIRMED without two saved raw reproduction pairs.

## Step 8 – Evidence standard (no false positives)

Every claim is measured against the known-dead baseline path on the same host: a probe result identical to the baseline is NEGATIVE, period. CONFIRMED requires baseline differentiation PLUS two independent reproductions with different canaries PLUS raw request/response pairs saved to <WORKDIR>/raw/. A single reproduction is INCONCLUSIVE. Static-only findings (sink + source traced in code, not yet executed live) are CANDIDATE — valuable leads, never reported as vulnerabilities. Auth walls you cannot cross are BLOCKED (document the wall and what credential would unlock it; never fabricate the other side). Secrets met in the JS are redacted in all reports and never live-tested without explicit user approval.

One more hard rule: a payload that "works" in your head but was never executed against <TARGET> is worth nothing — delete it from the CONFIRMED column and re-file it as CANDIDATE with the exact reproduction steps the next run needs. The gadgets.json verdict field is a legal document for the rest of the pipeline; every downstream skill trusts it blindly.

## Step 9 – Finished artifact & handoff

Finished artifact: `<WORKDIR>/gadgets.json` — one JSON array; each record has `file, line, sink, sink_class, source, chain (source → sink → trigger), context_snippet, filter_notes, payload, verdict (CANDIDATE|INCONCLUSIVE|CONFIRMED|NEGATIVE|BLOCKED), evidence_files[]`.

Sink-class quick reference for the verdict column (use verbatim):

- `code-exec`: eval, new Function, string setTimeout/setInterval — highest priority chains.
- `html-sink`: innerHTML, outerHTML, insertAdjacentHTML, document.write, jQuery .html()/.append(), dangerouslySetInnerHTML, v-html, ng-bind-html.
- `nav-sink`: location.href/assign/replace — open-redirect and javascript: URL leads.
- `msg-sink`: postMessage listeners — impact lives or dies on the origin check; always record the check verbatim.
- `clobber-source`: named elements, window.name, location.hash/search, document.referrer — usually the source half of a chain, not a sink.

Handoff: the **feature_map** skill fires this output next — it consumes the gadget chains (CONFIRMED + high-value CANDIDATE) as hunt leads and plans their escalation paths (e.g. HTML-sink + admin session = stored XSS writeup research). **report_output** consumes CONFIRMED items only, with the saved raw pairs as evidence. When handing off, flag the single highest-impact CONFIRMED chain first — the next skill should never have to re-rank your output.
