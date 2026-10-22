"""
check_pptx_hygiene.py — Programmatic pre-pass for slide QC
==========================================================

Catches hygiene issues that don't need vision — they can be answered
deterministically by reading the PPTX XML. Runs BEFORE the visual QC
pass so the visual pass can focus on what only eyes can catch.

Detects:
  - Lorem ipsum / placeholder text residue
  - "[Insert X]" / "Subtitle goes here" / TODO / FIXME / XXX in text
  - The template's own sample lines ("<Customize with ...>", "Click to edit")
  - Hidden slides leaking into the file
  - Comments left attached to slides
  - Speaker notes with non-substantive content
  - A text item ending with a final period; a chart without its header line
    ("Chart title, Unit", the unit plain after a comma) or unit, or with the
    unit written in brackets or parentheses; a legend not one row at the
    chart's top right (owner's rules 2026-10-09, corrected 2026-10-13: no
    brackets; slide-builder/scripts/chart_rules.py; layout Majors, fixed
    automatically)
  - File name patterns that signal workspace dumps
    ("Final_final_v3.pptx", "Copy of...", "deck (3).pptx")
  - A page number typed as plain text instead of a slide-number field
    (Major, fixed automatically; owner's rule 2026-10-12: never hardcoded)
  - Icons (owner's rules 2026-10-21): an icon inside a chart (Major); more
    than 6 icons on a page, icons on more than a third of the pages, or one
    icon on 3 or more pages (Advisory). Icons are found by the alt text
    "Icon: <name>" or the shape name icon-<name> that slide-builder gives them.

Footer / page-number presence is NOT detected here — it lives in the
visual QC pass instead, because most decks inherit those from the
slide master or layout and python-pptx doesn't see the inherited text
at the slide level. The visual pass reads the rendered PNG, where
inheritance is resolved, so it gives a reliable answer.

Outputs JSON to stdout — the SKILL invoker reads this and merges into
the unified Critical/Major/Advisory table. JSON shape:

  {
    "pptx": "<absolute path>",
    "slides": <int>,
    "violations": [
      {
        "slide": <int or null>,           # null for deck-level
        "severity": "Critical|Major|Advisory",
        "category": "<short tag>",
        "issue": "<one-line description>",
        "content": true, "auto_fix": false   # only on wording findings
      },                                      # (repeats-title, title-load):
                                              # they go to the user
      ...
    ]
  }

The script never modifies the PPTX.

Usage:
    py -3 check_pptx_hygiene.py "<path to deck.pptx>"
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

from pptx import Presentation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pptx_openability import check_openability  # noqa: E402


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Cross-skill placeholder contract.
#
# slide-builder/twins/helpers.py add_footer() emits these EXACT strings as
# INTENTIONAL presenter prompts when the caller passes footnote=None or
# source=None. Mirror of:
#   INTENTIONAL_FOOTNOTE_PLACEHOLDER = "[add footnote here or delete]"
#   INTENTIONAL_SOURCE_PLACEHOLDER   = "[add source here or delete]"
# in slide-builder/twins/helpers.py. Identity-matched, not regex-matched —
# do not generalize. If slide-builder changes the wording, this list must
# change in lockstep (and the cross-skill contract test should catch drift).
INTENTIONAL_PLACEHOLDER_STRINGS: tuple[str, ...] = (
    "[add footnote here or delete]",
    "[add source here or delete]",
)


LOREM_PATTERNS: list[tuple[str, str]] = [
    (r"\blorem\s+ipsum\b",         "Lorem ipsum"),
    (r"\bdolor\s+sit\s+amet\b",    "Lorem ipsum (dolor sit amet)"),
    (r"\[insert[^\]]{0,50}\]",     "[Insert ...] placeholder"),
    (r"\[your[^\]]{0,50}\]",       "[Your ...] placeholder"),
    (r"\bsubtitle\s+goes\s+here\b", "'Subtitle goes here' placeholder"),
    (r"\bplaceholder\s+text\b",    "'Placeholder text'"),
    (r"\bclick\s+to\s+add\b",      "'Click to add' template prompt"),
    (r"\bTODO\b",                  "TODO marker"),
    (r"\bFIXME\b",                 "FIXME marker"),
    (r"\bXXX\b",                   "XXX marker"),
    # Sweep gap from Pre-Workshop Scope Alignment build:
    # Hardline #2 placeholders (worker emits these when the brief doesn't
    # enumerate cell/list content, with a named source the user should
    # consult). These are NOT the intentional-presenter-prompt convention
    # (slide-builder/twins/helpers.py constants) — they mean unfinished
    # work and stay Critical. Visual disambiguation remains an open item.
    (r"\[[^\]]{1,60}\s+—\s+fill\s+from\b[^\]]{0,60}\]", "Hardline #2 '[X — fill from ...]' placeholder"),
    (r"\[[^\]]{1,30}\s+goes\s+here\]", "'[X goes here]' template prompt"),
    (r"\[\s*(TBD|TK|TKTK)\s*\]",        "[TBD] / [TK] marker"),
    (r"\b(TBD|TKTK)\b",                  "TBD / TKTK marker (bare)"),
]


# A template's own sample line left on a slide: a whole line in angle brackets
# ("<Customize with the client name>"), or PowerPoint's "Click to edit" prompt
# typed in as text. A layout footer cloned with its sample text shipped on every
# slide of a deck and only a human eye caught it (2026-10-08). Matched per line,
# so "<5% of spend" inside a sentence is not flagged. Mirrors
# slide-builder/twins/composer.py SAMPLE_TEXT_RE, which clears these lines at
# finalize.
SAMPLE_LINE_RE = re.compile(r"^\s*(<[^<>\n]{2,200}>|click to (add|edit)\b.*)\s*$", re.I)


def _is_intentional_placeholder(text: str) -> bool:
    """Return True if `text` contains a known slide-builder intentional
    presenter-prompt placeholder. Identity-match against the cross-skill
    contract — these strings are deliberately rendered for the presenter
    to fill or delete before showing the deck, not lorem-ipsum residue.
    """
    return any(ph in text for ph in INTENTIONAL_PLACEHOLDER_STRINGS)

FILENAME_BAD_PATTERNS: list[tuple[str, str]] = [
    (r"final[-_ ]?final",                                "'final_final' in filename"),
    (r"v\d+[-_ ]?final",                                 "'vN_final' pattern in filename"),
    (r"USE[-_ ]?THIS[-_ ]?ONE",                          "'USE_THIS_ONE' in filename"),
    (r"^copy\s+of\s+",                                   "starts with 'Copy of'"),
    (r"\s*\(\d+\)\.pptx$",                               "'(N).pptx' duplicate-file suffix"),
    # Standalone draft/wip/tmp/temp markers — surrounded by non-letters so
    # "template" / "templated" don't match "temp".
    (r"(?<![a-z])(draft|wip|tmp|temp)(?![a-z])",         "draft/wip/temp marker in filename"),
]

# Patterns indicating speaker notes are scratch, not substantive
NOTES_JUNK_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bdraft\b",
    r"\bfix\s+this\b",
    r"\bscratch\b",
    r"\bWIP\b",
    r"\basdf+\b",
    r"\btest\s+test\b",
    r"\bxxxxx+",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gather_slide_text(slide) -> str:
    """Concatenate all run text in a slide for full-text scanning."""
    chunks: list[str] = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text:
                    chunks.append(run.text)
    return " ".join(chunks)


def _slide_is_hidden(slide) -> bool:
    """Slides hidden in PowerPoint set `show="0"` on the sld element."""
    return slide._element.get("show") == "0"


def _slide_has_comments(slide) -> bool:
    """Check for comment relationships attached to the slide part."""
    try:
        for rel in slide.part.rels.values():
            if "comment" in (rel.reltype or "").lower():
                return True
    except Exception:
        pass
    return False


def _emu_to_in(emu) -> float | None:
    if emu is None:
        return None
    try:
        return int(emu) / 914400
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_filename(pptx_path: pathlib.Path) -> list[dict]:
    name = pptx_path.name
    name_lower = name.lower()
    for pat, label in FILENAME_BAD_PATTERNS:
        if re.search(pat, name_lower):
            return [{
                "slide": None,
                "severity": "Major",
                "category": "file-hygiene",
                "issue": f"Filename smells like a workspace dump ({label}): '{name}'. Rename before sharing.",
            }]
    return []


def check_placeholders_in_text(slide, slide_num: int) -> list[dict]:
    violations: list[dict] = []
    text = _gather_slide_text(slide)
    if not text:
        return violations

    # The old presenter prompts ("[add source here or delete]"). Designers
    # are told never to write them now (2026-10-02), so one on a finished
    # slide is a leak a reader would see: Major, not Advisory.
    if _is_intentional_placeholder(text):
        violations.append({
            "slide": slide_num,
            "severity": "Major",
            "category": "placeholder-prompt",
            "issue": (
                f"Slide {slide_num} shows a placeholder prompt "
                f"('[add source here or delete]' or similar). Put the real "
                f"source or footnote in, or remove the line."
            ),
        })
        # Strip the intentional placeholder strings before the Critical
        # regex pass so the existing LOREM_PATTERNS don't false-Critical
        # on a known-intentional substring.
        scrub = text
        for ph in INTENTIONAL_PLACEHOLDER_STRINGS:
            scrub = scrub.replace(ph, "")
        text = scrub

    for pat, label in LOREM_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            violations.append({
                "slide": slide_num,
                "severity": "Critical",
                "category": "placeholder-residue",
                "issue": f"Placeholder text detected on Slide {slide_num}: {label}.",
            })
    return violations


def check_template_sample_text(slide, slide_num: int) -> list[dict]:
    """Critical: a line of the template's own sample text is on the slide."""
    hits: list[str] = []
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue
        for para in shape.text_frame.paragraphs:
            line = "".join(r.text or "" for r in para.runs)
            if line.strip() and SAMPLE_LINE_RE.match(line):
                hits.append(line.strip())
    if not hits:
        return []
    shown = "; ".join(repr(h[:60]) for h in hits[:3])
    return [{
        "slide": slide_num,
        "severity": "Critical",
        "category": "template-sample-text",
        "issue": (f"Slide {slide_num} shows the template's sample text ({shown}). "
                  f"Put the real text in, or clear the line: the template's footer or "
                  f"another layout box kept its sample line."),
    }]


def _banned_terms() -> list[tuple[str, "re.Pattern"]]:
    """The shared list in slide-builder/reference/banned-words.md."""
    md = (pathlib.Path(__file__).resolve().parents[2] / "slide-builder" / "reference"
          / "banned-words.md")
    try:
        text = md.read_text(encoding="utf-8")
    except OSError:
        return []
    m = re.search(r"<!-- banned:start -->(.*?)<!-- banned:end -->", text, re.S)
    terms = [ln.strip() for ln in (m.group(1) if m else "").splitlines() if ln.strip()]
    terms += ["McKinsey", "BCG", "Bain", "MBB"]
    out = []
    for term in terms:
        if term.endswith("*"):
            out.append((term, re.compile(r"\b" + re.escape(term[:-1]) + r"\w*", re.I)))
        else:
            out.append((term, re.compile(r"\b" + re.escape(term) + r"\b", re.I)))
    return out


def check_banned_words(slide, slide_num: int) -> list[dict]:
    """Buzzwords and competitor names: Major, with the fix."""
    text = _gather_slide_text(slide) or ""
    hits = sorted({m.group(0) for _, rx in _banned_terms() for m in [rx.search(text)] if m})
    if not hits:
        return []
    return [{
        "slide": slide_num,
        "severity": "Major",
        "category": "buzzword",
        "issue": (f"Slide {slide_num} uses {', '.join(repr(h) for h in hits)}: replace "
                  f"each with the number or named fact it stands for."),
    }]


def check_type_scale(slide, slide_num: int, slide_h: int) -> list[dict]:
    """Body text 12 pt by default and never under 10.5 pt, at most 3 body
    sizes; sources, footnotes and chart labels not under 9 pt
    (slide-builder/scripts/type_scale.py). Breaks are Major (fix it, or the
    user gives a reason); body text at 10.5 to 11 pt is an Advisory note."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]
                               / "slide-builder" / "scripts"))
        import type_scale
    except Exception:
        return []
    r = type_scale.check_slide(slide, slide_h)
    out = [{
        "slide": slide_num,
        "severity": "Major",
        "category": "text size",
        "issue": (f"Slide {slide_num}: {p}. Bring body text back to 12 pt (10.5 pt at "
                  f"the lowest) by cutting words or splitting the content."),
    } for p in type_scale.problems(r)]
    out += [{
        "slide": slide_num,
        "severity": "Advisory",
        "category": "text size",
        "issue": (f"Slide {slide_num}: {n}. Allowed when the content cannot be cut; "
                  f"12 pt is the default."),
    } for n in type_scale.notes(r)]
    return out


def check_line_spacing(slide, slide_num: int) -> list[dict]:
    """Exact line spacing tighter than the font needs
    (slide-builder/scripts/type_scale.py line_spacing_slide, 2026-10-14): lines
    whose letters meet are Major (category line-spacing, fixed automatically
    as an overlap); capitals reaching above a top-anchored box, seen only when
    the box is selected, are Advisory."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]
                               / "slide-builder" / "scripts"))
        import type_scale
        r = type_scale.line_spacing_slide(slide)
    except Exception:
        return []
    out = [{
        "slide": slide_num,
        "severity": "Major",
        "category": "line-spacing",
        "issue": (f"Slide {slide_num}: {p}. Set the line spacing to at least the font's "
                  f"need (or 1.0 x the size), or give the text more room."),
    } for p in type_scale.line_spacing_problems(r)]
    out += [{
        "slide": slide_num,
        "severity": "Advisory",
        "category": "line-spacing",
        "issue": (f"Slide {slide_num}: {n}. Recompile with the current converter, which "
                  f"gives such boxes a top inset; the text does not move."),
    } for n in type_scale.line_spacing_notes(r)]
    return out


def check_title_load(prs) -> list[dict]:
    """The owner's rule (2026-10-08): each of the title, the takeaway under it
    and a bottom takeaway band must add something the others do not say. A
    line that repeats the title (half or more of its content words are in the
    title) is a content Major: a wording choice that goes to the user and is
    never fixed automatically. A two-line title with a takeaway under it AND a
    filled band is an Advisory recommendation
    (slide-builder/scripts/title_load.py)."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]
                               / "slide-builder" / "scripts"))
        import title_load
    except Exception:
        return []
    try:
        return title_load.deck_findings(prs)
    except Exception:
        return []


def check_chart_and_period_rules(prs) -> list[dict]:
    """The owner's three rules (2026-10-09), from
    slide-builder/scripts/chart_rules.py. All layout Majors, fixed
    automatically (qc_fix_policy.py keys):
      final_period     a text item ends with a period (periods between
                       sentences, ellipses, abbreviations and list numbers
                       are fine)
      chart_header     a chart without its header line "Chart title, Unit",
                       with a value axis and no unit, or with the unit in
                       brackets or parentheses ("Title, [M GPUs]")
      legend_position  a legend that is not one row at the chart's top right
    Drawn charts are found by shape name (chart-...); a deck whose chart
    pieces are not named that way is not flagged here (the vision pass still
    looks). Native charts are read from the chart object."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]
                               / "slide-builder" / "scripts"))
        import chart_rules
    except Exception:
        return []
    try:
        return chart_rules.deck_findings(prs)
    except Exception:
        return []


def check_hidden_slides(prs) -> list[dict]:
    violations: list[dict] = []
    for i, slide in enumerate(prs.slides, start=1):
        if _slide_is_hidden(slide):
            violations.append({
                "slide": i,
                "severity": "Major",
                "category": "hidden-slide",
                "issue": f"Slide {i} is marked hidden — will not appear in presentation mode. Confirm intentional or unhide.",
            })
    return violations


def check_comments(prs) -> list[dict]:
    violations: list[dict] = []
    for i, slide in enumerate(prs.slides, start=1):
        if _slide_has_comments(slide):
            violations.append({
                "slide": i,
                "severity": "Major",
                "category": "comments-left",
                "issue": f"Slide {i} has reviewer comments still attached. Resolve or delete before sharing.",
            })
    return violations


def check_speaker_notes(slide, slide_num: int) -> list[dict]:
    if not slide.has_notes_slide:
        return []
    text = slide.notes_slide.notes_text_frame.text or ""
    if not text.strip():
        return []
    for pat in NOTES_JUNK_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return [{
                "slide": slide_num,
                "severity": "Major",
                "category": "speaker-notes",
                "issue": f"Slide {slide_num} speaker notes contain scratch content (matched '{pat}'). Clean up or delete before sharing.",
            }]
    return []


_PAGE_NUMBER_NAME_RE = re.compile(
    r"^\s*(page[\s_-]*(number|num|no)|slide[\s_-]*(number|num|no))", re.I)
_BARE_NUMBER_RE = re.compile(r"^\s*\d{1,4}\s*$")


def check_page_number_fields(slide, slide_num: int) -> list[dict]:
    """Major (automatic fix, qc_fix_policy key page_number_field): a page
    number typed as plain text. Owner's rule (2026-10-12): page numbers are
    never hardcoded. In a slide-number placeholder, or a shape named like a
    page number, a bare number with no slide-number field (<a:fld
    type="slidenum">) stays the same when slides are moved, added or deleted,
    so the deck shows wrong numbers. Fix: recompile (finalize and compile
    write real fields)."""
    from pptx.oxml.ns import qn
    hits: list[str] = []
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue
        is_pn = False
        try:
            is_pn = bool(shape.is_placeholder and int(shape.placeholder_format.type) == 13)
        except Exception:
            pass
        if not is_pn and not _PAGE_NUMBER_NAME_RE.match(shape.name or ""):
            continue
        for para in shape.text_frame.paragraphs:
            if not _BARE_NUMBER_RE.match(para.text or ""):
                continue
            if any((f.get("type") or "").lower() == "slidenum"
                   for f in para._p.findall(qn("a:fld"))):
                continue
            hits.append(f"{shape.name!r} shows {para.text.strip()!r}")
    if not hits:
        return []
    return [{
        "slide": slide_num,
        "severity": "Major",
        "category": "page_number_field",
        "auto_fix": True,
        "issue": (f"Slide {slide_num}: the page number is typed text, not a slide-number "
                  f"field ({'; '.join(hits[:2])}), so it goes wrong when slides are moved, "
                  f"added or deleted. Fix: recompile the deck (finalize and compile write "
                  f"real fields)."),
    }]


# Footer / page-number detection was attempted here as a python-pptx pass but
# produced too many false positives — most decks inherit the footer from the
# slide master or layout, and python-pptx does not see the inherited text at
# the slide level. The visual QC pass already catches missing footers reliably
# because it reads the rendered PNG, where master inheritance is resolved.
# So this check intentionally lives in the visual pass, not here.


# ---------------------------------------------------------------------------
# Entry
ICON_CAP = 6


def _icon_name(sh) -> str:
    """The plain icon name of a Slide Lab icon shape, or ''."""
    try:
        c_nv = sh._element.xpath("./*[1]/p:cNvPr")
        descr = (c_nv[0].get("descr") or "") if c_nv else ""
    except Exception:
        descr = ""
    if descr.startswith("Icon: "):
        return descr[6:].strip()
    name = (getattr(sh, "name", "") or "").strip()
    if name.lower().startswith("icon-"):
        return name[5:].strip()
    return ""


def _icons_on(shapes, off=(0, 0, 1.0, 1.0)):
    """(name, box in EMU) for every icon on a slide, including icons inside
    groups (mapped through the group's child coordinates)."""
    ox, oy, sx, sy = off
    for sh in shapes:
        try:
            x0 = ox + (sh.left or 0) * sx
            y0 = oy + (sh.top or 0) * sy
            x1 = x0 + (sh.width or 0) * sx
            y1 = y0 + (sh.height or 0) * sy
        except Exception:
            continue
        name = _icon_name(sh)
        if name:
            yield name, (x0, y0, x1, y1)
            continue
        if getattr(sh, "shape_type", None) == 6:
            try:
                ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
                xfrm = sh._element.grpSpPr.find(ns + "xfrm")
                ch_off, ch_ext = xfrm.find(ns + "chOff"), xfrm.find(ns + "chExt")
                cx, cy = int(ch_off.get("x")), int(ch_off.get("y"))
                cw, chh = int(ch_ext.get("cx")) or 1, int(ch_ext.get("cy")) or 1
                gsx, gsy = (x1 - x0) / cw, (y1 - y0) / chh
                yield from _icons_on(sh.shapes, (x0 - cx * gsx, y0 - cy * gsy, gsx, gsy))
            except Exception:
                yield from _icons_on(sh.shapes, off)


def check_icons(prs) -> list[dict]:
    """Owner's icon rules (2026-10-21): an icon inside a chart is Major
    (category icon_in_chart); more than 6 icons on a page, icons on more than
    a third of the pages, or one icon on 3 or more pages are Advisory notes
    (category icon_use)."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]
                               / "slide-builder" / "scripts"))
        import chart_rules
    except Exception:
        chart_rules = None
    out: list[dict] = []
    pages_with: list[int] = []
    pages_of: dict[str, list[int]] = {}
    total = len(prs.slides)
    for i, slide in enumerate(prs.slides, start=1):
        found = list(_icons_on(slide.shapes))
        if not found:
            continue
        pages_with.append(i)
        for name, _box in found:
            pages_of.setdefault(name, [])
            if i not in pages_of[name]:
                pages_of[name].append(i)
        if len(found) > ICON_CAP:
            out.append({"slide": i, "severity": "Advisory", "category": "icon_use",
                        "issue": (f"Slide {i}: {len(found)} icons on one page; the limit is "
                                  f"{ICON_CAP}. Keep the icons whose picture adds meaning and use "
                                  f"numbers or plain shapes for the rest.")})
        areas = []
        if chart_rules is not None:
            try:
                areas = chart_rules.chart_areas(slide)
            except Exception:
                areas = []
        for name, (x0, y0, x1, y1) in found:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if any(a[0] <= mx <= a[2] and a[1] <= my <= a[3] for a in areas):
                out.append({"slide": i, "severity": "Major", "category": "icon_in_chart",
                            "auto_fix": True,
                            "issue": (f"Slide {i}: icon '{name}' sits inside a chart. Charts carry "
                                      f"no icons: remove it, or move it out of the chart and "
                                      f"label the point in words.")})
    if total >= 3 and len(pages_with) * 3 > total:
        out.append({"slide": None, "severity": "Advisory", "category": "icon_use",
                    "issue": (f"Icons on {len(pages_with)} of {total} pages (more than a third: "
                              f"pages {', '.join(map(str, pages_with))}). Use numbers or plain "
                              f"shapes as markers; keep icons for pages where the picture adds "
                              f"meaning.")})
    for name, pages in sorted(pages_of.items()):
        if len(pages) >= 3:
            out.append({"slide": None, "severity": "Advisory", "category": "icon_use",
                        "issue": (f"Icon '{name}' is on {len(pages)} pages "
                                  f"({', '.join(map(str, pages))}). The same picture on many "
                                  f"pages stops meaning anything: keep it where it adds the most.")})
    return out


# ---------------------------------------------------------------------------

def run_all_checks(pptx_path: pathlib.Path) -> dict:
    prs = Presentation(str(pptx_path))
    violations: list[dict] = []

    violations.extend(check_filename(pptx_path))
    violations.extend(check_hidden_slides(prs))
    violations.extend(check_comments(prs))
    # Structure PowerPoint refuses to open. Everything else here reads the deck
    # the way python-pptx and LibreOffice do, which is how a deck that would not
    # open at all once passed this check with zero violations.
    violations.extend(check_openability(prs, pptx_path))
    violations.extend(check_title_load(prs))
    violations.extend(check_chart_and_period_rules(prs))
    violations.extend(check_icons(prs))

    for i, slide in enumerate(prs.slides, start=1):
        violations.extend(check_placeholders_in_text(slide, i))
        violations.extend(check_template_sample_text(slide, i))
        violations.extend(check_banned_words(slide, i))
        violations.extend(check_type_scale(slide, i, prs.slide_height))
        violations.extend(check_line_spacing(slide, i))
        violations.extend(check_speaker_notes(slide, i))
        violations.extend(check_page_number_fields(slide, i))

    # Sort: Critical first, then Major, then Advisory; within severity by slide number
    severity_order = {"Critical": 0, "Major": 1, "Advisory": 2}
    violations.sort(key=lambda v: (severity_order.get(v["severity"], 9),
                                    v["slide"] if v["slide"] is not None else 0))

    return {
        "pptx": str(pptx_path),
        "slides": len(prs.slides),
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Programmatic hygiene pre-pass for slide QC. Emits JSON to stdout."
    )
    parser.add_argument("pptx", help="Path to the PPTX file to inspect")
    args = parser.parse_args()

    pptx_path = pathlib.Path(args.pptx).resolve()
    if not pptx_path.exists():
        print(json.dumps({"error": f"File not found: {pptx_path}"}), file=sys.stderr)
        return 1
    if not pptx_path.is_file() or pptx_path.suffix.lower() != ".pptx":
        print(json.dumps({"error": f"Not a .pptx file: {pptx_path}"}), file=sys.stderr)
        return 1

    try:
        result = run_all_checks(pptx_path)
    except Exception as exc:
        print(json.dumps({"error": f"Failed to inspect {pptx_path.name}: {exc}"}), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
