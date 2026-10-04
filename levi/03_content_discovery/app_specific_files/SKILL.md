---
name: app-specific-files
description: >
  Derives framework-specific hidden paths from the JS-analysis tech fingerprint (Next.js, Nuxt, Laravel, Django, Rails, Spring, WordPress) and probes app-specific config/backup naming with the same baseline and verification discipline as the generic battery. USE THIS SKILL whenever the user wants to hunt framework-specific exposed files after the tech stack is known. Trigger on: "framework-specific file discovery", "Next.js exposed files", "Laravel telescope check", "Spring actuator files", "tech-derived paths", "app-specific config hunting". This skill produces the verified tech-derived file inventory – the ffuf-workflow skill fires it at scale by running the derived battery with recursion and calibrated filters.
---

# App-Specific Files Discovery

You are operating as the world's best bug bounty hunter and red teamer. Your job is to turn the framework fingerprint from JS analysis into a targeted file battery that generic wordlists never contain: `/_next/static/` build manifests, `/telescope` and `/horizon` dashboards, `/.env` on Laravel, `/actuator/heapdump` on Spring, `/_nuxt/` payloads, `wp-config.php.bak` on WordPress. Generic batteries find generic files. Tech-derived batteries find the misconfigurations that only exist on THIS stack.

## Step 1 – Gather Inputs

Collect before building the battery:
- `02_js_analyze/tech_choices.md` — the framework/build-tooling fingerprint. This is
  the battery's blueprint. If it's missing, STOP: this skill cannot run without it.
  (Fall back to `generic-files`, which is stack-agnostic.)
- `discovery/baseline.txt` — the extension-matched baselines from `generic-files`.
  Reuse them; do not recalibrate unless the host changed.
- `discovery/generic_files.txt` + `generic_files_raw.md` — already-confirmed manifests
  hard-confirm the stack (a CONFIRMED `composer.json` = Laravel-family until proven
  otherwise) and already-probed paths must NOT be re-probed.
- `02_js_analyze/routes_params.md` — app-specific naming hints (route prefixes,
  tenant slugs, feature names) for the custom-naming battery.

Division of labor: consumes `tech_choices.md` + baselines + prior results; produces
`discovery/app_specific.txt` (verified tech-derived hits),
`discovery/app_specific_raw.md` (battery derivation table + probe log + raw pairs).
Skip when `tech_choices.md` is inconclusive (no framework signal = no derived battery),
when the Generic battery already confirmed the same paths, or when the stack is a
fully static export with no server runtime — probing `/actuator` on a static S3 site
is time-pass.

## Step 2 – Translate the Fingerprint into a Battery

One section per detected framework. Probe ONLY the sections matching
`tech_choices.md` — running all seven sections on every host is generic fuzzing with
extra steps, and it burns rate budget.

**Next.js:** `/_next/static/<buildId>/` (get buildId from page HTML or JS),
`/_next/static/<buildId>/_buildManifest.js`, `/_next/static/<buildId>/_ssgManifest.js`,
`/api/` (enumerate from JS), `/_next/data/<buildId>/<page>.json` (data routes —
compare against the HTML page; unauthenticated JSON data endpoints are the prize)

**Nuxt:** `/_nuxt/`, `/_nuxt/manifest.json`, `/_payload.json`, `/_payload.js`,
`/api/_content/` (Nuxt Content), `/__nuxt_error` (no — that's a route; probe
`/_nuxt/` build assets for sourcemap comments)

**Laravel:** `/telescope`, `/telescope/requests`, `/horizon`, `/horizon/api/jobs`,
`/.env` (already in generic — note the dedupe), `/storage/logs/laravel.log`,
`/vendor/composer/installed.json` (exposed vendor = full dependency leak),
`/api/documentation` (Scramble/Scribe)

**Django:** `/static/admin/`, `/admin/` (route — dedupe with generic-routes),
`/sitemap.xml` (INFO), `/api/schema/`, `/api/docs/` (drf-spectacular),
`/media/`, `/staticfiles.json`

**Rails:** `/rails/info/routes` (dev only — a hit here is a finding),
`/rails/info/properties`, `/sidekiq`, `/resque`, `/assets/.sprockets-manifest-*.json`
(glob: probe the manifest name found in page HTML)

**Spring Boot:** `/actuator`, `/actuator/env`, `/actuator/heapdump`,
`/actuator/threaddump`, `/actuator/mappings`, `/actuator/beans`,
`/actuator/configprops`, `/api-docs`, `/v3/api-docs`, `/swagger-ui/index.html`
(`/actuator/env` and `/heapdump` with real content = high severity; handle per
program rules, never exfiltrate the heap)

**WordPress:** `/wp-config.php.bak`, `/wp-config.php~`, `/wp-config.php.old`,
`/wp-json/wp/v2/users` (user enumeration — INFO/lead, not a file win),
`/wp-content/debug.log`, `/wp-content/uploads/` (directory listing check),
`/license.txt`, `/readme.html` (version disclosure — INFO)

**App-specific naming:** derive from `routes_params.md` tokens. Token `billing`
→ `/billing.sql`, `/billing_backup.zip`, `/config-billing.json`. Token `tenant`
`acme` → `/acme.env`, `/config-acme.json`. Every derived path documents its source
token + framework section. If a derived path duplicates a generic-files probe,
dedupe it and note the dedupe — probing twice is not thoroughness.

## Step 3 – Build the Derivation Table First

Before any probe, write `discovery/app_specific_raw.md` section 1: a table of
`framework | path | why (what it leaks) | source (tech_choices line / generic hit / JS token)`.
This table is the review surface: a reviewer must be able to strike any row and ask
"why did you probe this?" and get a one-line answer. Rows without a source are deleted.

## Step 4 – Probe with the Same Baseline Discipline

Extension-matched baselines from Step 1 inputs. Same 1s spacing, same plain GET,
same capture (status/size/sha1/content-type/title). The response-intelligence table
from `generic-files` applies verbatim — framework paths get no special pleading.
A 200 `/_next/static/BUILD_ID/_buildManifest.js` with HTML body is the SPA costume,
not a build manifest.

## Step 5 – Understand Framework-Specific Content

- `/_next` build manifests / `/_nuxt` payloads: confirm they parse as JS/JSON and
  contain route/page data — then mine them for NEW routes and feed those to
  `generic-routes` (this is the loop: files → routes → files).
- `/telescope`, `/horizon`, `/sidekiq`: a login/403 = EXISTS but gated (lead, not
  finding). A 200 dashboard with request data = CONFIRMED high-value — screenshot
  the marker, save raw pair, reproduce 2×, escalate per program rules.
- `/actuator/env`, `/heapdump`: verify content-type and first bytes
  (`application/octet-stream` + `JAVA PROFILE` magic for heapdump). Do NOT download
  full heapdumps — note size, confirm the first 64KB, stop.
- `/vendor/composer/installed.json`, `/.sprockets-manifest`: CONFIRMED = dependency
  list served unauthenticated. Quote the package count as the marker, not the list.
- `wp-config.php.bak` serving PHP source = CONFIRMED critical-class. Verify it
  contains `DB_PASSWORD`-shaped lines, redact everything, escalate immediately.

## Step 6 – Feed Findings Back into the Loop

Every CONFIRMED app-specific file is mined for the next battery: build manifests
yield routes (→ `generic-routes`), `installed.json` yields exact library versions
(→ cross-check with `02_js_analyze/libraries.md` for known CVEs — that's a lead for
the vuln-analysis track, not this skill), `debug.log` tails yield paths and
subdomains. Document each follow-up as a handoff line in the raw file, don't chase
it inside this skill — one skill, one job.

## Step 7 – Exact Commands (Copy-Paste)

```bash
TARGET="https://target.example.com"
# Baselines already in discovery/baseline.txt — re-verify freshness first:
curl -sk -o /dev/null -w "dead-path check: %{http_code} %{size_download}\n" "$TARGET/levi-dead-$RANDOM"

# Example: Next.js buildId extraction, then manifest probes
BUILD=$(curl -sk "$TARGET/" | grep -o '/_next/static/[A-Za-z0-9_-]*' | head -1 | cut -d/ -f4)
echo "buildId=$BUILD"
for p in "_next/static/$BUILD/_buildManifest.js" "_next/static/$BUILD/_ssgManifest.js"; do
  out=$(curl -sk -o /tmp/ab -w "%{http_code} %{size_download} %{content_type}" --max-time 20 "$TARGET/$p")
  echo "$p -> $out sha1=$(sha1sum /tmp/ab | cut -d' ' -f1) :: $(head -c 80 /tmp/ab | tr -d '\n')"
  sleep 1
done

# Example: Spring actuator env (verify, don't exfiltrate)
curl -sk -D /tmp/ah -o /tmp/ae --max-time 20 "$TARGET/actuator/env"
head -1 /tmp/ah | tr -d '\r'; echo "size=$(wc -c < /tmp/ae) :: $(head -c 100 /tmp/ae | tr -d '\n')"

# Example: Laravel telescope — exists vs gated vs open
curl -sk -o /tmp/tl -w "%{http_code} %{size_download}\n" --max-time 20 "$TARGET/telescope"
grep -oi '<title>[^<]*' /tmp/tl | head -1

# Dedupe check against generic-files before probing (never probe twice)
grep -qxF "CONFIRMED $CANDIDATE" discovery/generic_files.txt 2>/dev/null && echo "ALREADY COVERED — skip"
```

## Step 8 – Completion Checklist

- [ ] `tech_choices.md` read; framework sections selected and documented (or skill
      correctly skipped as inconclusive, with the reason logged)
- [ ] Derivation table written in `discovery/app_specific_raw.md` BEFORE probing —
      every row has framework + why-it-leaks + source
- [ ] Battery deduped against `generic_files.txt` (no double-probes; dedupes noted)
- [ ] Every probe compared against the extension-matched baseline
- [ ] Response-intelligence table applied to every result (no framework favoritism)
- [ ] Every CONFIRMED hit reproduced 2× with matching status + size + hash
- [ ] Raw pairs saved (secrets redacted; heapdumps truncated at 64KB verification)
- [ ] CONFIRMED manifests mined for follow-up routes/versions; follow-ups logged as
      handoff lines, not chased inside this skill
- [ ] NEGATIVE paths logged as one-liners
- [ ] `discovery/app_specific.txt` written in the exact finished-artifact format
- [ ] Review: reviewer reads the derivation table, strikes 3 rows at random, and the
      hunter justifies each from `tech_choices.md` or a JS token; reviewer re-probes
      2 CONFIRMED hits against baseline. Unjustified rows = failed review.
- Nudge prompts:
  - "You probed /actuator because the stack is Spring — show me the tech_choices.md line that says so."
  - "That 200 on /telescope — login page or open dashboard? The difference is a lead vs a finding."
  - "The build manifest gave you five new routes. Did you feed them to generic-routes, or admire them and move on?"

## Step 9 – Evidence Standard (No False Positives)

- **CONFIRMED** = extension-matched baseline divergence + framework-content markers
  verified (parses as manifest/JSON/dashboard, magic bytes, or dashboard markers) +
  2× reproduction + raw pair saved.
- **INCONCLUSIVE** = diverges but content ambiguous (HTML body on a JSON path).
- **NEGATIVE** = matches baseline, redirect, or gated-login with no data.
- **BLOCKED** = documented with observed behavior.
- Auth-gated dashboards (`/telescope` login, `/sidekiq` 403) are CONFIRMED-existing
  but gated — logged as leads with the gate type, never as "access found."
- Exposed secrets/credentials follow the same handling as `generic-files`: verify
  exposure, redact, escalate — never test.

## Step 10 – Finished Artifact & Handoff

Done = `discovery/app_specific.txt` exists, one line per hit:
`CONFIRMED <path> <status> <size_bytes> <framework> <marker>` — e.g.
`CONFIRMED /actuator/env 200 48210 spring propertySources-present`.
Or the single `NONE <host> <date> framework=<name>` line.
`discovery/app_specific_raw.md` holds the derivation table, probe log, raw pairs,
negative log, and follow-up handoff lines.

Handoff: **ffuf-workflow** consumes `app_specific.txt` + the derivation table — the
derived battery becomes a seeded ffuf run with `-recursion` on CONFIRMED directories
(e.g. `/_next/static/<buildId>/` recursed for unreferenced chunks).
**generic-routes** consumes newly mined routes from CONFIRMED manifests (the loop
runs both directions). **bugbounty-report-intel** consumes surprising CONFIRMED
finds as new writeup-pattern seeds.
