#!/usr/bin/env python3
"""gadget_mapper.py — sink/source regex mapping over a JS directory (stdlib only).

Maps dangerous sinks (eval, innerHTML, postMessage listeners, location, ...)
and attacker-controllable sources (location.hash/search, document.referrer,
window.name, message events, URLSearchParams). Every hit is a CANDIDATE:
a sink becomes interesting only after a human traces a data flow from a
source to it (see the dangerous_functions_gadgets skill).

Usage:
    python3 gadget_mapper.py <js_dir> [-o gadgets.json] [--no-sources]

Output JSON entries:
    {file, line, kind: "sink"|"source", sink, source, context_snippet,
     source_trace: null, verdict: "CANDIDATE"}
"source_trace" is filled in by the analyst during data-flow tracing.
"""

import argparse
import json
import os
import re
import sys

SINKS = [
    ("eval", re.compile(r"\beval\s*\(")),
    ("Function_constructor", re.compile(r"\bnew\s+Function\s*\(")),
    ("setTimeout_string", re.compile(r"\bsetTimeout\s*\(\s*[\"'`]")),
    ("setInterval_string", re.compile(r"\bsetInterval\s*\(\s*[\"'`]")),
    ("innerHTML", re.compile(r"\.innerHTML\s*\+?=(?!=)")),
    ("outerHTML", re.compile(r"\.outerHTML\s*\+?=(?!=)")),
    ("document.write", re.compile(r"\bdocument\.write(?:ln)?\s*\(")),
    ("insertAdjacentHTML", re.compile(r"\.insertAdjacentHTML\s*\(")),
    ("jquery_html", re.compile(r"\.\s*html\s*\(")),
    ("jquery_append", re.compile(r"\.\s*append\s*\(")),
    ("location_href_assign", re.compile(r"\blocation\s*\.\s*href\s*=(?!=)")),
    ("location_assign", re.compile(r"(?<![\w$.])location\s*=\s*[\"'`]")),
    ("location_method", re.compile(r"\blocation\s*\.\s*(?:assign|replace)\s*\(")),
    ("postMessage_listener", re.compile(r"addEventListener\s*\(\s*[\"']message[\"']")),
    ("onmessage_assign", re.compile(r"\bonmessage\s*=(?!=)")),
    ("postMessage_send", re.compile(r"\.postMessage\s*\(")),
    ("dangerouslySetInnerHTML", re.compile(r"dangerouslySetInnerHTML")),
    ("vue_v_html", re.compile(r"\bv-html\b")),
    ("ng_bind_html", re.compile(r"ng-bind-html")),
]

SOURCES = [
    ("location.hash", re.compile(r"\blocation\.hash\b")),
    ("location.search", re.compile(r"\blocation\.search\b")),
    ("document.referrer", re.compile(r"\bdocument\.referrer\b")),
    ("document.URL", re.compile(r"\bdocument\.URL\b")),
    ("window.name", re.compile(r"\bwindow\.name\b")),
    ("message_event", re.compile(r"addEventListener\s*\(\s*[\"']message[\"']")),
    ("URLSearchParams", re.compile(r"\bURLSearchParams\b")),
]


def scan_file(path, include_sources):
    hits = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return hits
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        snippet = stripped[:200]
        for name, rx in SINKS:
            if rx.search(line):
                hits.append({
                    "file": path,
                    "line": lineno,
                    "kind": "sink",
                    "sink": name,
                    "source": None,
                    "context_snippet": snippet,
                    "source_trace": None,
                    "verdict": "CANDIDATE",
                })
        if include_sources:
            for name, rx in SOURCES:
                if rx.search(line):
                    hits.append({
                        "file": path,
                        "line": lineno,
                        "kind": "source",
                        "sink": None,
                        "source": name,
                        "context_snippet": snippet,
                        "source_trace": None,
                        "verdict": "CANDIDATE",
                    })
    return hits


def main():
    ap = argparse.ArgumentParser(description="Sink/source mapping over a JS directory.")
    ap.add_argument("js_dir", help="directory of JS files (use normalized/)")
    ap.add_argument("-o", "--output", default="gadgets.json", help="output JSON path")
    ap.add_argument("--no-sources", action="store_true", help="skip source mapping, sinks only")
    args = ap.parse_args()

    results = []
    n_files = 0
    for root, _dirs, files in os.walk(args.js_dir):
        for fn in sorted(files):
            if not fn.endswith(".js"):
                continue
            n_files += 1
            results.extend(scan_file(os.path.join(root, fn),
                                     include_sources=not args.no_sources))

    # dedupe on (file, line, kind, sink/source name)
    seen = set()
    uniq = []
    for r in results:
        key = (r["file"], r["line"], r["kind"], r["sink"] or r["source"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(uniq, f, indent=2)

    n_sink = sum(1 for r in uniq if r["kind"] == "sink")
    n_src = len(uniq) - n_sink
    sys.stderr.write("scanned %d files -> %d hits (%d sinks, %d sources) -> %s\n"
                     % (n_files, len(uniq), n_sink, n_src, args.output))
    sys.stderr.write("NOTE: every hit is CANDIDATE until a source->sink data flow is traced.\n")


if __name__ == "__main__":
    main()
