#!/usr/bin/env python3
"""secrets_scan.py — two-engine secret scan over a JS directory (stdlib only).

Engine 1: known-regex patterns (AWS, GCP, GitHub, Slack, Stripe, JWT, private
keys, generic api_key/token assignments, DB URLs, webhooks).
Engine 2: Shannon-entropy scan over string literals (>= 20 chars, >= 4.5 bits).

Every hit is a CANDIDATE, never a confirmed leak. Obvious placeholders
(test/example/xxx/changeme) are auto-marked NEGATIVE with a reason.

Usage:
    python3 secrets_scan.py <js_dir> [-o candidates.json] [--entropy 4.5]

Output JSON entries:
    {file, line, type: "regex"|"entropy", pattern_name, value_redacted,
     context, verdict: "CANDIDATE"|"NEGATIVE", reason}
Values are redacted (first 4 chars + length). chmod 600 the output file.
NEVER live-test a candidate secret without explicit user approval.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter

# (name, compiled_regex, value_group_index)
PATTERNS = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), 0),
    ("aws_secret_key", re.compile(r"(?i)aws_secret[^A-Za-z0-9_]{0,12}[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9/+=]{40})\b"), 1),
    ("github_token", re.compile(r"\b(ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghu_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,})\b"), 1),
    ("gitlab_token", re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"), 0),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"), 0),
    ("slack_webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"), 0),
    ("stripe_key", re.compile(r"\b((?:sk|rk|pk)_live_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,})\b"), 1),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), 0),
    ("twilio_key", re.compile(r"\b(AC[a-f0-9]{32}|SK[a-f0-9]{32})\b"), 1),
    ("sendgrid_key", re.compile(r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b"), 0),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"), 0),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), 0),
    ("generic_secret_assign", re.compile(
        r"(?i)\b(api[_-]?key|apikey|secret|token|passwd|password|auth[_-]?key|client[_-]?secret)\b"
        r"\s*[:=]\s*[\"']([^\"']{8,200})[\"']"), 2),
    ("db_url", re.compile(
        r"(?i)\b(postgres(?:ql)?|mongodb(?:\+srv)?|mysql|redis)://[^:/?#\s:]+:[^@/?#\s]+@[^\s\"'<>]+"), 0),
]

PLACEHOLDER_WORDS = ("test", "example", "xxx", "changeme", "your_", "my_", "dummy",
                     "sample", "placeholder", "todo", "fixme", "null", "undefined",
                     "abcdef", "123456", "aaaaaa", "xxxxxx")

COMMON_WORDS = frozenset("""
the and for are but not you all any can had her was one our out day get has him
his how its may new now old see two way who boy did its let put say she too use
function return const var let this that with from have will would there their
what when make like time just know take into your more them than then than
""".split())

STRING_RE = re.compile(r'''(["'`])((?:\\.|(?!\1)[^\\]){20,300})\1''')


def shannon(s):
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def redact(value):
    head = value[:4]
    return "%s…(len %d)" % (head, len(value))


def is_placeholder(value):
    v = value.lower()
    return any(w in v for w in PLACEHOLDER_WORDS)


def looks_like_sentence(s):
    words = re.findall(r"[a-z]{3,}", s.lower())
    if len(words) < 3:
        return False
    common = sum(1 for w in words if w in COMMON_WORDS)
    return common >= 3


def scan_file(path):
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
        # Engine 1: known regexes
        for name, rx, group in PATTERNS:
            for m in rx.finditer(line):
                value = m.group(group)
                entry = {
                    "file": path,
                    "line": lineno,
                    "type": "regex",
                    "pattern_name": name,
                    "value_redacted": redact(value),
                    "context": stripped[:160],
                    "verdict": "CANDIDATE",
                    "reason": "",
                }
                if is_placeholder(value):
                    entry["verdict"] = "NEGATIVE"
                    entry["reason"] = "placeholder-like value"
                hits.append(entry)
        # Engine 2: entropy on string literals
        for m in STRING_RE.finditer(line):
            value = m.group(2)
            if len(value) < 20 or " " in value[:12] and looks_like_sentence(value):
                if looks_like_sentence(value):
                    continue
            if len(set(value)) < 8:  # low alphabet diversity, e.g. "aaaaaaaa..."
                continue
            h = shannon(value)
            if h >= ARGS.entropy:
                entry = {
                    "file": path,
                    "line": lineno,
                    "type": "entropy",
                    "pattern_name": "high_entropy_string_%.1f" % h,
                    "value_redacted": redact(value),
                    "context": stripped[:160],
                    "verdict": "CANDIDATE",
                    "reason": "",
                }
                if is_placeholder(value):
                    entry["verdict"] = "NEGATIVE"
                    entry["reason"] = "placeholder-like value"
                hits.append(entry)
    return hits


def main():
    global ARGS
    ap = argparse.ArgumentParser(description="Two-engine secret scan over a JS directory.")
    ap.add_argument("js_dir", help="directory of JS files (use normalized/)")
    ap.add_argument("-o", "--output", default="candidates.json", help="output JSON path")
    ap.add_argument("--entropy", type=float, default=4.5, help="entropy threshold bits/char")
    ARGS = ap.parse_args()

    results = []
    n_files = 0
    for root, _dirs, files in os.walk(ARGS.js_dir):
        for fn in sorted(files):
            if not fn.endswith(".js"):
                continue
            n_files += 1
            results.extend(scan_file(os.path.join(root, fn)))

    # dedupe on (file, line, pattern_name, value_redacted)
    seen = set()
    uniq = []
    for r in results:
        key = (r["file"], r["line"], r["pattern_name"], r["value_redacted"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)

    with open(ARGS.output, "w", encoding="utf-8") as f:
        json.dump(uniq, f, indent=2)
    try:
        os.chmod(ARGS.output, 0o600)
    except OSError:
        pass

    cand = sum(1 for r in uniq if r["verdict"] == "CANDIDATE")
    neg = len(uniq) - cand
    sys.stderr.write("scanned %d files -> %d hits (%d CANDIDATE, %d NEGATIVE) -> %s\n"
                     % (n_files, len(uniq), cand, neg, ARGS.output))


if __name__ == "__main__":
    main()
