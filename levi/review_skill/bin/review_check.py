#!/usr/bin/env python3
"""review_check.py — mechanical half of the LEVI Review Skill.

Board rules enforced:
  1. Every tool/action from the checklist has a log file or output (artifact exists).
  2. All output is non-zero bytes.
  3. Output matches expected good format and size (JSON parses, md has sections,
     shell has curl, sane minimum sizes).

Usage:
  python3 review_check.py --workdir <dir> --phase {phase1,phase2,discovery,all}
                          [--out review_draft.md]

Writes a markdown draft verdict table. Exit 0 = all PASS, 1 = any FAIL.
Human reviewer judgment (tick-without-trace, size sanity vs corpus) still applies
on top — see review_skill/SKILL.md.
"""
import argparse, glob as globmod, json, os, sys

# skill -> [(path-or-glob, kind, params)]
# kinds: file | dir | json | md | sh | glob
MANIFEST = {
    "phase1": {
        "spider_harvest":          [("js_inventory/manifest.json", "json", {}),
                                    ("raw", "dir", {})],
        "lazy_loaded_chunks":      [("raw/chunks", "dir", {}),
                                    ("chunk_manifest.json", "json", {})],
        "historical_js":           [("historical", "dir", {}),
                                    ("diff_old_new.md", "md", {"min_lines": 5})],
        "sourcemap_harvest":       [("sourcemaps", "dir", {})],
        "anti_automation_fetch":   [("fetch_log.md", "md", {"min_lines": 5})],
        "store_normalize":         [("normalized", "dir", {}),
                                    ("inventory_final.json", "json", {})],
    },
    "phase2": {
        "jsluice_jxscout_tools":   [("jsluice_out", "dir", {})],
        "waymore_tools":           [("waymore_out", "dir", {})],
        "chrome_devtools_tools":   [("devtools_notes.md", "md", {"min_lines": 5})],
        "dangerous_functions_gadgets": [("gadgets.json", "json", {})],
        "params_routes":           [("routes_params.md", "md", {"min_lines": 5})],
        "api_analysis":            [("api_map.md", "md", {"min_lines": 5})],
        "library_analysis":        [("libraries.md", "md", {"min_lines": 5})],
        "framework_tech":          [("tech_choices.md", "md", {"min_lines": 5})],
        "feature_map":             [("feature_map.md", "md", {"min_lines": 5})],
        "secrets_analysis":        [("secrets_candidates.json", "json", {})],
        "report_output":           [("report.md", "md", {"min_lines": 20,
                                        "must_contain": ["CONFIRMED"]}),
                                    ("curl_commands.sh", "sh", {})],
    },
    "discovery": {
        "generic_routes":          [("discovery/generic_routes.txt", "file", {})],
        "generic_files":           [("discovery/generic_files.txt", "file", {})],
        "app_specific_files":      [("discovery/app_specific.txt", "file", {})],
        "bugbounty_report_intel":  [("discovery/writeup_patterns.md", "md", {"min_lines": 5})],
        "api_discovery":           [("discovery/api_surface.md", "md", {"min_lines": 5})],
        "ffuf_workflow":           [("discovery/ffuf_*.json", "glob", {})],
        "onelistforall_micro":     [("discovery/olfa_*.txt", "glob", {})],
        "js_to_wordlist":          [("custom_list.txt", "file", {"min_lines": 10})],
        "phases_generic_specific": [("discovery/phase_log.md", "md", {"min_lines": 5})],
    },
}


def check_one(workdir, pattern, kind, params):
    """Return (ok, detail)."""
    full = os.path.join(workdir, pattern)
    if kind == "glob":
        matches = [m for m in globmod.glob(full) if os.path.isfile(m)]
        if not matches:
            return False, f"no files match `{pattern}` — claimed run has no output"
        zero = [m for m in matches if os.path.getsize(m) == 0]
        if zero:
            return False, f"zero-byte output: {', '.join(zero)}"
        return True, f"{len(matches)} file(s), all non-zero"
    if not os.path.exists(full):
        return False, f"missing `{pattern}` — no log file or output"
    if kind == "dir":
        if not os.path.isdir(full):
            return False, f"`{pattern}` exists but is not a directory"
        files = [os.path.join(r, f) for r, _, fs in os.walk(full) for f in fs]
        live = [f for f in files if os.path.getsize(f) > 0]
        if not live:
            return False, f"`{pattern}/` empty or all zero-byte"
        return True, f"{len(live)} non-zero file(s)"
    # file-based kinds
    if os.path.getsize(full) == 0:
        return False, f"`{pattern}` is zero bytes"
    text = open(full, errors="replace").read()
    if kind == "json":
        try:
            json.loads(text)
        except Exception as e:
            return False, f"`{pattern}` is not valid JSON: {e}"
        return True, "valid JSON, non-zero"
    if kind == "md":
        lines = text.splitlines()
        ml = params.get("min_lines", 1)
        if len(lines) < ml:
            return False, f"`{pattern}` has {len(lines)} lines, expected >= {ml} (too small to be real)"
        for needle in params.get("must_contain", []):
            if needle not in text:
                return False, f"`{pattern}` missing required marker `{needle}`"
        return True, f"{len(lines)} lines, markers present"
    if kind == "sh":
        if "curl" not in text:
            return False, f"`{pattern}` contains no curl commands"
        n = text.count("curl ")
        return True, f"{n} curl command(s)"
    return True, "exists, non-zero"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--phase", default="all",
                    choices=["phase1", "phase2", "discovery", "all"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    workdir = a.workdir
    phases = ["phase1", "phase2", "discovery"] if a.phase == "all" else [a.phase]

    rows, fails = [], 0
    for ph in phases:
        for skill, artifacts in MANIFEST[ph].items():
            reasons, ok_all = [], True
            for pattern, kind, params in artifacts:
                ok, detail = check_one(workdir, pattern, kind, params)
                reasons.append(("PASS" if ok else "FAIL") + f" — {detail}")
                ok_all = ok_all and ok
            verdict = "PASS" if ok_all else "FAIL"
            fails += 0 if ok_all else 1
            rows.append((ph, skill, verdict, reasons))

    # zero-byte sweep (board rule 2, whole tree)
    zero_all = []
    for r, _, fs in os.walk(workdir):
        for f in fs:
            p = os.path.join(r, f)
            if os.path.getsize(p) == 0:
                zero_all.append(os.path.relpath(p, workdir))

    out = ["# Review draft (mechanical) — " + workdir, "",
           "| Phase | Skill | Verdict | Checks |",
           "|-------|-------|---------|--------|"]
    for ph, skill, verdict, reasons in rows:
        icon = "✅" if verdict == "PASS" else "⬜"
        out.append(f"| {ph} | {icon} {skill} | {verdict} | {'; '.join(reasons)} |")
    out += ["",
            f"**Failed skills:** {fails} / {len(rows)}",
            "",
            "## Zero-byte sweep (whole workdir)"]
    out.append("none — clean" if not zero_all else
               "\n".join(f"- [ ] `{z}` — zero bytes" for z in zero_all))
    out += ["",
            "> Mechanical result only. The human reviewer still owes: tick-without-trace",
            "> audit, size-sanity vs corpus, secrets-redaction check — see SKILL.md Steps 2.6, 15, 16."]

    out_path = a.out or os.path.join(workdir, "review_draft.md")
    open(out_path, "w").write("\n".join(out) + "\n")
    print(f"wrote {out_path}: {len(rows)-fails}/{len(rows)} PASS")
    if zero_all:
        print(f"WARNING: {len(zero_all)} zero-byte file(s) in workdir")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
