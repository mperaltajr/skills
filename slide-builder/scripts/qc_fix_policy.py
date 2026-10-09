#!/usr/bin/env python3
"""qc_fix_policy.py — which QC findings Slide Lab fixes without asking.

Owner's decision (2026-10-09): after slide-qc, every Critical and every Major
in the layout/format group is fixed automatically (at most two rounds), and
recorded; Majors in the content group still go to the user, in ONE table with
proposed fixes and one reply, because fixing them rewrites the user's words or
numbers. This file is the one place that says which is which. slide-qc's
report tags each finding with a category key from here, and
apply_qc_fix.py --auto refuses any finding this does not class "auto".

  py -3 scripts/qc_fix_policy.py --list
  py -3 scripts/qc_fix_policy.py classify "slide 3 [overflow] Major: text cut off; slide 5 [headline] Major: topic label"

A finding is written "slide N [category] Severity: text" (the tag and the
severity are optional). With no tag the text is matched against the phrases
below, content phrases first; anything unrecognized is "ask" (never guess a
rewrite of the user's content into an automatic fix). Advisory findings are
never fixed automatically.
"""
from __future__ import annotations

import re
import sys

# category key -> (decision, label, phrases matched when a finding has no tag)
CATEGORIES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # layout / format: fixed automatically
    "text_size": ("auto", "Text under the size floor, or more than 3 body sizes",
                  ("size floor", "under the floor", "under 10.5", "under 9 pt", "under 9pt",
                   "body sizes", "text size", "font size", "typography drift")),
    "overflow": ("auto", "Overflow or clipping",
                 ("overflow", "clipped", "clipping", "cut off", "bleeds", "past the slide")),
    "overlap": ("auto", "Overlapping shapes or text", ("overlap", "obscured", "collid")),
    "arrow_into_box": ("auto", "Arrow runs into a box", ("arrow",)),
    "panel_vanishes": ("auto", "Panel vanishing into the background",
                       ("vanish", "pale fill", "edge cannot be seen", "invisible panel")),
    "chrome": ("auto", "Chrome drift, or takeaway / footnote / source line out of place",
               ("chrome drift", "out of place", "misplaced", "takeaway position",
                "footnote position", "source position", "not under the title")),
    "sample_text": ("auto", "Template sample text or placeholder prompt left on the slide",
                    ("sample text", "placeholder", "lorem", "[add ")),
    "footer_page_number": ("auto", "Missing footer or page number",
                           ("footer", "page number")),
    "axis_unit": ("auto", "Chart axis without a unit", ("axis", "no unit", "missing unit")),
    # The three chart and punctuation rules (owner's rules, 2026-10-09;
    # slide-builder/scripts/chart_rules.py finds them)
    "final_period": ("auto", "A text item ends with a final period",
                     ("final period", "ends with a period", "trailing period")),
    "chart_header": ("auto", "Chart without its header line (\"Chart title, [Unit]\") or "
                             "without a unit",
                     ("chart header", "header line", "no chart title")),
    "legend_position": ("auto", "Chart legend not one row at the chart's top right",
                        ("legend",)),
    "palette": ("auto", "Color palette drift", ("palette", "off-brand color", "off-brand colour")),
    # content: asked, in one table with proposed fixes
    "number_not_in_brief": ("ask", "A number or label that is not in the brief",
                            ("not in the brief", "not in brief", "unsourced number",
                             "number does not match", "figure does not match")),
    "buzzwords": ("ask", "Buzzwords or hedging",
                  ("buzzword", "hedg", "banned word", "weasel", "competitor firm")),
    "headline": ("ask", "Headline that is not a fact, or a topic label",
                 ("topic label", "not an action title", "headline is not", "title is not a",
                  "not a claim", "headline")),
    "bullets_parallel": ("ask", "Bullets not parallel", ("parallel",)),
    "missing_source": ("ask", "Missing source where one was expected",
                       ("missing source", "no source", "source line missing", "source missing")),
    "rewrite": ("ask", "Anything that rewrites words or numbers",
                ("reword", "rewrite", "wording", "rephrase", "change the number")),
}

CONTENT_FIRST = [k for k, v in CATEGORIES.items() if v[0] == "ask"]
LAYOUT = [k for k, v in CATEGORIES.items() if v[0] == "auto"]


def category_of(text: str) -> str:
    """The category key for a finding's text ("" when unrecognized)."""
    m = re.search(r"\[([a-z_]+)\]", text or "")
    if m and m.group(1) in CATEGORIES:
        return m.group(1)
    low = (text or "").lower()
    for key in CONTENT_FIRST + LAYOUT:
        if any(p in low for p in CATEGORIES[key][2]):
            return key
    return ""


def decide(text: str) -> tuple[str, str]:
    """("auto" | "ask" | "none", category). Criticals are always automatic;
    Advisory findings are never fixed automatically; an unrecognized Major is
    asked."""
    low = (text or "").lower()
    cat = category_of(text)
    if re.search(r"\bcritical\b", low):
        return "auto", cat or "critical"
    if re.search(r"\badvisory\b", low):
        return "none", cat
    if not cat:
        return "ask", ""
    return CATEGORIES[cat][0], cat


def split_findings(summary: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;\n]+", summary or "") if p.strip()]


def classify(summary: str) -> list[dict]:
    rows = []
    for item in split_findings(summary):
        d, cat = decide(item)
        m = re.search(r"\bslide\s+(\d{1,3})", item, re.I)
        rows.append({"finding": item, "decision": d, "category": cat,
                     "slide": int(m.group(1)) if m else None})
    return rows


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not argv or argv[0] == "--list":
        print("Critical findings: always fixed automatically.")
        for want, head in (("auto", "Fixed automatically (Major, layout/format)"),
                           ("ask", "Asked, in one table (Major, content)")):
            print(f"\n{head}:")
            for k, (d, label, _) in CATEGORIES.items():
                if d == want:
                    print(f"  [{k}]  {label}")
        print("\nAdvisory findings: never fixed automatically. Unrecognized Majors: asked.")
        return 0
    if argv[0] == "classify" and len(argv) > 1:
        for r in classify(" ; ".join(argv[1:])):
            print(f"{r['decision']:4}  [{r['category'] or '?'}]  {r['finding']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
