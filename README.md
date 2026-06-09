Reconnaissance is the foundation of any successful bug bounty or red-team engagement. The more you know about your target, the higher your chance of finding vulnerabilities. In particular, enumerating hidden endpoints — subdomains, archived URLs, unlinked pages — expands your attack surface. Passive recon (OSINT, publicly available info) is especially valuable because it “doesn’t interact with the target directly” and thus makes “very little noise”. Active recon (scanning, probing) comes next, unearthing hidden content by actually querying the target. Together these steps give you context and stealthy access to bug locations. Always remember: only scan targets you are explicitly authorized to test. Bug bounty programs and pentests define a clear scope — a list of domains, subdomains, and asset types you may test. Violating scope (or legal boundaries) can invalidate your work and even get you into trouble.

Passive vs. Active Recon
Reconnaissance falls into two main categories. Passive recon gathers data from open sources: WHOIS, search engines, public APIs (Shodan, Censys), and archived services. It is stealthy. For example, Google dorks, certificate transparency logs, and archive services can all reveal endpoints without touching the target’s servers. Active recon involves directly interacting with the target: DNS queries, ping sweeps, or HTTP requests. While active techniques can find hidden hosts or services that OSINT misses, they also generate traffic the target could detect. A smart recon strategy uses passive first (for broad mapping) then active techniques (to confirm and explore) once you know what to look for.

Scoping responsibly: Before any recon, double-check program rules. Every bug bounty or red-team engagement has a defined scope — e.g. *.example.com or specific IP ranges. Only test assets listed in scope, and respect explicit exclusions (out-of-scope items). For example, Bugcrowd notes that an asterisk in scope (*.bugcrowd.com) means all subdomains are fair game, unless the program rules say otherwise. Operating within scope is not just ethical, it’s required for your findings to be valid.

Subdomain Enumeration with subfinder
A great first step is finding all subdomains of the target. Subdomains often host hidden services (dev sites, APIs, staging apps). Subfinder (by ProjectDiscovery) is a popular passive subdomain enumerator. It “uses passive online sources” (whois, search engines, SSL logs, etc.) to find subdomains. It’s praised for being “fast, reliable, and offering extensive coverage”.

Installation: If you have Go installed, one can run:

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
Or download binaries from the GitHub release.

Usage: The basic subfinder command is:

subfinder -d example.com -o subdomains.txt
This asks subfinder to enumerate passive results for example.com and save them to subdomains.txt. You can add flags like -t 50 (threads) or -silent to suppress extra output. For example:

subfinder -d example.com -silent -t 50 -o example_subs.txt
This would quietly find subdomains (one per line in example_subs.txt). A sample output might be:

example.com
www.example.com
api.example.com
dev.example.com
(Your output will vary by target.)

You can also feed a list of domains via -dL domains.txt. Many hunters run multiple tools (like Sublist3r, Amass, Assetfinder) and merge/uniquify the results, since each finds slightly different subdomains. Regardless, the goal is the same: build a complete list of candidate hostnames for the target.

Archive Mining with waybackurls and gau
Next, search archives of known URLs. waybackurls (Tomnomnom) and gau (“Get All URLs”) are powerful for this. These tools query sources like the Wayback Machine, Common Crawl, and other indexed data to fetch historical URLs for your domains.

waybackurls: Given a domain, it fetches all URLs the Internet Archive (Wayback Machine) has recorded. For example:
echo "example.com" | waybackurls > wayback.txt
(If waybackurls is in your PATH.) This writes every archived URL to wayback.txt. Waybackurls requires Go; install it with go get github.com/tomnomnom/waybackurls. The command above would output lines like:

http://example.com/about
https://example.com/login?next=/dashboard
https://api.example.com/v1/data
gau: Similarly, gau fetches known URLs from several sources (AlienVault, VirusTotal, URLScan, etc.). Use it like:
echo "example.com" | gau > gau.txt
This captures even more historical endpoints. You must install it (e.g. go get -u github.com/lc/gau).

After running both, combine and deduplicate:

cat wayback.txt gau.txt | sort -u > all_urls.txt
This merged all_urls.txt contains any unique URL (paths, endpoints) gathered from archives. These may include forgotten or hidden pages (login forms, admin panels, JavaScript endpoints) that aren’t linked from the main site.

Why archive mining? These tools often surface endpoints you’d never find by crawling the live site. They reveal things developers had on the site at some point, and attackers might have hidden files. For example, old endpoints like /portal, /admin, or API paths may show up. As one guide notes, “fetch all the URLs that the Wayback Machine knows about” helps you get everything recorded about the domain.

Validating Endpoints with httpx
Once you have lists of subdomains (subdomains.txt) and URLs (all_urls.txt), the next step is to check which ones are actually alive and gather details. httpx (ProjectDiscovery) is a fast, multi-probe HTTP scanner perfect for this. It takes a list of hosts or URLs and issues requests to see which respond.

Installation: go install github.com/projectdiscovery/httpx/cmd/httpx@latest or grab a binary.

Basic Usage: Common flags include:

-silent: suppress extra text, only show results
-status-code or -sc: print HTTP status codes
-title: include the page’s <title>
-server: show the Server header
-random-agent: rotate common User-Agent strings
-threads / -t: set concurrency (e.g. -t 200)
-timeout: per-request timeout (seconds)
-follow-redirects: by default, it shows only final statuses or can show redirects.
For example, to filter a list of domains to only the ones that serve HTTP/S and record info:

cat subdomains.txt | httpx -silent -status-code -title -server -o alive.txt
This reads each domain, tries http:// and https://, and writes lines like:

https://www.example.com [200] [Server: nginx] [Title: Example Domain]
https://api.example.com [200] [Server: apache] [Title: API Endpoint]
https://dev.example.com [404] ...
The alive.txt file now has all endpoints that responded (and the ones that didn’t are skipped).

A more advanced command might use multiple flags:

httpx -l all_urls.txt -silent -title -sc -server -random-agent -timeout 8 -t 100 -o results.txt
This probes every URL in all_urls.txt, using a random User-Agent on each request and a timeout of 8s, with up to 100 concurrent threads. The output lists live URLs with metadata. (If you only want status 200/301, you can use -mc 200,301 or invert filters with -fc to ignore 404/403.)

You can also use httpx creatively, e.g. its -path option for brute-forcing paths, or -favicon to fingerprint services. For example, running:

echo example.com | subfinder -silent | httpx -favicon
will output the favicon hash of each subdomain. These features enrich your recon output and help prioritize.

Directory and Parameter Fuzzing with ffuf
With live endpoints in hand, it’s time to fuzz directories and parameters to find hidden resources. ffuf (“Fuzz Faster U Fool”) is a flexible web fuzzer written in Go. You provide it a wordlist and a URL template with the keyword FUZZ, and it tries each word in place of FUZZ, reporting any responses that don’t match the default error pages.

Directory discovery: To find hidden directories/files on a host:
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
     -u https://target.com/FUZZ -mc 200 -o ffuf_dir.txt
This will try each word as a path, only showing results that return status 200. You can adjust with -mc (match code) or -fc (filter out code). For example, -fc 404 excludes 404s.

Filtering noise: If the server returns a custom 404 page with size X, you can skip responses of that size using -fs. In ffuf’s docs, they demonstrate filtering out a default response of size 4242 bytes: -fs 4242. For example:
ffuf -w small.txt -u https://target/FUZZ -mc 200 -fs 4242
This avoids showing hits that are just the standard “not found” page.

Parameter fuzzing: You can fuzz parameter names or values similarly. For example, to find valid GET parameters:
ffuf -w /usr/share/wordlists/param-names.txt \
     -u https://target/script.php?FUZZ=test -fc 400
Or if the parameter name is known and you want to fuzz its value:

ffuf -w /usr/share/wordlists/values.txt \
     -u https://target/script.php?user=FUZZ -mc 200
Use -H to fuzz headers (like Host), and -d for POST data fuzzing.

Output: ffuf prints a table of results. For example, a successful directory fuzz might show:

[Status: 200] https://target.com/admin (Size: 483)
[Status: 200] https://target.com/api (Size: 1024)
Found results mean the paths exist (e.g. /admin often indicates an admin panel).

Download the Medium App
By mixing -w, -u, and filters, you can tailor ffuf to find just the interesting endpoints. It supports recursion (-recursion) too, to drill down into discovered subdirectories.

Crawling with hakrawler
Even after fuzzing, it’s useful to crawl the site dynamically. hakrawler is a simple, fast web crawler designed for quickly extracting URLs and assets (including JS endpoints). It basically spiders through HTML, JavaScript, robots.txt, sitemap.xml and even queries Wayback while it runs.

Usage:

echo "https://target.com" | hakrawler -depth 3 -subs > hakrawl.txt
This command starts at target.com, crawls links up to 3 hops deep, and -subs makes it include subdomains found in links. You can also feed it a list of URLs: cat urls.txt | hakrawler. The output is a list of discovered links, one per line. For example:

https://target.com/
https://target.com/login
https://target.com/static/js/app.bundle.js
https://api.target.com/v1/users
Hakrawler will collect pretty much anything linked on those pages, including JavaScript endpoints and APIs.

If you use a proxy (e.g. Burp or OWASP ZAP) for analysis, hakrawler supports that too:

echo target.com | hakrawler -proxy http://127.0.0.1:8080
(This routes requests through your proxy, which can help you monitor requests or rotate through Tor.)

Hakrawler also has a useful note: if a domain redirects to www.example.com (for example), the non-www entry might show no results unless you include -subs. That’s because it will stick to the exact domain unless told to include subdomains.

Building an Efficient Recon Pipeline
So how do we tie all these tools together? The power is in piping outputs and chaining tools. A typical workflow looks like:

Subdomain enumeration:
subfinder -d example.com -silent -o subs.txt
(You might also run Assetfinder/Amass and append their results to subs.txt, then dedupe: sort -u subs.txt -o subs.txt.)

2. Check live domains:

cat subs.txt | httpx -silent -status-code -o alive_domains.txt
This filters only the live subdomains (step [40†L149-L152] shows how httpx -silent “filters the subdomains by checking if they are alive”).

3. Archive mining:

cat alive_domains.txt | waybackurls | tee wayback.txt
cat alive_domains.txt | gau | tee gau.txt
We run Wayback and gau on each active domain. Then combine:

cat wayback.txt gau.txt | sort -u > historical_urls.txt
4. Validate and enrich URLs:

cat historical_urls.txt | httpx -silent -status-code -title -o valid_urls.txt
Now valid_urls.txt has only URLs that still respond (and their titles/status codes).

5. Fuzz for hidden paths:

ffuf -w /usr/share/wordlists/common.txt -u FUZZ://example.com/FUZZ -m 200 -o ffuf_results.txt
You can feed the discovered domains from alive_domains.txt into ffuf for each one, or manually target specific hosts.

6. Crawl dynamic links:

cat alive_domains.txt | xargs -I % sh -c 'echo % | hakrawler -subs'
This runs hakrawler on each live domain. (Or simply: echo example.com | hakrawler -subs.)

A shorter example pipeline (as a one-liner) might look like:

subfinder -d example.com | httpx -silent | tee alive.txt | gau | waybackurls | sort -u > endpoints.txt
This would discover subs, filter live, then fetch archive URLs for those, and output unique endpoints. (From here, you’d probably filter again with httpx, etc.)

You can also send outputs through tee at each stage to save intermediate files. For example, a simple bash script at the end of this article shows how to string these tools together into one workflow.

Prioritizing Endpoints
With dozens or hundreds of endpoints, focus is key. Prioritize the most promising targets first:

HTTP status: Endpoints returning 200 (OK) or 302/301 (redirects) are often more interesting than those returning 404/403. For example, a 302 redirect might hint at a login page. Use httpx -mc 200,302 to filter.
Content type: HTML pages with forms or dynamic apps get attention. Large binary responses (images, videos) can usually be skipped. You can use httpx’s -ct or -size filters to drop known static types.
URL pattern: Look at path names. Common words like admin, login, portal, api, dashboard, wp-admin, etc., are high-value. JSON or XML API endpoints (ending in .json, .xml) may reveal data. For example, endpoints like /api/v1/users or /secret/config stand out.
Parameter fuzz hints: URLs with query parameters (e.g. ?id=, ?page=, ?token=) deserve testing for injection or logic flaws. Use tools like Arjun or ffuf on parameters for these.
Server info and titles: httpx can show the server header and HTML <title>. A custom server (e.g. Apache vs. nginx) or a descriptive title can give clues about the technology. Make note of unusual ones.
Novel endpoints: Any endpoint discovered by only one tool should be double-checked. For example, if waybackurls found a /hidden.php, verify if it’s really accessible now (it might be a false positive if the site returned 200 for every path).
Always validate findings manually before chasing them. A reported “vulnerability” found during recon might turn out to be a false positive (e.g., a generic error page looking unique). If an endpoint looks interesting, try accessing it in a browser or with curl/httpie to confirm its behavior.

OPSEC and Stealth Tips
Being stealthy not only helps keep you below the radar, it also mimics real attacker behavior. Some best practices:

Rotate User-Agents: Don’t let all your requests come from the default tool signature. Tools like httpx have a -random-agent flag that randomly picks from common browser user-agents. For example:
cat subs.txt | httpx -random-agent -silent -o live.txt
For ffuf, you can use the -H flag to set a custom User-Agent header.

Throttle and Timeout: Don’t blast servers with thousands of threads at once. Use moderate thread counts (-t) and reasonable timeouts (-timeout). For example, -t 50 -timeout 8 reduces load. Slower, well-spaced scans generate less noise and are less likely to trip WAFs.
Proxy or VPN: Route your scans through a proxy chain or VPN if allowed. Hakrawler’s -proxy example shows using -proxy http://localhost:8080 to send traffic through Burp. You could similarly configure httpx with a proxy. (Some platforms forbid VPNs, so always check rules.)
Avoid Known Patterns: If the target has WAF or IPS, they often block rapid requests. Vary the timing and user-agent strings, and consider adding small delays. For example, run sleep 0.5 between requests in a loop if needed.
Respect robots.txt: As a courtesy (and to find interesting paths), check robots.txt first. Hakrawler or a simple curl https://target.com/robots.txt can list disallowed paths, which sometimes include hidden admin URLs.
By applying these OPSEC measures, you make your reconnaissance stealthier and avoid blowing your cover too early.

#!/bin/bash
# recon.sh - Simple Reconnaissance Pipeline Script
# Usage: ./recon.sh target.com

if [ -z "$1" ]; then
  echo "Usage: $0 target-domain.com"
  exit 1
fi

TARGET=$1

echo "[*] Finding subdomains for $TARGET..."
subfinder -d $TARGET -silent | sort -u > subs.txt

echo "[*] Fetching archived URLs..."
cat subs.txt | waybackurls | tee wayback.txt
echo $TARGET | gau | tee gau.txt

echo "[*] Merging URL lists..."
cat wayback.txt gau.txt | sort -u > all_urls.txt

echo "[*] Filtering alive URLs..."
cat all_urls.txt | httpx -silent -status-code -o valid_urls.txt

echo "[*] Directory fuzzing on $TARGET..."
ffuf -w /usr/share/wordlists/common.txt -u https://$TARGET/FUZZ -mc 200 -o ffuf_dirs.txt

echo "[*] Done! Results saved to subs.txt, valid_urls.txt, ffuf_dirs.txt."
Figure: A simple Bash script chaining the tools into one workflow. (Copy and save this as recon.sh, make it executable with chmod +x recon.sh, then run ./recon.sh example.com to try it.)

Avoiding Burnout and False Positives
Recon can generate a mountain of data. To avoid burnout and noise:

Stay organized: Keep notes or spreadsheets. Track which hosts/endpoints you’ve already checked to avoid duplication. Automate as much as possible, but review results in manageable chunks.
Take breaks: Recon sessions can be tedious. Work in blocks (e.g. scan a night and review in the morning). Long overnight scans (when network use is low) can finish tasks without you watching the screen.
Filter rigorously: Automate filtering of obvious false positives (common 404 pages, duplicates). Trust confirmed anomalies only. For example, if every hostname returns a 200 redirect to a default page, treat that carefully.
Trust but verify: Before filing a bug, manually interact with the endpoint. Many seeming vulnerabilities (like an accessible admin login page) are legitimate parts of the application. Verify you can actually exploit them.
Know when to stop: It’s easy to over-recon (scanning endlessly). Once you’ve enumerated subdomains, found all unique endpoints, and fuzzed the key hosts, pause and analyze. Additional scanning often yields diminishing returns.
Above all, maintain a sustainable pace and sanity. Recon is important, but it’s just one phase of engagement. Balanced, thorough work always beats frantic, unfocused scanning.

















The Hidden API Endpoints That Can Make $10k in Bug Bounties (Complete Methodology)
The Endpoint Nobody Was Testing


BugHunter’s Journal

6 min read

1
The Endpoint Nobody Was Testing
2
What Are "Hidden" API Endpoints?
3
Why These Endpoints Exist
4
Reason 1: Legacy Code
5
Reason 2: Different Platforms
Show all 38 sections
The Endpoint Nobody Was Testing
Most bug bounty hunters test the obvious stuff: login forms, search boxes, password resets. They're all fighting over the same vulnerabilities, competing for $500 payouts.

Meanwhile, some people are getting $10,000+ bounties by testing API endpoints that don't even appear in the application.

This isn't luck. It's methodology.

Here's what nobody tells you: Modern web applications expose 3–5x more API endpoints than what you see in the browser. These hidden endpoints are:

Poorly documented

Minimally tested

Often lack proper authorization

Sitting there, waiting to pay you

Let me show you exactly how to find these hidden goldmines.

What Are "Hidden" API Endpoints?
None
Hidden endpoints aren't actually hidden — they're just not linked anywhere in the UI.

Example:

The web app has a visible feature: "View Profile."

Visible endpoint:


GET /api/users/me
Hidden endpoints doing the same thing:


GET /api/v1/users/me
GET /api/v2/users/me
GET /api/internal/users/me
GET /api/admin/users/me
GET /api/mobile/users/me
Each version might have different security controls. Or none at all.

Real bug bounty case:

/api/v3/users/me → Secure, well-tested
/api/v1/users/me → Returns admin token in response
Payout: $3000
API Hacking for Bug Bounty: A Complete Beginner-to-Advanced Guide APIs power 83% of all web traffic today. Yet most bug bounty hunters completely ignore them.

Why These Endpoints Exist
Reason 1: Legacy Code
The company upgrades from API v1 to v3, but forgets to shut down v1 and v2.


v3 → Production (secure)
v2 → Deprecated (forgotten)
v1 → Ancient (no security)
Reason 2: Different Platforms

/api/web/...     → For website
/api/mobile/...  → For mobile app
/api/internal/... → For admin panel
Each team builds its own API. Security is inconsistent.

Reason 3: Debug/Test Endpoints
Developers create endpoints for testing:


/api/debug/user-info
/api/test/create-admin
/api/dev/reset-database
They forget to remove them before going live.

The 10-Step Methodology
The 10-Step Methodology
🧠 Step 1 — Start With Recon: Know Where APIs Hide
🔍 A. Inspect the Mobile App
Mobile apps bundle API endpoints in: 📌 Decompiled APK/IPA 📌 Network calls while using the app 📌 Hard-coded base URLs in config files

Toolbox you need:

Burp Suite / Charles Proxy (intercept traffic)
JADX / Hopper (decompile)
Postman (to test endpoints)
Example: Intercepting a login request reveals:


POST /api/v2/user/login
But hidden in the decompiled strings:


POST /api/v2/admin/override
Bingo — hidden endpoint.

🧩 Step 2 — Crawl the JavaScript
Modern SPAs (React, Vue, Angular) often include API routes in JS bundles.

🛠️ Open Chrome DevTools → Sources → Search for "api/" or "/v1/"

You may find endpoints like:


GET /api/v1/internal/price_override
POST /api/v1/system/refresh_cache
These usually aren't documented, but they exist on the server.

🔓 Step 3 — Check Unauthenticated Access
Once you discover an endpoint, don't assume it's safe. Test:

✔️ Access with no token ✔️ Access with a normal user token ✔️ Access with invalid tokens

Example:


GET /api/v1/admin/users
If this returns data with a normal token — you just found a high severity bug.

💣 Step 4 — Fuzz & Abuse Hidden Endpoints
Now that you've found hidden APIs, try:

🔹 Forced Browsing
Guess variations like:


/api/v1/internal/users
/api/v1/admin/user_list
/api/v1/hidden/backup
🔹 Parameter Tampering
If an endpoint takes user_id, try:


?user_id=1
?user_id=99999
?user_id=-1
Watch for: ✔️ data leaks ✔️ unauthorized access ✔️ unintended actions

🧪 Step 5 — Validate Behavior With Intention
Finding endpoints is one thing — proving impact is another.

Ask: ✔️ Does it expose PII? ✔️ Can it modify data? ✔️ Does it bypass auth checks?

Example high impact:


POST /api/v1/admin/reset_password
With no authorization checks — this is full account takeover potential.

💡 That's the kind of vulnerability that pays top tier.

Step 6: Map Visible Endpoints
Use Burp Suite to capture all API calls while using the application normally.

What you'll see:


POST /api/auth/login
GET /api/users/profile
GET /api/products/list
POST /api/orders/create
Write these down. This is your baseline.

Step 7: Version Enumeration
For every endpoint, test different versions:

Original:


GET /api/users/profile
Test variations:


GET /api/v1/users/profile
GET /api/v2/users/profile
GET /api/v3/users/profile
GET /api/v4/users/profile
GET /v1/api/users/profile
GET /v2/api/users/profile
Real example:

Modern endpoint (v3):


GET /api/v3/orders/123
Response: 403 Forbidden (proper authorization check)
Old endpoint (v1):


GET /api/v1/orders/123
Response: 200 OK
{
  "order_id": 123,
  "customer": "John Doe",
  "total": 499.99,
  "credit_card": "4532-****-****-8821"
}
No authorization check on v1!

Step 8: Platform Path Testing
Test these prefixes for every endpoint:


/api/web/...
/api/mobile/...
/api/app/...
/api/android/...
/api/ios/...
/api/admin/...
/api/internal/...
/api/staff/...
/api/partner/...
/api/developer/...
Real example:

Web endpoint:


GET /api/web/user/settings
Requires: CSRF token + session cookie
Mobile endpoint (same function):


GET /api/mobile/user/settings
Requires: Only JWT token (easier to exploit)
The mobile endpoint had weaker security.

Step 9: Environment/Debug Path Testing

/api/dev/...
/api/test/...
/api/debug/...
/api/staging/...
/api/beta/...
/api/alpha/...
/api/sandbox/...
/api/demo/...
Real bug bounty case:

Found endpoint:


GET /api/debug/users/all
Response:


{
  "users": [
    {"id": 1, "email": "admin@company.com", "password_hash": "..."},
    {"id": 2, "email": "user@example.com", "password_hash": "..."},
    ...
    (50,000+ users with password hashes)
  ]
}
No authentication required.

Step 10: Automated Discovery
Use tools to brute force common paths:

Using ffuf:


ffuf -u https://api.example.com/FUZZ/users/profile \
     -w api-paths.txt \
     -H "Authorization: Bearer YOUR_TOKEN"
Wordlist (api-paths.txt):


api
api/v1
api/v2
api/v3
api/web
api/mobile
api/admin
api/internal
api/debug
api/test
v1/api
v2/api
Using Arjun (parameter discovery):


arjun -u https://api.example.com/users/profile
Finds hidden parameters like:


?admin=true
?debug=1
?internal=yes

**Example 1: The $12,000 Version Bug
Target**: SaaS platform
Visible endpoint:
```text
GET /api/v3/documents/123
Authorization: Bearer token123
Response:


{
  "id": 123,
  "title": "My Document",
  "content": "..."
}
Proper authorization-only returns MY documents.
**Tested old version:**
GET /api/v1/documents/123
Authorization: Bearer token123
Response:


{
  "id": 123,
  "title": "Confidential Report",
  "content": "...",
  "owner_id": 5678,  ← Not me!
  "all_versions": [...],
  "edit_history": [...]
}
No authorization check! Accessed any document by changing the ID.

Impact:200,000+ documents exposed

Example 2: The $1000 Mobile API
Target: Financial app Web API (secure):

POST /api/web/transfer
{
  "from": "account123",
  "to": "account456",
  "amount": 100
}
Requires: 2FA code + CSRF token

Mobile API (same function):

Mobile API skipped the 2FA requirement.
Impact: Unauthorized fund transfers

POST /api/mobile/transfer
{
  "from": "account123",
  "to": "account456",
  "amount": 100
}
Requires: Only JWT token (no 2FA!) Mobile API skipped the 2FA requirement. Impact: Unauthorized fund transfers

Example 3: The $6,000 Debug Endpoint
Target: E-commerce site Found endpoint: GET /api/debug/orders

No authentication required.

Response:


{
  "total_orders": 45000,
  "orders": [
    {
      "order_id": 1,
      "customer_email": "customer1@email.com",
      "total": 299.99,
      "credit_card_last4": "1234"
    },
    ...
  ]
}
All orders from all customers, no auth needed.

Advanced Techniques
Advanced Techniques
Technique 1: HTTP Method Tampering

Visible endpoint:


GET /api/users/123 Response: Basic user info
Try different methods:


POST /api/users/123 ← Might return more data
PUT /api/users/123 ← Might allow updates
DELETE /api/users/123 ← Might allow deletion
PATCH /api/users/123 ← Might allow partial updates
Sometimes different formats have different security.

Technique 3: Case Sensitivity Testing

GET /api/users/profile
GET /API/users/profile
GET /Api/Users/Profile
GET /api/USERS/PROFILE
Some servers handle these differently.

Technique 4: Trailing Slash

GET /api/users/profile
GET /api/users/profile/
GET /api/users/profile//
GET /api/users/profile/..
Technique 5: Subdomain Enumeration

api.example.com
api-v1.example.com
api-old.example.com
api-staging.example.com
api-test.example.com
api-dev.example.com
mobile-api.example.com
internal-api.example.com
Tools You Need
Subfinder

subfinder -d example.com | grep api
Complete Testing Checklist
✅ Version variations (v1, v2, v3, etc.)
✅ Platform paths (web, mobile, admin, internal)
✅ Environment paths (dev, test, debug, staging)
✅ HTTP methods (GET, POST, PUT, DELETE, PATCH)
✅ File extensions (.json, .xml, .php)
✅ Case variations
✅ Trailing slashes
✅ Subdomain enumeration
✅ Parameter discovery
✅ Old documentation (Wayback Machine)
1. Burp Suite
Capture all API traffic

2. ffuf

ffuf -u https://api.example.com/FUZZ -w wordlist.txt
3. Arjun

arjun -u https://api.example.com/endpoint
4. waybackurls

waybackurls example.com | grep api
5. SubFinder

subfinder -d example.com
🔥 Pro Tips That Separate Juniors from Pros
✅ Always test both GET & POST — same endpoint can behave differently ✅ Check all environments — prod/test/staging endpoints sometimes leak

📝 How to Write a Winning Bug Report
High payouts depend on clear, reproducible reports.

Include:

Summary: What's broken
Steps: Exactly how to reproduce
Requests: Endpoint + method
Response: What the server returns
Impact: Why this matters
PoC Script: Automate if possible
Example


POST /api/v1/admin/reset_password
Auth: None
Payload: {"user_id": "12345", "new_password": "P@ssw0rd"}
Response:
{"status": "success"}
Impact:
Unauthenticated attacker can reset any user's password.
The Fastest Route to $10k
Week 1: Pick one target, map ALL visible endpoints

Week 2: Test version variations for each endpoint

Week 3: Test platform/environment variations

Week 4: Automate with ffuf + custom wordlists

Focus on:

Financial apps (higher payouts)
SaaS platforms (many API versions)
Apps with mobile + web versions
One critical finding = $5k-$15k

Final Tips
1. Old is gold

v1 endpoints often have no security
Companies forget they exist
2. Mobile APIs are weaker

Developers assume mobile = secure
Often skip 2FA, CSRF protection
3. Debug endpoints are treasure

/api/debug/...
/api/test/...
Usually zero authentication
4. Document everything

Keep a spreadsheet of all endpoints tested
Track patterns across different targets
5. Automate the boring parts

Use scripts for version enumeration
Build custom wordlists from patterns you see
Start Today
Pick a bug bounty program
Use Burp to capture visible endpoints
Test just ONE endpoint with all variations
Document your findings
Scale up
Hidden endpoints are the highest ROI in bug bounty hunting.

Everyone tests the login form. Nobody tests /api/v1/debug/users.

Be the nobody.

👏 Clap if this helps you find your first hidden endpoint 💬 Comment your biggest API discovery 🔔 Follow for more bug bounty techniques

#BugBounty #APIHacking #CyberSecurity #EthicalHacking #BugBountyTips #HiddenAPIs #SecurityResearch #InfoSec #HackerOne #Bugcrowd







I learned early that “not found” often means “not looked at.” In large systems, endpoints die, versions split, and shadow routes persist on backends or in old mobile apps. Those forgotten endpoints are low-noise, high-impact targets. This article walks you through the mindset, the techniques and real-case archetypes that turn a casual 404 into a serious payout without being noisy or reckless.

The forgotten-endpoint phenomenon
Forgotten endpoints aren’t glamorous. They’re leftovers from migrations, abandoned feature branches, mobile clients that never got updated or configuration files left in build artifacts. Typical origins:

API versioning drift (/api/v1/ still running while /api/v3/ is live)
Developer debug routes and admin stubs (/debug/, /admin_old/)
Old mobile app endpoints that the frontend stopped using but the backend still serves
Misrouted CDN or caching configurations that expose archive paths
Press enter or click to view image in full size

Why they matter: those endpoints often bypass newer protections (auth checks, input validation, CSP) introduced in later versions. That mismatch is what turns a low-signal path into a high-impact hole.

How I hunt forgotten endpoints
You don’t need a supercomputer just curiosity and a predictable pipeline. Here are the methods I use every time.

Historical recon (Wayback + gau)
Historic URLs give you a map of what used to exist.

gau target.com | grep -E "/v1/|/old/|/api/"
waybackurls target.com | grep -E "beta|staging|old|v1"
Collect everything, then filter for paths that look like API routes, admin panels or files (.env, .json, .bak).

2. Smart wordlist expansion

Generic wordlists miss bespoke names. Merge commons (dev, staging, backup) with app-specific tokens (URLs and path fragments you find in JS). Example fuzz paths to try:

/api/v1/, /api/old/, /admin_old/, /debug/, /backup/, /staging/, /mobile/v1/
3. JavaScript reconnaissance

JS bundles are gold. They leak internal endpoints, feature flags, and potentially forgotten paths.

# extract paths from JS
cat all.js | grep -Eo "(\/[a-zA-Z0-9_\/\-]{3,})" | sort -u
Look for /v1/, /internal/, /svc/, /upload/, or anything that looks like an API path.

4. Targeted probing

Probe likely paths with httpx (or Burp for manual inspection). Check for subtle differences in headers, content-length, or behavior that indicate the endpoint exists but returns 404/403 for normal access.

httpx -l paths.txt -mc 200,403,500 -silent
Small differences are clues an extra header, a different server banner, or a redirect tells you the code path still runs.

How forgotten endpoints yield real bugs
Below are anonymized case archetypes inspired by real reports. I’ll keep destructive details out but I’ll explain the core mechanics so you learn the pattern.

Write on Medium
Case A. The deprecated API (IDOR by omission)

An old API /v1/get_user returned user details by numeric ID and relied on a front-end session check that was removed in later versions. The new API used JWT + scopes, but /v1/ still accepted unauthenticated requests — a logical mismatch. Result: an attacker could enumerate IDs and retrieve data that the modern API protected. Fix: decommission /v1/ or add consistent auth checks across versions.

Case B. The leftover config (secrets in build artifacts)

A staged admin endpoint /admin_old/config.json remained accessible and contained non-rotated keys used by a CI process. The keys were scoped and auditable, but they allowed privileged API calls. Result: sensitive access to internal tooling large bounty. Fix: remove secrets from artifacts, use vaults, rotate keys on deprecation.

Case C. Legacy upload API (unsafe file handling)

A legacy image upload endpoint allowed certain file types and never updated server-side validation when the stack changed. Modern uploads used safe libraries; the old route didn’t. By abusing content-type handling and upload path resolution, an attacker could place a payload accessible by a route the webserver executed. Result: high-severity impact. Fix: unify upload handling and remove deprecated upload endpoints.

Turning “404” into a lead checklist for follow-ups

When you hit a 404 do these quick checks before moving on:

Inspect headers: does Server, X-Powered-By, or Via differ from other 404 ?
Try nearby paths: add /old, /v1, /admin, /backup.
Check for soft 404s: compare body lengths and titles versus canonical 404 pages.
Look in JS for references to the path (it might be hardcoded in an old client).
Search Wayback / archived API docs for the endpoint semantics.
These small clues tell you whether the 404 is a real dead end or a sign of a shadow route.

Automating discovery

Scripted approaches speed things up without blasting a target:

Build a merged paths list: historical + JS-extracted + custom wordlist.
Filter with httpx for interesting status codes and content-length variance.
Run low-noise checks (HEAD requests first, then GET only on promising hits).
Feed live endpoints into nuclei or your custom template that checks for auth differences, interesting headers, or leaked data shapes.
cat wayback_paths.txt js_paths.txt custom_words.txt | sort -u > paths_all.txt
httpx -l paths_all.txt -method HEAD -silent -o head_results.txt
Responsible disclosure & defensive takeaways
If you find something sensitive, follow the target’s bug bounty or disclosure policy. Don’t exfiltrate data; document behavior and give clear repro steps that show impact without harvesting secrets.

For engineering teams, the defensive checklist is short and effective:

Maintain an authoritative API inventory and retire versions explicitly.
Enforce deprecation notices and auto-block old clients at gateways.
Scan build artifacts and releases for exposed configs/secrets.
Run automated smoke tests that validate new auth and validation logic across versions.
A mindset, not just a technique
The best bug hunting moves are patient and curious. A 404 is rarely the end of a story it’s a bookmark. Treat every “not found” as a hypothesis: either that path died cleanly or it hides a relic that exposes modern systems. That curiosity combined with careful, low-noise tooling is how I turned forgotten endpoints into serious bounties.

If this write-up helped you look at “not found” a little differently, consider supporting my research and caffeine supply












