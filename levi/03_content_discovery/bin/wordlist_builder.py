#!/usr/bin/env python3
"""wordlist_builder.py — JS corpus -> custom_list.txt (stdlib only).

Tokenizes analyzed JS files into a target-specific wordlist:
  - endpoint-ish strings ("/api/v3/users")
  - parameter names (object keys, searchParams.get("..."), query keys)
  - route fragments (path: "/dashboard", router.push("..."))
then splits camelCase/snake_case/kebab-case/path segments, strips framework
noise words, applies a small documented set of high-signal mutations, dedupes,
and writes custom_list.txt (one token per line, priority-ordered) plus an
optional frequency file and build log.

Usage:
  python3 bin/wordlist_builder.py --js-dir normalized/ --out custom_list.txt
  python3 bin/wordlist_builder.py --js-dir normalized/ --api-map api_map.md \\
      --routes routes_params.md --confirmed discovery/generic_routes.txt \\
      --merge custom_list.txt --out custom_list.txt --log discovery/wordlist_build_log.md
"""

import argparse
import os
import re
import sys
from collections import Counter
from datetime import date

# ----------------------------------------------------------------------------
# Framework / language noise: vocabulary of the tooling, not the target.
# Extend here when a new framework's tokens pollute a run (log the extension).
# ----------------------------------------------------------------------------
NOISE_WORDS = {
    # frameworks & build tooling
    "react", "vue", "angular", "svelte", "component", "props", "state",
    "render", "useeffect", "usestate", "useref", "usememo", "usecallback",
    "classname", "webpack", "chunk", "chunks", "runtime", "manifest",
    "polyfill", "vendor", "vendors", "modules", "require", "exports",
    "import", "export", "default", "__webpack_require__", "node",
    # dom / html
    "div", "span", "button", "input", "form", "label", "select", "option",
    "table", "tbody", "thead", "image", "img", "link", "script", "style",
    "header", "footer", "title", "body", "html", "onclick", "onchange",
    # language keywords
    "function", "return", "const", "let", "var", "new", "this", "typeof",
    "instanceof", "async", "await", "promise", "then", "catch", "finally",
    "throw", "error", "errors", "null", "undefined", "true", "false",
    "string", "number", "boolean", "object", "array", "json",
    # generic filler
    "data", "item", "items", "list", "index", "key", "value", "values",
    "name", "type", "types", "id", "test", "tests", "demo", "example",
    "examples", "sample", "foo", "bar", "baz", "lorem", "ipsum", "todo",
    "temp", "tmp", "misc", "other", "unknown",
}

# Filename-ish stems that earn backup-suffix mutations (conservative list).
BACKUP_STEMS = {
    "config", "configuration", "settings", "setting", "env", "backup",
    "dump", "database", "db", "app", "appsettings", "web", "server",
    "package", "composer", "wp-config",
}

# ----------------------------------------------------------------------------
# Extraction regexes (run over raw JS text and over markdown analysis files)
# ----------------------------------------------------------------------------
ENDPOINT_RE = re.compile(r"""["'](/[A-Za-z0-9_\-./?=&%{}:;$+@!~*']{2,160})["']""")
OBJKEY_RE = re.compile(r"""["']([A-Za-z_][A-Za-z0-9_]{2,40})["']\s*:""")
UNQUOTED_KEY_RE = re.compile(r"""[{,]\s*([A-Za-z_][A-Za-z0-9_]{2,40})\s*:""")
SEARCHPARAM_RE = re.compile(r"""get\(\s*["']([A-Za-z_][A-Za-z0-9_\-]{1,40})["']\s*\)""")
ROUTEDEF_RE = re.compile(r"""(?:path|route)\s*:\s*["']([^"']{1,120})["']""")
NAV_RE = re.compile(
    r"""(?:router\.push|navigate|history\.push|redirect)\(\s*["']([^"']{1,120})["']"""
)
QUERYKEY_RE = re.compile(r"""[?&]([A-Za-z_][A-Za-z0-9_]{1,40})=""")

PRIO_API_PATH = 1    # whole API paths first
PRIO_ROUTE = 2       # whole route paths
PRIO_PARAM = 3       # parameter names
PRIO_SPLIT = 4       # split tokens
PRIO_MUTATION = 5    # mutations last


def split_camel(chunk):
    """Split camelCase / PascalCase (incl. acronym boundaries) into words."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", chunk)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    return s.split()


def clean_token(tok):
    tok = tok.strip().strip("/")
    # drop template placeholders down to their static prefix: "/api/${v}" -> "api"
    tok = re.sub(r"\$\{[^}]*\}", "", tok)
    tok = re.sub(r"[:*?]+$", "", tok)
    return tok.strip("/")


def variants(token, prio):
    """Yield (variant, prio) for a raw token: original + split forms."""
    out = {}
    t = clean_token(token)
    if not t or len(t) > 160:
        return out
    low = t.lower()
    out[low] = min(out.get(low, 99), prio)

    chunks = [c for c in re.split(r"[./_\-]+", t) if c]
    words = []
    for chunk in chunks:
        words.extend(split_camel(chunk))
    words = [w.lower() for w in words if w]
    for w in words:
        if 2 <= len(w) <= 40 and w not in NOISE_WORDS:
            out[w] = min(out.get(w, 99), PRIO_SPLIT if prio > PRIO_SPLIT else prio)
    # adjacent path pairs: api/v3 -> "api/v3"
    if "/" in t:
        parts = [p.lower() for p in t.split("/") if len(p) >= 2]
        for a, b in zip(parts, parts[1:]):
            if len(a) <= 40 and len(b) <= 40:
                out[f"{a}/{b}"] = min(out.get(f"{a}/{b}", 99), prio)
    # separator-swapped compounds: internalConsole -> internal-console, etc.
    if len(words) >= 2 and all(2 <= len(w) <= 30 for w in words):
        joined = "".join(words)
        if len(joined) <= 60:
            out[joined] = min(out.get(joined, 99), PRIO_MUTATION)
            out["-".join(words)] = min(out.get("-".join(words), 99), PRIO_MUTATION)
            out["_".join(words)] = min(out.get("_".join(words), 99), PRIO_MUTATION)
    return out


def mutate(token):
    """High-signal mutations only. Returns {variant: PRIO_MUTATION}."""
    out = {}
    m = re.fullmatch(r"v([0-9]{1,2})", token)
    if m:  # version siblings: API rot lives in old versions
        for v in ("v1", "v2", "v3", "v4"):
            if v != token:
                out[v] = PRIO_MUTATION
    if token in ("admin", "administrator"):
        for v in ("admin", "administrator", "administration"):
            if v != token:
                out[v] = PRIO_MUTATION
    if token == "console":
        out["consoles"] = PRIO_MUTATION
    if token in BACKUP_STEMS:  # backup suffixes, filename stems only
        for suf in (".bak", ".old", ".json", ".zip"):
            out[token + suf] = PRIO_MUTATION
    return out


def extract_from_text(text, freq, tokens):
    """Harvest raw tokens from JS/markdown text into tokens {tok: prio}."""
    for m in ENDPOINT_RE.finditer(text):
        raw = m.group(1).split("?")[0]
        prio = PRIO_API_PATH if "/api" in raw or "/v1" in raw or "/v2" in raw or "/v3" in raw else PRIO_ROUTE
        for var, vp in variants(raw, prio).items():
            tokens[var] = min(tokens.get(var, 99), vp)
            freq[var] += 1
        for qm in QUERYKEY_RE.finditer(m.group(1)):
            q = qm.group(1).lower()
            if q not in NOISE_WORDS and len(q) >= 3:
                tokens[q] = min(tokens.get(q, 99), PRIO_PARAM)
                freq[q] += 1
    for rx, prio in ((OBJKEY_RE, PRIO_PARAM), (UNQUOTED_KEY_RE, PRIO_PARAM),
                     (SEARCHPARAM_RE, PRIO_PARAM),
                     (ROUTEDEF_RE, PRIO_ROUTE), (NAV_RE, PRIO_ROUTE)):
        for m in rx.finditer(text):
            raw = m.group(1)
            if "/" in raw:
                for var, vp in variants(raw, prio).items():
                    tokens[var] = min(tokens.get(var, 99), vp)
                    freq[var] += 1
            else:
                for var, vp in variants(raw, prio).items():
                    tokens[var] = min(tokens.get(var, 99), vp)
                    freq[var] += 1


def read_files(js_dir):
    texts = []
    count = 0
    total_bytes = 0
    for root, _, files in os.walk(js_dir):
        for fn in sorted(files):
            if not fn.endswith(".js"):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    data = fh.read()
            except OSError:
                continue
            count += 1
            total_bytes += len(data)
            texts.append(data)
    return texts, count, total_bytes


def main():
    ap = argparse.ArgumentParser(description="JS corpus -> custom_list.txt")
    ap.add_argument("--js-dir", required=True, help="dir of analyzed JS files")
    ap.add_argument("--api-map", help="02_js_analyze/api_map.md (extra token source)")
    ap.add_argument("--routes", help="02_js_analyze/routes_params.md (extra token source)")
    ap.add_argument("--confirmed", nargs="*", default=[],
                    help="discovery/*.txt verified lists to fold back in")
    ap.add_argument("--merge", help="existing custom_list.txt to merge (rebuild mode)")
    ap.add_argument("--out", default="custom_list.txt")
    ap.add_argument("--freq-out", help="top-200 frequency annotations file")
    ap.add_argument("--log", help="build log to append a dated section to")
    ap.add_argument("--max-tokens", type=int, default=50000)
    args = ap.parse_args()

    if not os.path.isdir(args.js_dir):
        print(f"ERROR: --js-dir not found: {args.js_dir}", file=sys.stderr)
        sys.exit(1)

    tokens = {}          # token -> best (lowest) priority
    freq = Counter()

    texts, file_count, total_bytes = read_files(args.js_dir)
    for t in texts:
        extract_from_text(t, freq, tokens)

    for extra in (args.api_map, args.routes):
        if extra and os.path.isfile(extra):
            with open(extra, encoding="utf-8", errors="ignore") as fh:
                extract_from_text(fh.read(), freq, tokens)

    confirmed_count = 0
    for cf in args.confirmed:
        if not os.path.isfile(cf):
            continue
        with open(cf, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == "CONFIRMED" and parts[1].startswith("/"):
                    confirmed_count += 1
                    for var, vp in variants(parts[1], PRIO_API_PATH).items():
                        tokens[var] = min(tokens.get(var, 99), vp)
                        freq[var] += 1

    # mutations (documented families only)
    mut_count = 0
    for tok in list(tokens):
        if tokens[tok] >= PRIO_MUTATION:
            continue
        for var, vp in mutate(tok).items():
            if var not in tokens:
                mut_count += 1
            tokens[var] = min(tokens.get(var, 99), vp)

    # merge existing list on rebuild (union, never silent deletion)
    merged_count = 0
    if args.merge and os.path.isfile(args.merge):
        with open(args.merge, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                t = line.strip()
                if t and not t.startswith("#") and t not in tokens:
                    tokens[t] = PRIO_SPLIT
                    merged_count += 1

    # drop noise that slipped through splitting
    tokens = {t: p for t, p in tokens.items()
              if t not in NOISE_WORDS and 2 <= len(t) <= 120 and t.strip()}

    # priority order, then frequency; cap at --max-tokens
    ordered = sorted(tokens, key=lambda t: (tokens[t], -freq.get(t, 0), t))
    cut = len(ordered) - args.max_tokens
    if cut > 0:
        ordered = ordered[:args.max_tokens]
    else:
        cut = 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        for t in ordered:
            fh.write(t + "\n")

    if args.freq_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.freq_out)), exist_ok=True)
        with open(args.freq_out, "w", encoding="utf-8") as fh:
            fh.write("# top-200 tokens by source frequency\n")
            for t, n in freq.most_common(200):
                fh.write(f"# freq={n} {t}\n")

    if args.log:
        os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
        with open(args.log, "a", encoding="utf-8") as fh:
            fh.write(f"\n## build {date.today().isoformat()}\n")
            fh.write(f"- corpus: {args.js_dir} — {file_count} .js files, {total_bytes} bytes\n")
            fh.write(f"- confirmed lists folded in: {confirmed_count} paths\n")
            fh.write(f"- merged from existing: {merged_count} tokens\n")
            fh.write(f"- mutations emitted: {mut_count} (families: separator-swap, "
                     f"version-siblings v1-v4, admin-family, backup-suffixes on "
                     f"{len(BACKUP_STEMS)} stems)\n")
            fh.write(f"- final: {len(ordered)} tokens (cut {cut} over cap {args.max_tokens})\n")
            fh.write("- noise list: NOISE_WORDS (see script header)\n")

    print(f"wrote {len(ordered)} tokens -> {args.out} "
          f"(from {file_count} js files, +{confirmed_count} confirmed, "
          f"+{merged_count} merged, +{mut_count} mutations, cut {cut})")
    print("top tokens by frequency:")
    for t, n in freq.most_common(15):
        print(f"  {n:6d}  {t}")


if __name__ == "__main__":
    main()
