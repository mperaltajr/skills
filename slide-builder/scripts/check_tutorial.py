#!/usr/bin/env python3
"""check_tutorial.py: is Slide-Lab-Tutorial.html still true to the code?

The tutorial quotes button labels, option counts and timings. Each of those has
gone stale before (a "NONE" button and "+1 / +2 / +3 more" options that no
longer existed, "one design per slide" after the default became three). This
check fails when the tutorial and the code disagree:

  1. a retired phrase is in the tutorial (see RETIRED below)
  2. a button label listed in the tutorial's facts block ("labels") is not found
     in build_review.py, or the page shows a label (class="ui") that is not in
     that list
  3. options_per_slide / options_per_slide_revision in the facts block differ
     from slide-builder/settings.json
  4. the tutorial contains an em-dash (U+2014)
  5. the page shows a fact (data-f="...") that the facts block does not have,
     or whose text differs from the facts block (the page was not rebuilt
     with docs/tutorial/assemble.py after the facts changed)

Run it whenever build_review.py, register_template.py, publish_cleanup.py,
check_done.py or settings.json change, and before sharing the tutorial.

Run:  py -3 scripts/check_tutorial.py [--tutorial <path>]
Exit: 0 pass | 1 problems found (listed) | 2 a file is missing or unreadable
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent                      # slide-builder/
ROOT = SKILL.parent                      # the skills folder
DEFAULT_TUTORIAL = ROOT / "Slide-Lab-Tutorial.html"
BUILD_REVIEW = HERE / "build_review.py"
SETTINGS = SKILL / "settings.json"

EM_DASH = "—"

# (what to report, regex). Matched against the tutorial with embedded images
# removed, so base64 picture data cannot trigger a false hit.
RETIRED = [
    ('a "NONE" button', re.compile(r"\bNONE\b")),
    ('"+1" (the old more-options picker)', re.compile(r"\+1\b")),
    ('"+3 more"', re.compile(r"\+3 more", re.I)),
    ('"one design per slide"', re.compile(r"one design per slide", re.I)),
    ('"worth a minute"', re.compile(r"worth a minute", re.I)),
    ('"/feedback" (help is /slidelab-log)', re.compile(r"/feedback\b", re.I)),
    ('"register.html" (registration is in chat)', re.compile(r"register\.html", re.I)),
    ('"Example-Registration" (that file no longer exists)', re.compile(r"Example-Registration", re.I)),
]

FACTS_RE = re.compile(
    r'<script[^>]*id="slidelab-facts"[^>]*>(.*?)</script>', re.S | re.I)
DATA_URI_RE = re.compile(r"data:[a-z/+.-]+;base64,[A-Za-z0-9+/=]+", re.I)
UI_RE = re.compile(r'<span class="ui(?: [^"]*)?">(.*?)</span>', re.S)
DATA_F_RE = re.compile(r'<(\w+)\b[^>]*\sdata-f="([^"]+)"[^>]*>(.*?)</\1>', re.S)


def _norm(text: str) -> str:
    """Page-source text as a user reads it: entities decoded, an em-dash
    between words written as a comma (the tutorial never uses em-dashes)."""
    text = html.unescape(text)
    text = re.sub(r"\s*—\s*", ", ", text)
    return re.sub(r"\s+", " ", text)


def _label_in_source(label: str, source: str) -> bool:
    if label in source:
        return True
    # Pick buttons are generated: f'...>PICK {letter}</button>'
    m = re.fullmatch(r"PICK ([A-Z])", label)
    return bool(m) and "PICK {letter}" in source


def _get(facts: dict, path: str):
    cur = facts
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def check(tutorial: Path) -> list[str]:
    problems: list[str] = []
    page = tutorial.read_text(encoding="utf-8")
    source = _norm(BUILD_REVIEW.read_text(encoding="utf-8"))
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    text = DATA_URI_RE.sub("", page)

    # 4. em-dashes
    n_dash = page.count(EM_DASH)
    if n_dash:
        lines = sorted({i for i, ln in enumerate(page.splitlines(), 1) if EM_DASH in ln})
        problems.append(f"{n_dash} em-dash(es) on line(s) {', '.join(map(str, lines[:15]))}"
                        + (" ..." if len(lines) > 15 else ""))

    # 1. retired phrases
    for what, rx in RETIRED:
        hits = [i for i, ln in enumerate(text.splitlines(), 1) if rx.search(ln)]
        if hits:
            problems.append(f"retired phrase {what} on line(s) {', '.join(map(str, hits[:10]))}")

    # facts block
    m = FACTS_RE.search(page)
    if not m:
        problems.append('no facts block (<script type="application/json" id="slidelab-facts">)')
        return problems
    try:
        facts = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        problems.append(f"facts block is not valid JSON: {exc}")
        return problems

    # 2. labels
    labels = facts.get("labels") or []
    if not labels:
        problems.append('facts block has no "labels" list')
    for label in labels:
        if not _label_in_source(label, source):
            problems.append(f'label "{label}" is not in build_review.py (renamed or removed?)')
    for shown in sorted({html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
                         for s in UI_RE.findall(text)}):
        if shown not in labels:
            problems.append(f'the page shows label "{shown}" but it is not in the facts "labels" list')

    # 3. option counts
    for key in ("options_per_slide", "options_per_slide_revision"):
        if facts.get(key) != settings.get(key):
            problems.append(f"{key}: tutorial says {facts.get(key)!r}, settings.json says {settings.get(key)!r}")

    # 5. every fact the page shows exists, and is written in as the facts say
    for _tag, key, shown in DATA_F_RE.findall(text):
        value = _get(facts, key)
        if value is None:
            problems.append(f'the page shows fact "{key}" but the facts block has no such entry')
        elif html.unescape(shown).strip() != str(value):
            problems.append(f'fact "{key}" reads "{html.unescape(shown).strip()[:60]}" on the page '
                            f'but "{str(value)[:60]}" in the facts block (re-run docs/tutorial/assemble.py)')

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tutorial", type=Path, default=DEFAULT_TUTORIAL)
    args = ap.parse_args()
    for f in (args.tutorial, BUILD_REVIEW, SETTINGS):
        if not f.is_file():
            print(f"MISSING: {f}")
            return 2
    problems = check(args.tutorial)
    if problems:
        print(f"TUTORIAL CHECK FAILED: {args.tutorial}")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"Tutorial check passed: {args.tutorial}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
