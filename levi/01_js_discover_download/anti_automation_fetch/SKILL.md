---
name: anti-automation-fetch
description: >
  Six-rung escalation ladder for WAF/bot-blocked targets: real-UA curl, HTTP/2 with ordered headers, webfetch-style requests, mitmproxy interception, Chrome DevTools MCP, then Puppeteer/Playwright real browser. USE THIS SKILL whenever fetches get blocked (403, captcha, empty bodies, TLS-fingerprint drops) or the user says "bypass the waf", "bot blocked", "can't fetch". Trigger on: "waf block", "bot detection", "403 on curl", "captcha block", "cloudflare block", "fetch is blocked", "anti-automation". This skill produces fetch_log.md with per-rung results – every other Phase-1 skill calls it when a block appears, and it never fabricates a result.
---

# Anti-Automation Fetch

You are operating as the world's best bug bounty hunter and red teamer. Your job is to GET THE BYTES when a target's bot defenses say no — climbing a disciplined escalation ladder, one rung at a time, and documenting every rung honestly. A fabricated fetch is the worst false positive in this pack: it poisons every downstream analysis.

## Step 1 – Gather Inputs

Collect everything before starting:

- **Consumes:** target URL(s) that failed (`<BLOCKED_URL>`), the failure evidence from the calling skill (HTTP code, response body sample, headers), the dead-path baseline for comparison.
- Output: append to `<RUN_DIR>/js_inventory/fetch_log.md` — one section per rung, every rung, pass or fail.
- Identify the blocker FIRST — the rung you start on depends on the diagnosis:
  - `403` + `cf-mitigated` / `challenge` headers → Cloudflare managed challenge (start rung 1, expect to climb fast)
  - `403` + `Server: awselb` / Akamai reference ID → Akamai/edge WAF (start rung 1)
  - Empty body + connection reset on curl but browser works → TLS fingerprinting (skip to rung 2/6)
  - `429` → rate limit, NOT a bot block: slow down, do NOT climb the ladder (climbing past a rate limit is rude and pointless)
  - CAPTCHA HTML → start rung 1, plan to reach rung 6

## Step 2 – Decide When to Use vs When to Skip

**USE when:** any Phase-1 fetch fails with a block signature (403 WAF page, challenge, captcha, TLS reset, empty body where a browser renders fine); the user explicitly asks to get past bot protection on an in-scope target.

**SKIP when (time-pass filter):**
- The failure is a 404 or DNS NXDOMAIN — that is not a block, it is an answer. Do not climb a ladder against a 404.
- The failure is a 429 rate limit — back off and retry slower. Escalating tools against a rate limit is time-pass at best, ban-worthy at worst.
- The target is out of scope — no ladder rung authorizes out-of-scope fetching. Ever.
- The user has not authorized interactive browser automation on this engagement and rung 6 is the only remaining option — document BLOCKED at rung 5 instead.

## Step 3 – Rung 1: curl With Real Browser UA, Headers, and Cookies

Most "blocks" are just missing headers. Send what a real browser sends:

```bash
curl -sS -D /tmp/r1_headers.txt -o /tmp/r1.body -w "%{http_code} %{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "Sec-Ch-Ua: \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\", \"Not-A.Brand\";v=\"99\"" \
  -H "Sec-Ch-Ua-Mobile: ?0" -H "Sec-Ch-Ua-Platform: \"Windows\"" \
  -H "Sec-Fetch-Dest: document" -H "Sec-Fetch-Mode: navigate" \
  -H "Sec-Fetch-Site: none" -H "Sec-Fetch-User: ?1" \
  -H "Upgrade-Insecure-Requests: 1" \
  --compressed "<BLOCKED_URL>"
head -c 500 /tmp/r1.body; echo; grep -iE '^(HTTP|server:|cf-mitigated|set-cookie)' /tmp/r1_headers.txt
```

**What a block looks like:** 403 with `cf-mitigated: challenge` (Cloudflare), a `Set-Cookie: _abck=` + 403 HTML (Akamai), or a captcha form in the first 500 bytes.
**Climb when:** the body is a challenge/captcha/WAF page instead of the expected content. **Stop here when:** you get the real content — verify by comparing against what the calling skill expected (JS content-type, non-baseline body).

## Step 4 – Rung 2: HTTP/2 With Browser Header Ordering

Some WAFs fingerprint HTTP/1.1 or curl's header order. Force HTTP/2 and order headers exactly as Chrome sends them:

```bash
curl -sS --http2 -D /tmp/r2_headers.txt -o /tmp/r2.body -w "%{http_code} %{http_version} %{size_download}\n" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  -H "sec-ch-ua: \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\", \"Not-A.Brand\";v=\"99\"" \
  -H "sec-ch-ua-mobile: ?0" \
  -H "sec-ch-ua-platform: \"Windows\"" \
  -H "upgrade-insecure-requests: 1" \
  -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "sec-fetch-site: none" -H "sec-fetch-mode: navigate" \
  -H "sec-fetch-user: ?1" -H "sec-fetch-dest: document" \
  -H "accept-encoding: gzip, deflate, br" -H "accept-language: en-US,en;q=0.9" \
  --compressed "<BLOCKED_URL>"
```

**What a block looks like:** same WAF page as rung 1, or `%{http_version}` showing `1.1` when you asked for 2 (middlebox downgrade — note it).
**Climb when:** identical block page. **Key check:** confirm `%{http_version}` is actually `2` — if curl silently fell back to 1.1, this rung never really ran; fix that before climbing.

## Step 5 – Rung 3: Webfetch-Style Request

The "webfetch" rung: a clean, single-shot document fetch through the MCP webfetch surface with browser-like headers — no curl TLS fingerprint at all:

```bash
# Concept: issue the fetch via the webfetch MCP tool (browser-grade TLS stack),
# headers mirrored from rung 1. Save the FULL response (headers + body) to /tmp/r3.*.
# If the MCP surface is unavailable in this run, say so in fetch_log.md and climb —
# do not simulate this rung with curl, that is rung 1 wearing a costume.
```

**What a block looks like:** challenge/captcha content returned to the webfetch caller, or a tool-level error naming bot protection.
**Climb when:** blocked content or an explicit automation error. **Honesty rule:** if you cannot actually invoke webfetch here, write `RUNG 3: NOT ATTEMPTED (no webfetch surface)` — a skipped rung documented beats a faked rung.

## Step 6 – Rung 4: Request Interception via mitmproxy

Route a REAL browser's traffic through mitmproxy so you capture the exact request bytes a genuine client sends — then replay the interesting ones:

```bash
# Terminal 1: start the proxy (real commands)
mitmproxy --listen-port 8080 --save-stream-file /tmp/r4_flows.mitm
# Terminal 2: point a real browser at it, visit <BLOCKED_URL> by hand (or via the user's live browser),
# then dump the captured flows:
mitmdump -r /tmp/r4_flows.mitm -n -v 2>&1 | grep -A5 "<TARGET_HOST>" | head -60
```

**What you are looking for:** the exact header set, cookie jar, and TLS behavior of a successful real-browser load. Replay the captured request with curl `--proxy http://127.0.0.1:8080` to confirm which headers were load-bearing.
**Climb when:** even the real browser through the proxy gets challenged — the block is behavioral/session-based, not fingerprint-based. **Stop when:** the intercepted real-browser request succeeds — you now have the working header/cookie set; hand it back to the calling skill.

## Step 7 – Rung 5: Chrome DevTools MCP

Drive a real Chromium via the Chrome DevTools MCP server — genuine rendering, genuine TLS, genuine JS execution:

```bash
# Requires the chrome-devtools-mcp server configured in this environment.
# Workflow: navigate to <BLOCKED_URL>, wait for network idle, then:
#   1. Read the rendered DOM (proves the challenge was passed or not)
#   2. Export the response bodies of the JS asset requests (Network domain)
#   3. Save each JS body to <RUN_DIR>/js_inventory/raw/ with its URL in the manifest
```

**What a block looks like:** the DOM shows a challenge/captcha page; the Network domain shows 403s on the asset requests.
**Climb when:** DevTools-driven Chromium is ALSO challenged — the defense is keying on automation signals (headless flags, `navigator.webdriver`).
**Document:** which DevTools calls you made and what the DOM actually showed. "It worked" without the DOM evidence is not a rung result.

## Step 8 – Rung 6: Puppeteer / Playwright Real Browser

The top rung: a full browser with stealth posture, real user profile, headed if possible:

```bash
npm ls puppeteer playwright 2>/dev/null || npm i -g puppeteer
node - <<'EOF'
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--disable-blink-features=AutomationControlled'] });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36');
  const jsBodies = {};
  page.on('response', async (res) => {
    const url = res.url();
    if (url.endsWith('.js') && res.ok()) jsBodies[url] = await res.text().catch(() => null);
  });
  await page.goto('<BLOCKED_URL>', { waitUntil: 'networkidle2', timeout: 60000 });
  console.log('title:', await page.title());
  console.log('js captured:', Object.keys(jsBodies).length);
  require('fs').writeFileSync('/tmp/r6_js.json', JSON.stringify(Object.keys(jsBodies)));
  await browser.close();
})().catch(e => { console.error('RUNG6-FAIL:', e.message); process.exit(1); });
EOF
```

**What a block looks like:** `RUNG6-FAIL` with timeout/navigation errors, or a captcha title.
**Iron rule:** if this rung fails, THE LADDER IS EXHAUSTED. Write `BLOCKED` in `fetch_log.md` (Step 9). There is no rung 7 in this skill — do not invent one.

## Step 9 – The Iron Rule: Document BLOCKED, Never Fabricate

If all attempted rungs fail, append EXACTLY this to `fetch_log.md`:

```markdown
## BLOCKED: <BLOCKED_URL>
- Date: <YYYY-MM-DD>
- Rungs attempted: 1 (curl+UA) FAIL [403 cf-mitigated] / 2 (http2) FAIL [same] / ...
- Highest rung reached: <N>
- Verdict: BLOCKED — no bytes fetched. Downstream skills must treat this URL's JS as UNKNOWN, not empty.
```

Then STOP. Do not: mark the file as harvested, invent bundle contents, copy a similar file from elsewhere, or let a downstream skill assume the inventory is complete. A BLOCKED entry is a successful run of this skill — honesty about the gap is the deliverable.

## Step 10 – Completion Checklist

Tick every box. "Done" = the finished artifact exists on disk at its exact path.

- [ ] Blocker diagnosed (WAF vendor / TLS fingerprint / rate limit / captcha) before choosing the start rung
- [ ] Rate-limit (429) cases handled by backoff, NOT by climbing
- [ ] Rung 1 attempted with full browser header set; result + block signature logged
- [ ] Rung 2 attempted with `--http2`; actual negotiated version verified in output
- [ ] Rung 3 attempted or honestly marked NOT ATTEMPTED with the reason
- [ ] Rung 4 attempted (mitmproxy capture) or marked not-applicable with reason
- [ ] Rung 5 attempted (DevTools MCP) or marked not-applicable with reason
- [ ] Rung 6 attempted (Puppeteer/Playwright) or skipped per authorization boundary with reason
- [ ] `fetch_log.md` has one section PER RUNG with command evidence or honest skip reason
- [ ] If all rungs failed: BLOCKED entry written in the exact format, downstream skills notified of the gap
- [ ] If any rung succeeded: the working header/cookie set handed back to the calling skill

**Nudge prompts:** "Did I verify the http version on rung 2, or assume it?" — "Is that rung-3 result real, or did I dress up rung 1?" — "If I am writing BLOCKED, did I actually exhaust the rungs or just get tired?"

## Step 11 – Evidence Standard (No False Positives)

- **Baseline:** rung success is judged against the calling skill's expectation (right content-type, body diverges from dead-path baseline), not against "got a 200". A 200 serving a challenge page is still a FAIL.
- **2x reproduction:** a rung that "works" must work twice in a row before the calling skill resumes on it — WAFs flake, and a flaky bypass is not a bypass.
- **Raw pairs saved:** every rung's response headers + first 500 body bytes live in `fetch_log.md`. A disputed rung gets re-judged from this log.
- **Verdicts:** per rung: SUCCESS (bytes match expectation, 2x) / FAIL (block signature observed) / NOT ATTEMPTED (reason documented). Per URL: FETCHED or BLOCKED. No other states exist.
- **Blocked = BLOCKED:** documented in the exact format, never upgraded to "probably fine", never fabricated.

## Step 12 – Finished Artifact & Handoff

**Finished artifact:** `<RUN_DIR>/js_inventory/fetch_log.md` — per-rung sections for every blocked URL, ending in either a working fetch configuration or a BLOCKED entry.

**Handoff:** the CALLING skill resumes with the working configuration (rung 1–6 winner) or proceeds with the documented gap — `spider-harvest` marks unharvested scripts as `fetch_failed: true` (not silently absent), `sourcemap-harvest` skips map probes for BLOCKED files, and review gate 1 explicitly asks "any BLOCKED entries?" so the gap is visible, not buried. This skill never hands off fabricated bytes — that is the whole point.
