---
name: generic-routes
description: >
  Discovers admin panels, management consoles, and framework-default routes through per-host 404-baseline calibration plus JS-derived custom admin-path guessing. USE THIS SKILL whenever the user wants to find hidden admin panels, management consoles, or framework default routes on a target. Trigger on: "find admin panels", "discover admin routes", "check for actuator", "wp-admin discovery", "route discovery", "admin panel hunting". This skill produces the verified route inventory – the api-discovery skill fires the next round by mounting method enumeration and spec probes on every confirmed route.
---

# Generic Routes Discovery

You are operating as the world's best bug bounty hunter and red teamer. Your job is to find the admin panels, management consoles, and framework-default routes that generic scanners miss — the forgotten `/actuator`, the custom `/internal-console` hinted at in a JS bundle, the `/manager/html` nobody remembered to delete. A "hit" counts only when it diverges from the host's own 404 baseline. Status codes alone are lies; divergence is truth.

## Step 1 – Gather Inputs

Collect everything before a single probe goes out:
- `<TARGET>` base URL (scheme + host). One skill run = one host. Never batch two hosts into one baseline.
- `02_js_analyze/routes_params.md` — JS-observed route hints, admin-ish strings, feature flags.
- `02_js_analyze/tech_choices.md` — framework identity (Django, Spring, WordPress, Laravel, Rails, Next.js…). If it's missing or inconclusive, you run the generic battery only — never guess the stack from vibes.
- A scratch note of the host's purpose (admin SPA? API gateway? marketing site?). A pure static marketing page with no app surface and no JS route hints is a time-pass target for this skill — say so and stop.

Division of labor: this skill consumes the three inputs above and produces
`discovery/generic_routes.txt` (verified hits only), `discovery/generic_routes_raw.md`
(full probe table with raw pairs + negative log), and `discovery/baseline.txt`
(the host's 404 baseline record). Skip this skill when a previous run's
`generic_routes_raw.md` already covers the same battery on the same host — re-running
dead paths is not work, and when the host is WAF-walled (every probe returns the
identical block page) log BLOCKED and move to `api-discovery` instead of burning
the battery against a wall.

## Step 2 – Calibrate the 404 Baseline (Mandatory, First)

No probes before this. Request 3 random dead paths (e.g. `/levi-dead-<rand1>`,
`/levi-dead-<rand2>.html`, `/levi/dead/<rand3>`) with plain GET. For each record:
status code, response size in bytes, word count, SHA1 of the body. The baseline =
the median behavior. Write it to `discovery/baseline.txt`. If any later step skips
baseline comparison, the run is invalid — full stop.

## Step 3 – Classify the Baseline Shape

- **Classic 404** (404, small stable body): easy mode — status + size both signal.
- **SPA fallback / wildcard** (200, identical body for all 3 dead paths): switch to
  **content-diff detection**. A hit = body hash differs from baseline hash. Status
  200 means nothing on these hosts — this is where most scanners hallucinate hits.
- **WAF/deny page** (403/identical body, or identical block page on everything):
  write `discovery/block_note.md`, probe only ~20 high-signal paths, and if all
  return the identical block page, mark the run BLOCKED and stop.

Re-verify the baseline mid-run if responses suddenly shift (all 500s, all 429s):
re-run the 3 dead paths. If the baseline moved, every classification so far is void —
recalibrate and re-run, and note the incident in `discovery/phase_log.md`.

## Step 4 – Build the Candidate Battery

**Framework defaults** (driven by `tech_choices.md`, never by vibes):
- Django: `/admin`, `/admin/login/`, `/static/admin/`
- Spring Boot: `/actuator`, `/actuator/health`, `/actuator/env`, `/actuator/heapdump`
- WordPress: `/wp-admin`, `/wp-login.php`, `/wp-json/wp/v2/`, `/xmlrpc.php`
- Tomcat/JBoss: `/manager/html`, `/manager/status`, `/jmx-console`
- Laravel: `/admin`, `/nova`, `/telescope`, `/horizon`
- Rails: `/admin`, `/rails/info`, `/sidekiq`
- Next.js/Nuxt: `/_next/`, `/api/`, `/__nuxt`
- Generic (always included): `/admin`, `/administrator`, `/login`, `/console`,
  `/manage`, `/manager`, `/panel`, `/cms`, `/backend`, `/internal`, `/ops`,
  `/portal`, `/dashboard`, `/api/docs`, `/api/redoc`, `/swagger`, `/swagger-ui`,
  `/graphql`, `/graphiql`, `/playground`, `/.well-known/change-password`

**Custom admin-path guesses from `routes_params.md`:** every admin-ish token becomes
a candidate. Token `internalConsole` → `/internal-console`, `/internal_console`,
`/internalconsole`, `/internal/console`. Token `opsPortal` → `/ops`, `/ops-portal`,
`/portal/ops`. Document every guess's source token in the raw log — no orphan guesses.
A guess you can't trace to a token is a guess you didn't make.

## Step 5 – Probe Every Candidate with a Plain GET

One request per path, ~1s delay between requests on targets without a stated rate
policy. Plain GET — no exotic headers, no method tricks. Those belong to the
403-bypass playbook, not to discovery. For each response capture: status, size in
bytes, body SHA1, and the `<title>` tag (first match). Log everything to the raw table.

## Step 6 – Classify by Baseline Divergence

A path is a CANDIDATE only if at least one holds: status differs from baseline
status, size differs by >10% from baseline size, or body SHA1 differs from baseline
SHA1 (on SPA-fallback hosts this is the ONLY signal). Status 200 alone means nothing
on an SPA host. A path matching baseline is NEGATIVE — logged so nobody re-tests it.

## Step 7 – Understand Every Candidate

Read the body (title tag, first 200 bytes, JSON keys if JSON). Hunt for: login forms,
"admin"/"console"/"dashboard" markers, stack traces, directory listings, GraphQL
explorer UI, actuator JSON (`{"status":"UP"}`), heapdump content-type
(`application/octet-stream`). Trap check: a CANDIDATE whose body is the main app's
login page (same title as `/`) is the SPA fallback wearing a costume — compare the
title to `/` before celebrating. Downgrade costume hits to NEGATIVE with a note.

## Step 8 – Reproduce Twice

Re-request each surviving CANDIDATE 2 more times on separate connections, ~60s
apart. Flaky CDN behavior and one-off 500s are not findings. If it doesn't reproduce
2× with matching status + size + hash, verdict = INCONCLUSIVE and the flakiness is
documented — not promoted.

## Step 9 – Save Raw Pairs and the Negative Log

For every CONFIRMED route, append the raw request/response (headers + first 2KB of
body) to `discovery/generic_routes_raw.md` under its heading. Raw pairs are the
evidence; the `.txt` is the index. Every NEGATIVE path goes into the same file as a
one-line `NEGATIVE <path> <status> <size>` entry — this is what stops the next run,
or the next agent, from re-probing dead paths.

## Step 10 – Handle Auth-Gated Panels and Slash Variants

A 200 login form at `/admin` is CONFIRMED as *existing* — the finding is "admin panel
exists; unauthenticated surface = login form only." Never claim "admin access found"
from a login page. Note default-credential risk as a follow-up lead, not a finding.
Then test trailing-slash and case variants of CONFIRMED routes only (`/admin` vs
`/admin/` vs `/ADMIN`) — servers that normalize differently sometimes expose
different handlers. Do this only for confirmed hits, never for the whole battery.
Do NOT spider into authenticated areas or submit credentials; discovery maps the
unauthenticated surface.

## Step 11 – Exact Commands (Copy-Paste)

```bash
# 0. One host per run
TARGET="https://target.example.com"

# 1. BASELINE — 3 random dead paths
for p in "levi-dead-$RANDOM" "levi-dead-$RANDOM.html" "levi/dead/$RANDOM"; do
  echo "== /$p =="
  curl -sk -o /tmp/base_body -w "status=%{http_code} size=%{size_download}\n" \
    "$TARGET/$p"
  echo "sha1=$(sha1sum /tmp/base_body | cut -d' ' -f1) words=$(wc -w < /tmp/base_body)"
done
# Eyeball the 3 runs, write medians into discovery/baseline.txt.

# 2. Candidate battery (edit: add framework defaults + JS-derived guesses)
cat > /tmp/route_candidates.txt <<'EOF'
admin
administrator
wp-admin
wp-login.php
manager/html
manager/status
actuator
actuator/health
actuator/env
graphql
graphiql
api/docs
swagger-ui
console
manage
panel
cms
backend
internal
ops
portal
nova
telescope
horizon
rails/info
sidekiq
EOF
while read -r r; do
  code=$(curl -sk -o /tmp/probe_body -w "%{http_code}" --max-time 20 "$TARGET/$r")
  size=$(wc -c < /tmp/probe_body); hash=$(sha1sum /tmp/probe_body | cut -d' ' -f1)
  title=$(grep -oi '<title>[^<]*' /tmp/probe_body | head -1)
  echo "$r -> $code size=$size sha1=$hash $title"
  sleep 1
done < /tmp/route_candidates.txt | tee /tmp/route_probe.log

# 3. Reproduce a candidate 2x (replace CANDIDATE)
for i in 1 2; do
  curl -sk -D /tmp/rep_hdr -o /tmp/rep_body --max-time 20 "$TARGET/CANDIDATE"
  echo "run$i: $(head -1 /tmp/rep_hdr | tr -d '\r') size=$(wc -c < /tmp/rep_body) sha1=$(sha1sum /tmp/rep_body | cut -d' ' -f1)"
  sleep 60
done

# 4. ffuf micro-pass over the same battery with auto-calibration (see ffuf-workflow)
ffuf -u "$TARGET/FUZZ" -w /tmp/route_candidates.txt -ac -t 20 -rate 20 \
  -o discovery/ffuf_routes.json -of json
```

## Step 12 – Completion Checklist

Tick every box. No skipping, no "looks done":
- [ ] `discovery/baseline.txt` exists with status/size/words/sha1 of 3 dead paths
- [ ] Baseline shape classified (classic 404 / SPA-fallback / WAF-block) and recorded
- [ ] Framework-default battery chosen from `tech_choices.md` (or generic set, with the reason documented)
- [ ] Every JS-derived custom guess traces to a source token in `routes_params.md`
- [ ] Every candidate probed with plain GET, ~1s spacing, no exotic headers
- [ ] Every CANDIDATE judged by baseline divergence, not status alone
- [ ] Every CANDIDATE understood (title/marker/JSON keys noted; SPA-costume trap checked)
- [ ] Every CONFIRMED route reproduced 2× with matching status + size + hash
- [ ] Raw request/response pairs saved in `discovery/generic_routes_raw.md`
- [ ] NEGATIVE paths logged so they are never re-probed
- [ ] `discovery/generic_routes.txt` written in the exact finished-artifact format
- [ ] Review: re-run the baseline command, spot-check 3 CONFIRMED routes with plain
      curl, confirm each diverges from baseline in the raw log. Any "confirmed" route
      that matches baseline on re-check fails the whole run.
- Nudge prompts (say these before declaring done):
  - "Did you calibrate the baseline FIRST, or did you start probing and promise yourself you'd compare later?"
  - "That 200 on /admin — is the title the same as the homepage? Then it's the SPA fallback, not a panel."
  - "If you stopped because the first 30 paths were dead, the panel is at path 31. Finish the battery."

## Step 13 – Evidence Standard (No False Positives)

- Baseline comparison vs a known-dead path on the SAME host is mandatory. A hit with
  no baseline record is INCONCLUSIVE by default — no exceptions.
- **CONFIRMED** = baseline divergence + 2× reproduction + raw pair saved.
- **INCONCLUSIVE** = diverges once but flaky, or the WAF interfered mid-run.
- **NEGATIVE** = matches baseline on first probe. Logged, never re-tested without a reason.
- **BLOCKED** = host returned the block page or rate-limited the run; documented in
  `discovery/block_note.md` with the observed behavior — not silently skipped.
- Static findings (a path seen in JS but never probed) stay CANDIDATE and do NOT
  enter `generic_routes.txt`. Chat summaries are not evidence; raw pairs are.

## Step 14 – Finished Artifact & Handoff

Done = `discovery/generic_routes.txt` exists, every line matches
`CONFIRMED <path> <status> <size_bytes> <title_or_marker>` — or the single line
`NONE <host> <date> baseline=<status>/<size>` when zero routes confirmed (an empty
file is ambiguous; a `NONE` line is a completed run). `discovery/generic_routes_raw.md`
holds the full probe table with raw pairs for hits.

Handoff: **api-discovery** consumes `generic_routes.txt` — every CONFIRMED admin/API-ish
route gets method enumeration and `/swagger`, `/openapi.json`, `/graphql` probes mounted
on it. **app-specific-files** consumes the framework signal: a CONFIRMED `/wp-admin` or
`/actuator` hard-confirms the stack and focuses the tech-derived file battery.
**phases-generic-specific** consumes `generic_routes_raw.md` + `baseline.txt` to certify
the Generic phase exit gate. Interesting-but-auth-gated panels go to the follow-up
queue — default-credential and auth-bypass work is a different pipeline, not this skill.
