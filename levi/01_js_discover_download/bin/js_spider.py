#!/usr/bin/env python3
"""js_spider.py -- Phase 1 helper for LEVI 01_js_discover_download (spider-harvest).

Crawls the target app (bounded depth, same-origin by default), extracts every
<script src> and inline <script> body, downloads the files (sha256-deduped),
probes <file>.js.map for each downloaded file, and writes manifest.json.

Stdlib only: urllib + html.parser. No third-party dependencies.

Usage:
    python3 js_spider.py --target https://app.example.com \
        --outdir ./js_inventory --max-depth 2
    python3 js_spider.py --target https://app.example.com --allow-cross-origin
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SOURCE_MAP_RE = re.compile(r"//#\s*sourceMappingURL=(\S+)")


class PageParser(HTMLParser):
    """Extracts <script src>, inline <script> bodies, and <a href> links."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts = []          # (src or None, inline_body or None)
        self.links = []
        self._in_script = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self._in_script = True
            self._buf = []
            self.scripts.append((attrs.get("src"), None))
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_data(self, data):
        if self._in_script:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script:
            self._in_script = False
            src, _ = self.scripts[-1]
            body = "".join(self._buf).strip()
            self.scripts[-1] = (src, body if body else None)


def fetch(url, timeout=15):
    """GET a URL. Returns (status, headers_dict, body_bytes) or (None, {}, b'')
    on failure, with the error string in headers_dict['_error']."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return e.code, dict(e.headers or {}), body
    except Exception as e:  # URLError, timeout, SSL errors, ...
        return None, {"_error": "%s: %s" % (type(e).__name__, e)}, b""


def sha16(data):
    return hashlib.sha256(data).hexdigest()[:16]


def canonical(url):
    """Strip query + fragment for download dedupe keys."""
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def main():
    ap = argparse.ArgumentParser(description="LEVI Phase-1 JS spider (stdlib only)")
    ap.add_argument("--target", required=True, help="Target base URL, e.g. https://app.example.com")
    ap.add_argument("--outdir", default="js_inventory", help="Output dir (created if missing)")
    ap.add_argument("--max-depth", type=int, default=2, help="Crawl depth (0 = target page only)")
    ap.add_argument("--same-origin-only", dest="same_origin_only", action="store_true",
                    default=True, help="Only crawl/download same-origin URLs (default: on)")
    ap.add_argument("--allow-cross-origin", dest="same_origin_only", action="store_false",
                    help="Also crawl cross-origin links (NOT recommended)")
    ap.add_argument("--max-pages", type=int, default=200, help="Page cap per run")
    ap.add_argument("--timeout", type=int, default=15, help="Per-request timeout seconds")
    ap.add_argument("--delay", type=float, default=0.5, help="Politeness delay between requests")
    args = ap.parse_args()

    target = args.target.rstrip("/")
    tparts = urllib.parse.urlsplit(target)
    if not tparts.scheme or not tparts.netloc:
        sys.exit("ERROR: --target must be a full URL like https://app.example.com")

    raw = os.path.join(args.outdir, "raw")
    inline_d = os.path.join(raw, "inline")
    maps_d = os.path.join(raw, "maps")
    for d in (raw, inline_d, maps_d):
        os.makedirs(d, exist_ok=True)

    manifest = {"target": target, "files": [], "pages_crawled": [], "errors": []}
    seen_pages, seen_downloads = set(), set()
    failures = []

    def log_fail(url, why, referrer=""):
        failures.append({"url": url, "why": why, "referrer": referrer})

    def same_origin(url):
        return urllib.parse.urlsplit(url).netloc == tparts.netloc

    # --- dead-path baseline: the false-positive control for the whole run ---
    dead_url = target + "/this-path-definitely-does-not-exist-9f3k2"
    d_status, _, d_body = fetch(dead_url, args.timeout)
    baseline_hash = hashlib.sha256(d_body).hexdigest() if d_body else None
    manifest["baseline"] = {
        "dead_path": dead_url, "status": d_status,
        "body_sha256": baseline_hash, "body_size": len(d_body),
    }
    time.sleep(args.delay)

    # --- bounded BFS crawl ---
    queue = [(target + "/", 0)]
    pages = []
    while queue and len(pages) < args.max_pages:
        url, depth = queue.pop(0)
        cu = canonical(url)
        if cu in seen_pages:
            continue
        seen_pages.add(cu)
        status, headers, body = fetch(url, args.timeout)
        ctype = headers.get("Content-Type", headers.get("content-type", ""))
        manifest["pages_crawled"].append({"url": url, "status": status,
                                          "content_type": ctype, "depth": depth})
        if status != 200 or not body or "html" not in ctype.lower():
            if status != 200:
                log_fail(url, "page fetch status=%s" % status)
            time.sleep(args.delay)
            continue
        try:
            html = body.decode("utf-8", errors="ignore")
        except Exception as e:
            log_fail(url, "decode error: %s" % e)
            continue
        parser = PageParser()
        try:
            parser.feed(html)
        except Exception as e:
            log_fail(url, "HTML parse error: %s" % e)
        pages.append((url, parser))
        # Regex safety net for malformed markup the parser may miss
        for m in re.finditer(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.I):
            if m.group(1) not in [s for s, _ in parser.scripts if s]:
                parser.scripts.append((m.group(1), None))
        if depth < args.max_depth:
            for href in parser.links:
                absu = urllib.parse.urljoin(url, urllib.parse.urldefrag(href)[0])
                p = urllib.parse.urlsplit(absu)
                if p.scheme not in ("http", "https"):
                    continue
                if args.same_origin_only and p.netloc != tparts.netloc:
                    continue
                if canonical(absu) not in seen_pages:
                    queue.append((absu, depth + 1))
        time.sleep(args.delay)

    # --- download scripts + inline bodies, probe .map per file ---
    def download_script(absu, page_url):
        """Download one script URL. Returns manifest entry dict."""
        entry = {"url": absu, "url_canonical": canonical(absu),
                 "inline_or_file": "file", "page_found_on": page_url,
                 "third_party": not same_origin(absu)}
        if entry["third_party"] and args.same_origin_only:
            entry.update({"downloaded": False, "note": "third-party, recorded not downloaded"})
            return entry
        key = entry["url_canonical"]
        if key in seen_downloads:
            entry.update({"downloaded": False, "note": "duplicate of already-downloaded URL"})
            return entry
        seen_downloads.add(key)
        status, headers, body = fetch(absu, args.timeout)
        time.sleep(args.delay)
        if status != 200 or not body:
            entry.update({"downloaded": False,
                          "note": "fetch failed status=%s err=%s" % (status, headers.get("_error", ""))})
            log_fail(absu, entry["note"], page_url)
            return entry
        full_hash = hashlib.sha256(body).hexdigest()
        if baseline_hash and full_hash == baseline_hash:
            entry.update({"downloaded": False, "false_positive": True,
                          "note": "body matches dead-path baseline (SPA fallback), not JS"})
            return entry
        name = sha16(body) + ".js"
        with open(os.path.join(raw, name), "wb") as f:
            f.write(body)
        entry.update({"downloaded": True, "sha256": full_hash,
                      "size": len(body), "stored_as": "raw/" + name})
        # --- .map probe: conventional URL, then tail comment ---
        map_entry = probe_map(absu, body, name, page_url)
        entry.update(map_entry)
        return entry

    def probe_map(js_url, js_body, js_name, page_url):
        """Probe <file>.js.map and //# sourceMappingURL. Returns dict of map_* fields."""
        result = {"map_probed": True, "map_found": False}
        candidates = []
        base = canonical(js_url)
        if base.lower().endswith(".js"):
            candidates.append(base + ".map")
        try:
            tail = js_body[-2048:].decode("utf-8", errors="ignore")
            m = SOURCE_MAP_RE.search(tail)
            if m:
                sm = m.group(1).strip()
                if sm.startswith("data:"):
                    result["map_source"] = "inline-data-uri (decode manually)"
                else:
                    resolved = urllib.parse.urljoin(js_url, sm)
                    if resolved not in candidates:
                        candidates.append(resolved)
                    result["map_advertised"] = sm
        except Exception:
            pass
        for map_url in candidates:
            if not same_origin(map_url) and args.same_origin_only:
                continue
            status, headers, body = fetch(map_url, args.timeout)
            time.sleep(args.delay)
            if status == 200 and body:
                try:
                    d = json.loads(body.decode("utf-8", errors="ignore"))
                    assert isinstance(d.get("sources"), list)
                except Exception:
                    log_fail(map_url, "map probe returned non-map JSON/HTML", page_url)
                    continue
                mname = js_name.replace(".js", ".map")
                with open(os.path.join(maps_d, mname), "wb") as f:
                    f.write(body)
                result.update({"map_found": True, "map_url": map_url,
                               "map_sources": len(d["sources"]),
                               "map_has_sources_content": "sourcesContent" in d,
                               "map_stored_as": "raw/maps/" + mname})
                break
            else:
                log_fail(map_url, "map probe status=%s" % status, page_url)
        return result

    for page_url, parser in pages:
        for src, body_text in parser.scripts:
            if src:
                if not src.strip() or src.strip().startswith(("javascript:", "{{", "{%")):
                    log_fail(src, "unresolvable src (template/empty/pseudo-URL)", page_url)
                    continue
                absu = urllib.parse.urljoin(page_url, src.strip())
                if urllib.parse.urlsplit(absu).scheme not in ("http", "https"):
                    log_fail(src, "non-http(s) src", page_url)
                    continue
                manifest["files"].append(download_script(absu, page_url))
            elif body_text:
                # Inline: keep non-empty; tiny non-JSON blobs are noise
                keep = len(body_text) >= 50 or (body_text.startswith("{") and body_text.endswith("}"))
                if not keep:
                    continue
                data = body_text.encode("utf-8")
                full_hash = hashlib.sha256(data).hexdigest()
                key = "inline:" + full_hash
                if key in seen_downloads:
                    continue
                seen_downloads.add(key)
                name = sha16(data) + ".js"
                with open(os.path.join(inline_d, name), "wb") as f:
                    f.write(data)
                manifest["files"].append({
                    "url": None, "sha256": full_hash, "size": len(data),
                    "inline_or_file": "inline", "page_found_on": page_url,
                    "stored_as": "raw/inline/" + name, "downloaded": True,
                    "third_party": False, "map_probed": False,
                    "note": "inline script, no .map applicable",
                })

    manifest["errors"] = failures
    manifest["summary"] = {
        "pages_crawled": len(manifest["pages_crawled"]),
        "scripts_found": len(manifest["files"]),
        "downloaded": sum(1 for f in manifest["files"] if f.get("downloaded")),
        "maps_found": sum(1 for f in manifest["files"] if f.get("map_found")),
        "failures": len(failures),
    }

    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)

    with open(os.path.join(args.outdir, "fetch_log.md"), "a") as f:
        f.write("## js_spider.py run\n\n")
        f.write("- target: %s\n- pages: %d, scripts: %d, downloaded: %d, maps: %d\n"
                % (target, manifest["summary"]["pages_crawled"],
                   manifest["summary"]["scripts_found"],
                   manifest["summary"]["downloaded"],
                   manifest["summary"]["maps_found"]))
        for e in failures:
            f.write("- FAIL %s :: %s (ref: %s)\n" % (e["url"], e["why"], e["referrer"]))
        f.write("\n")

    print(json.dumps(manifest["summary"], indent=1))


if __name__ == "__main__":
    main()
