#!/usr/bin/env python3
"""qc_fix_policy.py — which QC findings Slide Lab fixes without asking.

Owner's decision (2026-10-09): after slide-qc, every Critical and every Major
in the layout/format group is fixed automatically (at most two rounds), and
recorded; findings in the content group go to the user, in ONE table with
proposed fixes and one reply, because fixing them rewrites the user's words or
numbers. A Critical content finding is asked too (2026-10-09, validated fix:
slide-qc never makes content Critical, so one is a reviewer's mistake, and
the user decides it). This file is the one place that says which is which.
slide-qc's report tags each finding with a category key from here, and
apply_qc_fix.py --auto refuses any finding this does not class "auto".

  py -3 scripts/qc_fix_policy.py --list
  py -3 scripts/qc_fix_policy.py classify "slide 3 [overflow] Major: text cut off; slide 5 [headline] Major: topic label"

A finding is written "slide N [category] Severity: text".

  * Findings are split only where a ";" or a new line is followed by
    "slide N". Anything else after a ";" or a new line (fix detail) belongs to
    the finding before it.
  * The severity is read only from its place right after the tag
    ("[tag] Critical:", "Major:", "Advisory:"), never from words in the text
    ("misses the critical number" is not a Critical).
  * The tag is read only from its place after the slide number. It is
    normalized (lowercase, "-" and spaces to "_"), so slide-qc's hyphenated
    tags work, and a few aliases map onto the keys below (ALIASES).
  * The tag can only make a decision more cautious: a layout tag on a text
    that reads like a content finding is asked. With no tag, or a tag that
    is not a key, a finding is never automatic (the phrases below only name
    a likely category for the table).

Order: content category -> ask (whatever the severity); Critical -> auto;
layout Major -> auto; Advisory -> none (never fixed automatically); anything
else -> ask.
"""
from __future__ import annotations

import re
import sys

# category key -> (decision, label, phrases)
# The phrases name a likely category for an untagged finding (for the table;
# never "auto"), and the content phrases also turn a layout-tagged finding
# into a question when its text reads like content.
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
                             "number does not match", "figure does not match", "wrong number")),
    "buzzwords": ("ask", "Buzzwords or hedging",
                  ("buzzword", "hedg", "banned word", "weasel", "competitor firm")),
    "headline": ("ask", "Headline that is not a fact, or a topic label",
                 ("topic label", "not an action title", "headline is not", "title is not a",
                  "not a claim", "headline")),
    "repeats_title": ("ask", "A takeaway or band that repeats the title",
                      ("repeats the title", "repeat the title")),
    "title_load": ("ask", "A long title with a takeaway and a bottom band (title load)",
                   ("title load",)),
    "bullets_parallel": ("ask", "Bullets not parallel", ("parallel",)),
    "missing_source": ("ask", "Missing source where one was expected",
                       ("missing source", "no source", "source line missing", "source missing")),
    "rewrite": ("ask", "Anything that rewrites words or numbers",
                ("reword", "rewrite", "wording", "rephrase", "change the number")),
}

# Tags slide-qc and the checks write that are not keys themselves (after
# normalizing: lowercase, "-" and spaces to "_").
ALIASES: dict[str, str] = {
    "template_sample_text": "sample_text",
    "placeholder_prompt": "sample_text",
    "placeholder_residue": "sample_text",
    "buzzword": "buzzwords",
}

CONTENT_FIRST = [k for k, v in CATEGORIES.items() if v[0] == "ask"]
LAYOUT = [k for k, v in CATEGORIES.items() if v[0] == "auto"]

# Content phrases that turn a layout-tagged finding into a question. The bare
# word "headline" is left out here: "headline cut off" is a layout finding.
_CONTENT_GUARD = tuple(p for k in CONTENT_FIRST for p in CATEGORIES[k][2] if p != "headline")

# "slide N [tag] Severity: text"; every part before the text is optional.
_HEAD = re.compile(
    r"^\s*(?:slide\s+(?P<slide>\d{1,3})\b\s*[:.,-]?\s*)?"
    r"(?:\[(?P<tag>[^\]\n]{1,40})\]\s*)?"
    r"(?:(?P<sev>critical|major|advisory)\s*:)?",
    re.I)


def normalize_tag(tag: str | None) -> str:
    t = re.sub(r"[\s\-]+", "_", (tag or "").strip().lower())
    return ALIASES.get(t, t)


def parse(text: str) -> dict:
    """{"slide", "tag" (normalized, "" if none), "key" (a CATEGORIES key or ""),
    "severity" ("critical" | "major" | "advisory" | ""), "body"}."""
    m = _HEAD.match(text or "")
    tag = normalize_tag(m.group("tag")) if m and m.group("tag") else ""
    return {"slide": int(m.group("slide")) if m and m.group("slide") else None,
            "tag": tag, "key": tag if tag in CATEGORIES else "",
            "severity": (m.group("sev") or "").lower() if m else "",
            "body": (text or "")[m.end():] if m else (text or "")}


def _guess(low: str) -> str:
    for key in CONTENT_FIRST + LAYOUT:
        if any(p in low for p in CATEGORIES[key][2]):
            return key
    return ""


def category_of(text: str) -> str:
    """The category key for a finding: its tag when that is a key, else the
    likely category from the phrases ("" when unrecognized)."""
    p = parse(text)
    return p["key"] or _guess((text or "").lower())


def decide(text: str) -> tuple[str, str]:
    """("auto" | "ask" | "none", category)."""
    p = parse(text)
    low = (text or "").lower()
    key = p["key"]
    if not key:
        # No tag, or a tag that is not a key: never automatic.
        guess = _guess(low)
        if p["severity"] == "advisory" and (not guess or CATEGORIES[guess][0] != "ask"):
            return "none", guess
        return "ask", guess
    if CATEGORIES[key][0] == "ask":
        return "ask", key                      # content: the user decides, even a Critical
    if any(g in low for g in _CONTENT_GUARD):
        return "ask", key                      # a layout tag on what reads like content
    if p["severity"] == "critical":
        return "auto", key
    if p["severity"] == "major":
        return "auto", key
    if p["severity"] == "advisory":
        return "none", key
    return "ask", key                          # no severity in its place


def split_findings(summary: str) -> list[str]:
    """Split only where ";" or a new line is followed by "slide N"; other
    pieces (fix detail) stay with the finding before them."""
    parts = re.split(r"[;\n]+(?=\s*slide\s+\d)", summary or "", flags=re.I)
    return [re.sub(r"[;\s]+$", "", p.strip()) for p in parts if p.strip(" ;\n\t")]


def classify(summary: str) -> list[dict]:
    rows = []
    for item in split_findings(summary):
        d, cat = decide(item)
        p = parse(item)
        rows.append({"finding": item, "decision": d, "category": cat,
                     "slide": p["slide"], "tag": p["tag"], "known_tag": bool(p["key"]),
                     "severity": p["severity"]})
    return rows


def valid_keys() -> str:
    return ", ".join(LAYOUT) + " (automatic); " + ", ".join(CONTENT_FIRST) + " (asked)"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not argv or argv[0] == "--list":
        print('Write each finding "slide N [key] Severity: text" (the key from this list).')
        for want, head in (("auto", "Fixed automatically (Critical or Major, layout/format)"),
                           ("ask", "Asked, in one table (content, any severity)")):
            print(f"\n{head}:")
            for k, (d, label, _) in CATEGORIES.items():
                if d == want:
                    print(f"  [{k}]  {label}")
        print("\nAlso accepted: " + ", ".join(f"[{a}] = [{k}]" for a, k in ALIASES.items())
              + " (hyphens or spaces work too).")
        print("Advisory findings: never fixed automatically. No tag, or a tag not listed: "
              "asked, never automatic.")
        return 0
    if argv[0] == "classify" and len(argv) > 1:
        for r in classify(" ; ".join(argv[1:])):
            print(f"{r['decision']:4}  [{r['category'] or '?'}]  {r['finding']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
