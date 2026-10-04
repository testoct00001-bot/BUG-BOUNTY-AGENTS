---
name: generic-files
description: >
  Discovers exposed config files, backup artifacts, and version-control leftovers through baseline-calibrated probing and a response-intelligence table that separates real content from WAF block pages and SPA fallbacks. USE THIS SKILL whenever the user wants to find exposed .env files, .git directories, backup files, or config artifacts on a target. Trigger on: "find exposed config files", "backup file discovery", ".env exposed", ".git HEAD check", "config artifact hunting", "sensitive file discovery". This skill produces the verified exposed-file inventory – the app-specific-files skill fires next with the tech-derived file battery built on the same baseline discipline.
---

# Generic Files Discovery

You are operating as the world's best bug bounty hunter and red teamer. Your job is to find the files nobody meant to ship: `.env` with live credentials, `.git/HEAD` leaking the repo, `config.php.bak` sitting next to production code, `.DS_Store` mapping directories the spider never reached. These are not guesses — every file on your battery either diverges from the host's 404 baseline or it doesn't exist. A 200 that smells like a WAF block page gets verified, not celebrated.

## Step 1 – Gather Inputs

Collect before probing:
- `<TARGET>` base URL. One host per run, same baseline rules as `generic-routes`.
- `discovery/baseline.txt` — reuse the host's existing baseline if `generic-routes`
  already ran; if not, you calibrate it yourself in Step 2 (same procedure).
- `02_js_analyze/tech_choices.md` — optional here; the generic battery is
  stack-agnostic, but tech hints let you prioritize (a PHP stack makes `.php.bak`
  more interesting than `.env`? No — probe both, order PHP first).
- The response-intelligence table (Step 6) printed or memorized — you will classify
  every response through it.

Division of labor: consumes the baseline + target; produces
`discovery/generic_files.txt` (verified exposed files only),
`discovery/generic_files_raw.md` (full probe table, raw pairs, negative log).
Skip when the host already has a `generic_files_raw.md` covering the same battery,
or when the baseline is a WAF block page on every probe — log BLOCKED and move on.
Time-pass filter: a 200 `.css.map` with no secrets is not a win; the battery targets
files that leak credentials, source, or directory structure.

## Step 2 – Calibrate the 404 Baseline (Mandatory, First)

Same procedure as `generic-routes`: 3 random dead paths, record status/size/words/sha1,
write `discovery/baseline.txt` (reuse if fresh from a same-day run on the same host).
Additionally fetch one **known-extension dead path** (e.g. `/levi-dead-<rand>.env`) —
some servers return different baselines per extension (a static handler for `.env`
vs the app router for extensionless paths). If the two baselines differ, you now
have TWO baselines and every file probe is compared against the extension-matched one.
This is the trap that creates false `.env` hits: comparing an `.env` probe against
an extensionless baseline.

## Step 3 – Build the File Battery

Group by what they leak. Every entry is a literal path — no FUZZ yet, this is the
high-signal list:

**Environment & secrets:**
`.env`, `.env.local`, `.env.production`, `.env.bak`, `.env.old`, `.env~`,
`config.env`, `app.env`

**Version control:**
`.git/HEAD`, `.git/config`, `.git/logs/HEAD`, `.svn/entries`, `.hg/requires`,
`.bzr/README`

**Backups & editor droppings:**
`<app>.bak`, `<app>.old`, `<app>.orig`, `<app>.swp`, `<app>~`, `<app>.tmp`,
`backup.zip`, `backup.tar.gz`, `db.sql`, `dump.sql`, `site.sql`
(Probe both generic names AND app-named variants: `wp-config.php.bak`,
`config.php.bak`, `configuration.php~`, `settings.py.bak`, `appsettings.json.bak`)

**Framework/package manifests:**
`package.json`, `package-lock.json`, `composer.json`, `composer.lock`,
`Gemfile`, `Gemfile.lock`, `requirements.txt`, `pom.xml`, `web.config`,
`server.xml`, `.npmrc`, `yarn.lock`

**OS / editor artifacts:**
`.DS_Store`, `Thumbs.db`, `.idea/workspace.xml`, `.vscode/settings.json`

**Debug & info:**
`phpinfo.php`, `info.php`, `test.php`, `server-status`, `server-info`,
`robots.txt`, `sitemap.xml`, `.well-known/security.txt` (these last three are
recon, not findings — log them as INFO, not CONFIRMED wins)

Add JS-derived filenames: any config-ish token from `routes_params.md`
(`config`, `settings`, `secrets`, `credentials`, `dump`, `backup`) becomes
`/<token>.bak`, `/<token>.old`, `/<token>.json`, `/<token>.zip` candidates with
the source token documented.

## Step 4 – Probe with Extension-Aware Baseline Comparison

GET each path, ~1s spacing. Compare against the **extension-matched baseline**
from Step 2. A `.env` probe is compared to the `.env`-baseline, not the
extensionless one. Record status/size/sha1/content-type/title for every probe.
Content-type matters here: `text/plain` on `.git/HEAD` is a strong signal;
`text/html` with the SPA title is the fallback costume.

## Step 5 – Verify Content Is Real (Not a WAF Block Page)

This is where file discovery earns its no-FP bar. For every CANDIDATE:
1. Read the first 500 bytes. A real `.env` has `KEY=VALUE` lines; a real
   `.git/HEAD` starts with `ref: refs/heads/`; a real `package.json` starts with
   `{"name"`. A block page has `<html`, a WAF brand string, or the SPA shell.
2. Check the content-type header matches the file kind (mismatch = suspect).
3. Compare the body against the baseline body with `diff` — a "200 .env" whose body
   is byte-identical to the 404 page is a NEGATIVE wearing a 200 status.
4. For archives/dumps (`.zip`, `.sql`, `.tar.gz`): check magic bytes
   (`PK\x03\x04`, `-- `, `\x1f\x8b`) in the first bytes via `xxd | head`. Download
   at most the first 64KB for verification — never pull a full multi-MB dump
   without a reason; note the size and move on.
5. Secrets handling: if a file contains what looks like live credentials, DO NOT
   test them. Redact in notes, mark the file CONFIRMED-exposed, and escalate per
   the program's rules. Verification = the file is served unauthenticated, not
   that the credential works.

## Step 6 – Response-Intelligence Table

Classify every probe result through this table before writing any verdict:

| Response | vs Baseline | Verdict | Action |
|---|---|---|---|
| 200, body has file-kind markers (KEY=, `ref:`, `{`, magic bytes) | diverges | CONFIRMED | raw pair saved, reproduce 2× |
| 200, body is HTML / SPA shell / WAF brand | matches baseline hash | NEGATIVE | log, move on — the classic trap |
| 200, body differs but is generic error text | diverges weakly | INCONCLUSIVE | re-probe; check content-type |
| 301/302 to login or homepage | n/a | NEGATIVE | redirect = not exposed (note target) |
| 301/302 to the file itself on a CDN domain | n/a | FOLLOW-UP | probe the redirect target once |
| 403 with stable body | matches block baseline | NEGATIVE/BLOCKED | file may exist but is denied — not a finding |
| 403 with body differing from block baseline | diverges | INCONCLUSIVE | interesting — re-probe, check size delta |
| 206 partial content | diverges | CONFIRMED | server honored range; verify first bytes |
| 500 on one probe, 404 on re-probe | flaky | INCONCLUSIVE | document flakiness, do not promote |

If X then Y: body matches baseline hash → NEGATIVE even on 200. Content-type
`text/html` + SPA title → NEGATIVE even on 200. Magic bytes present → CONFIRMED
candidate, reproduce 2×. Redirect loop → NEGATIVE, note it once.

## Step 7 – Reproduce and Save Raw Pairs

Same bar as routes: 2× reproduction on separate connections ~60s apart, matching
status + size + hash. Append raw request/response (headers + first 2KB of body,
secrets redacted) to `discovery/generic_files_raw.md`. NEGATIVE paths logged as
one-liners. A CONFIRMED `.env` gets its first 3 non-secret lines quoted as the
marker (e.g. `APP_NAME=`, `DB_HOST=`) — never full values.

## Step 8 – Exact Commands (Copy-Paste)

```bash
TARGET="https://target.example.com"

# 1. Baselines: extensionless AND extension-matched
for p in "levi-dead-$RANDOM" "levi-dead-$RANDOM.env" "levi-dead-$RANDOM.php.bak"; do
  echo "== /$p =="
  curl -sk -o /tmp/fb -D /tmp/fb_hdr -w "status=%{http_code} size=%{size_download} ct=%{content_type}\n" "$TARGET/$p"
  echo "sha1=$(sha1sum /tmp/fb | cut -d' ' -f1)"
done

# 2. Battery
cat > /tmp/file_candidates.txt <<'EOF'
.env
.env.bak
.git/HEAD
.git/config
.svn/entries
wp-config.php.bak
config.php.bak
config.php~
composer.json
package.json
web.config
server.xml
.DS_Store
Thumbs.db
phpinfo.php
info.php
backup.zip
db.sql
dump.sql
.idea/workspace.xml
EOF
while read -r f; do
  out=$(curl -sk -o /tmp/fb -D /tmp/fb_hdr -w "%{http_code} %{size_download} %{content_type}" --max-time 20 "$TARGET/$f")
  hash=$(sha1sum /tmp/fb | cut -d' ' -f1)
  head5=$(head -c 120 /tmp/fb | tr -d '\n' | cut -c1-80)
  echo "$f -> $out sha1=$hash :: $head5"
  sleep 1
done < /tmp/file_candidates.txt | tee /tmp/file_probe.log

# 3. Magic-byte check on a candidate archive/dump (first 16 bytes)
curl -sk --max-time 20 "$TARGET/CANDIDATE" | head -c 16 | xxd

# 4. Baseline diff — is this "200 .env" just the 404 page?
curl -sk "$TARGET/CANDIDATE" -o /tmp/cand; curl -sk "$TARGET/levi-dead-$RANDOM.env" -o /tmp/bl
diff -q /tmp/cand /tmp/bl && echo "IDENTICAL_TO_BASELINE -> NEGATIVE"

# 5. Reproduce 2x
for i in 1 2; do
  curl -sk -o /tmp/rb --max-time 20 "$TARGET/CANDIDATE"
  echo "run$i size=$(wc -c < /tmp/rb) sha1=$(sha1sum /tmp/rb | cut -d' ' -f1)"; sleep 60
done
```

## Step 9 – Completion Checklist

- [ ] `discovery/baseline.txt` has BOTH extensionless and extension-matched baselines
- [ ] Full battery probed (env, VCS, backups, manifests, OS artifacts, debug) + JS-derived filename variants, each with a documented source
- [ ] Every probe compared against the extension-matched baseline, not a single global one
- [ ] Every CANDIDATE verified through the 5 content checks (markers, content-type, baseline diff, magic bytes, secret handling)
- [ ] Response-intelligence table applied to every result — no verdict without a table row
- [ ] Every CONFIRMED file reproduced 2× with matching status + size + hash
- [ ] Raw pairs saved in `discovery/generic_files_raw.md` (secrets redacted)
- [ ] NEGATIVE paths logged as one-liners; `robots.txt`/`sitemap.xml` logged as INFO
- [ ] No live credential was tested — exposure verified, secrets redacted, escalated per program rules
- [ ] `discovery/generic_files.txt` written in the exact finished-artifact format
- [ ] Review: reviewer re-runs baseline, spot-checks 3 CONFIRMED files with curl,
      diffs each against baseline, confirms file-kind markers present. Any "confirmed"
      file that diffs identical to baseline fails the run.
- Nudge prompts:
  - "That 200 on .env — did you diff it against the .env baseline, or the extensionless one? Do it now."
  - "The body starts with <html. It's the fallback. Mark it NEGATIVE and keep going."
  - "You found a .git/HEAD. Did you check .git/config too? Leaks chain — follow the chain."

## Step 10 – Evidence Standard (No False Positives)

- **CONFIRMED** = extension-matched baseline divergence + file-kind markers in body
  (or magic bytes) + 2× reproduction + raw pair saved with secrets redacted.
- **INCONCLUSIVE** = diverges but markers absent, or flaky across reproductions.
- **NEGATIVE** = matches baseline (any status), redirect to login/home, or WAF block page.
- **BLOCKED** = every probe returns the block page; documented, not silently skipped.
- A 200 with an HTML body on a `.env` probe is NEGATIVE until proven otherwise —
  the burden of proof is on the hunter, not the status code.
- Exposed secrets are never live-tested. CONFIRMED means "served unauthenticated
  with real file-kind content," full stop.

## Step 11 – Finished Artifact & Handoff

Done = `discovery/generic_files.txt` exists, one line per file:
`CONFIRMED <path> <status> <size_bytes> <content_type> <marker>` — marker examples:
`KEY=VALUE-lines`, `ref:-refs/heads/`, `PK-magic`, `composer-json`. Or the single
`NONE <host> <date>` line when nothing confirmed. `discovery/generic_files_raw.md`
holds the probe table, raw pairs (redacted), and the negative log.

Handoff: **app-specific-files** consumes `generic_files.txt` + `baseline.txt` — the
extension-matched baseline work carries over directly, and any CONFIRMED manifest
(`package.json`, `composer.json`) hard-confirms stack details for the tech-derived
battery. **bugbounty-report-intel** consumes surprising CONFIRMED finds (e.g. an
exposed `.svn/entries` in 2026) as new writeup-pattern seeds. Credential-class
finds escalate immediately per program rules — they do not wait for the phase gate.
