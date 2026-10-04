---
name: secrets-analysis
description: >
  Two-engine secrets scanner for <TARGET> JS bundles: known-regex patterns plus Shannon entropy, with everything labeled CANDIDATE until format-valid and context-suspicious. USE THIS SKILL whenever the user wants to scan bundles for leaked API keys, tokens, or credentials. Trigger on: "scan JS for secrets", "find API keys in the bundle", "entropy scan". This skill produces the redacted ammunition – the report_output fires it.
---

# Secrets Analysis

You are operating as the world's best bug bounty hunter and red teamer. Your job is to find leaked secrets in the target's JS bundles that generic scanners drown in false positives — two independent engines, ruthless candidate labeling, and zero live-testing without explicit user approval.

## Step 1 – Gather inputs
1. Read `<WORKDIR>/inventory_final.json` to know which normalized bundles exist and their line counts (large vendor bundles need pattern-priority ordering so you don't scan 200k lines of React before the app's own code).
2. List `<WORKDIR>/normalized/*.js` — these are the scan targets (never scan raw/ un-normalized bundles; minification noise and duplicates inflate entropy noise).
3. Check `<WORKDIR>/sourcemaps/` — if sourcemaps exist, prefer the original sources they expose; secrets in un-minified source have cleaner variable-name context.
4. Note the target's auth model (from stack fingerprint): does the app actually call a backend directly from JS? A `sk_live_` in a pure-static SPA's config object is a different animal than one in an API client's header builder.
5. Confirm the workhorse exists: `02_js_analyze/bin/secrets_scan.py`. If missing, write it per Step 6 before scanning.
6. Create a secure working dir: `mkdir -p <WORKDIR>/secrets_work && chmod 700 <WORKDIR>/secrets_work` — full secret values live here only, never in shared reports.

## Step 2 – Run ENGINE 1 (known-regex patterns)
7. Run the scan: `python3 secrets_scan.py <WORKDIR>/normalized -o <WORKDIR>/secrets_candidates.json`.
8. Verify every hit matches one of the verified patterns below — invent no new regexes without documenting them:
   - AWS access key: `AKIA[0-9A-Z]{16}`; AWS secret: 40-char `[A-Za-z0-9/+=]` adjacent to `aws_secret`/`aws-secret`
   - GitHub: `ghp_`, `gho_`, `ghu_`, `github_pat_`
   - GitLab: `glpat-`
   - Slack: `xox[baprs]-`; Slack webhooks: `hooks.slack.com/services/`
   - Stripe: `sk_live_`, `rk_live_`, `pk_live_`, `whsec_`
   - Google: `AIza[0-9A-Za-z_-]{35}`
   - Twilio: `AC[a-f0-9]{32}`, `SK[a-f0-9]{32}`
   - SendGrid: `SG\.[A-Za-z0-9_-]{22}`
   - JWT: `eyJ[A-Za-z0-9_-]+\.eyJ`
   - Private keys: `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
   - Generic: assignments to `api_key`, `apikey`, `token`, `secret`, `passwd`, `password`, `client_secret`
   - Database URLs: `postgres://`, `mongodb://`, `mysql://` with embedded `user:pass@` credentials
9. For each ENGINE 1 hit, pull ±3 lines of context: is it assigned to a key-named variable, does it carry a real service prefix, is it referenced in a network call? All three present → CANDIDATE.

## Step 3 – Run ENGINE 2 (Shannon entropy)
10. The scanner extracts all string literals ≥ 20 chars from each bundle.
11. Compute entropy per literal: `H = -sum(p * log2(p))` over the character distribution of the string.
12. Flag literals with H ≥ 4.5 bits/char as entropy candidates.
13. Exclude before flagging: dictionary words (check against a small wordlist), common tokens (`undefined`, `application/json`), and hashes of known libraries (bundle integrity hashes like `sha384-...` are everywhere).
14. If X do Y: a high-entropy literal assigned to `headers['Authorization']` → CANDIDATE with pattern_name `entropy_auth_header`; if Z pivot: a high-entropy literal that is exactly 32/40/64 hex chars in a `crypto.subtle.digest` call → likely a test fixture, mark NEGATIVE with reason `sha-fingerprint-of-known-lib`.

## Step 4 – Candidate labeling (format + context, both required)
15. CANDIDATE requires BOTH: format-valid (matches a real service's shape/length/charset) AND suspicious context (key-named variable, real service prefix, or used in a network call).
16. If the hit contains "example", "test", "xxx", "changeme", "placeholder", "dummy", or sits in a test-fixture/mock/fixture directory context → NEGATIVE with the reason recorded.
17. If format-valid but context is a config comment, dead code, or a docs string → INCONCLUSIVE, with the exact ambiguity noted (e.g. "matches ghp_ shape but inside a JSDoc example block").
18. If a hit is inside a vendored third-party library (check inventory_final.json's vendor tagging) and matches a generic pattern → INCONCLUSIVE with reason `vendor-lib-generic-match`; vendor libs are notorious for `secret` placeholder keys.
19. Every verdict lands in `secrets_candidates.json` as `{file, line, type: "regex"|"entropy", pattern_name, value_redacted, verdict}` — verdict is exactly one of CANDIDATE / INCONCLUSIVE / NEGATIVE.

## Step 5 – Handle secrets without live-testing
20. HARD RULE: never send a live request using a candidate secret without explicit user approval — no "harmless check", no `curl` with the key, no decoding a JWT against a real endpoint.
21. For each CANDIDATE, write the exact approval ask to send: `"I found a candidate <service> key in <file>:<line>; may I send one harmless read-only validation request? Reply yes/no"`.
22. If the user approves, the validation must be read-only, single-request, and logged with the raw pair saved to disk per the evidence standard — then the verdict upgrades to CONFIRMED or NEGATIVE.
23. If the user does not approve (or is silent), the verdict stays CANDIDATE and the handoff notes it as pending-approval. Blocked = BLOCKED, never fabricated.
24. Redaction everywhere: reports show the first 4 chars + `…(len N)`; full values exist only in the local JSON, which is `chmod 600`.

## Step 6 – Exact commands
```bash
# BASELINE: scan a known-clean vendor bundle first to calibrate noise
python3 02_js_analyze/bin/secrets_scan.py <WORKDIR>/normalized/react-dom.vendor.js -o /tmp/baseline_secrets.json
jq -r '.[] | [.verdict, .pattern_name] | @tsv' /tmp/baseline_secrets.json | sort | uniq -c

# PROBE: full two-engine scan over normalized bundles
mkdir -p <WORKDIR>/secrets_work && chmod 700 <WORKDIR>/secrets_work
python3 02_js_analyze/bin/secrets_scan.py <WORKDIR>/normalized -o <WORKDIR>/secrets_candidates.json
chmod 600 <WORKDIR>/secrets_candidates.json

# Summarize verdicts (redacted — full values never printed)
jq -r '.[] | [.verdict, .type, .pattern_name, .file] | @tsv' <WORKDIR>/secrets_candidates.json | sort | uniq -c | sort -rn

# VERIFY: pull context for one CANDIDATE before labeling
jq -r 'select(.verdict=="CANDIDATE") | "\(.file):\(.line)"' <WORKDIR>/secrets_candidates.json | head -5 | \
  while IFS=: read f l; do echo "=== $f:$l ==="; sed -n "$((l-3)),$((l+3))p" "<WORKDIR>/normalized/$f"; done
```

`secrets_scan.py` core (stdlib only, place at `02_js_analyze/bin/secrets_scan.py`):
```python
#!/usr/bin/env python3
"""Two-engine secrets scanner: regex patterns + Shannon entropy. stdlib only."""
import sys, os, re, json, math, argparse

PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret": r"(?i)(aws_secret|aws-secret)\W{0,5}[A-Za-z0-9/+=]{40}",
    "github_token": r"(ghp_|gho_|ghu_|github_pat_)[A-Za-z0-9_]{20,}",
    "gitlab_token": r"glpat-[A-Za-z0-9_\-]{20,}",
    "slack_token": r"xox[baprs]-[A-Za-z0-9\-]{10,}",
    "slack_webhook": r"hooks\.slack\.com/services/[A-Z0-9/_-]{20,}",
    "stripe_key": r"(sk_live_|rk_live_|pk_live_|whsec_)[A-Za-z0-9_\-]{16,}",
    "google_api_key": r"AIza[0-9A-Za-z_-]{35}",
    "twilio_sid": r"AC[a-f0-9]{32}",
    "twilio_key": r"SK[a-f0-9]{32}",
    "sendgrid_key": r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{40,}",
    "jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*",
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "generic_assignment": r"(?i)(api_key|apikey|client_secret|passwd|password)\W{0,3}[:=]\W{0,3}['\"][^'\"]{8,}['\"]",
    "db_url": r"(?i)(postgres|mongodb|mysql)://[^:/?#\s]+:[^@/?#\s]+@[^/?#\s]+",
}
NEGATIVE_HINTS = ("example", "test", "xxx", "changeme", "placeholder", "dummy", "mock", "fixture")
STRING_RE = re.compile(r"""(['"`])((?:\\.|(?!\1).){20,}?)\1""")

def entropy(s):
    if not s: return 0.0
    freq = {}
    for c in s: freq[c] = freq.get(c, 0) + 1
    return -sum((n / len(s)) * math.log2(n / len(s)) for n in freq.values())

def redact(v): return v[:4] + f"…(len {len(v)})" if len(v) > 8 else "…(len %d)" % len(v)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("js_dir"); ap.add_argument("-o", required=True)
    a = ap.parse_args(); out = []
    for root, _, files in os.walk(a.js_dir):
        for fn in sorted(files):
            if not fn.endswith(".js"): continue
            path = os.path.join(root, fn)
            try: src = open(path, encoding="utf-8", errors="ignore").read()
            except OSError: continue
            for i, line in enumerate(src.splitlines(), 1):
                for name, pat in PATTERNS.items():
                    for m in re.finditer(pat, line):
                        v = m.group(0)
                        verdict = "NEGATIVE" if any(h in line.lower() for h in NEGATIVE_HINTS) else "CANDIDATE"
                        out.append({"file": fn, "line": i, "type": "regex", "pattern_name": name,
                                    "value_redacted": redact(v),
                                    "verdict": verdict if verdict == "NEGATIVE" else "CANDIDATE",
                                    "reason": "placeholder/test hint in line" if verdict == "NEGATIVE" else "format-valid; context review pending"})
                for m in STRING_RE.finditer(line):
                    s = m.group(2)
                    if len(s) >= 20 and entropy(s) >= 4.5 and not any(h in s.lower() for h in NEGATIVE_HINTS):
                        if re.fullmatch(r"[a-z]+", s.lower()) and len(s) < 30: continue
                        out.append({"file": fn, "line": i, "type": "entropy", "pattern_name": "high_entropy_literal",
                                    "value_redacted": redact(s), "verdict": "INCONCLUSIVE",
                                    "reason": f"entropy {entropy(s):.2f} bits/char; context review pending"})
    json.dump(out, open(a.o, "w"), indent=2)
    print(f"wrote {len(out)} findings -> {a.o}")

if __name__ == "__main__": main()
```

## Step 7 – Completion checklist
- [ ] `<WORKDIR>/inventory_final.json` read; scan order prioritized (app code before vendor libs)
- [ ] `02_js_analyze/bin/secrets_scan.py` present and executable
- [ ] Baseline scan of a known-clean vendor bundle run; noise level recorded
- [ ] ENGINE 1 (regex) run across `<WORKDIR>/normalized/`; hits have ±3-line context pulled
- [ ] ENGINE 2 (entropy) run; dictionary words, common tokens, and known-lib hashes excluded
- [ ] Every finding labeled CANDIDATE / INCONCLUSIVE / NEGATIVE with a reason string
- [ ] `<WORKDIR>/secrets_candidates.json` written, `chmod 600`
- [ ] No secret live-tested; approval asks drafted for each CANDIDATE

### Review
A reviewer must verify: (1) every CANDIDATE shows format-validity AND suspicious context in the recorded reason — context-free regex hits are INCONCLUSIVE at best; (2) the NEGATIVE list actually contains the test/example/xxx hits with reasons, proving the negative-hint filter ran; (3) `secrets_candidates.json` is `chmod 600` and no report anywhere on disk contains a full secret value; (4) zero outbound requests were made with any candidate value.
*Did any CANDIDATE come from a vendored third-party lib — and if so, is the verdict INCONCLUSIVE rather than CANDIDATE?*
*For each CANDIDATE, what is the exact network call it feeds — is the secret actually reachable unauthenticated in the app's flow?*

"Done" = `<WORKDIR>/secrets_candidates.json` exists on disk at that exact path, `chmod 600`, every finding carries a verdict and a reason, and no full secret value appears outside it.

## Step 8 – Evidence standard (no false positives)
- Baseline: every scan run includes the known-clean vendor bundle baseline so pattern noise is quantified, not assumed.
- 2x reproduction: a CANDIDATE is only promoted to CONFIRMED after an approved, read-only validation request succeeds twice with identical results; raw request/response pairs for both runs are saved to `<WORKDIR>/secrets_work/verify_<pattern>_<line>.txt`.
- Static = CANDIDATE: nothing in this skill is CONFIRMED by static analysis alone — a regex match is a candidate, not a finding.
- Blocked = BLOCKED: if the user does not approve validation, the verdict stays CANDIDATE with `reason: "pending user approval"` — never upgraded on assumption.
- Verdicts are exactly CONFIRMED / INCONCLUSIVE / NEGATIVE (plus CANDIDATE for the pre-verification state); secrets are never live-tested without the explicit yes/no approval above.
- Redaction: reports show `first4…(len N)`; full values live only in the local `chmod 600` JSON.

## Step 9 – Finished artifact & handoff
- Finished artifact: `<WORKDIR>/secrets_candidates.json` — JSON array of `{file, line, type: "regex"|"entropy", pattern_name, value_redacted, verdict, reason}`.
- Handoff: `report_output` consumes this next. It gets a REDACTED table only — columns `file:line`, `pattern_name`, `value_redacted`, `verdict`, `reason`. Full values never leave the local JSON; the handoff must state the exact `chmod 600` path and the count of CANDIDATEs pending user approval.
- Also cross-feed: any CANDIDATE secret that appears in a network call feeds `api_analysis` as an auth-material lead (name the header/param and the call site, redacted).
