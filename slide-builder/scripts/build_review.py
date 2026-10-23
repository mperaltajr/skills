"""build_review.py

===============================

Generate a self-contained REVIEW.html for a slide-builder
orchestrator output dir.

Notable behaviors:
  - sys.path tweak for twins/ from slide-builder/
  - extract_option_pattern() reads each option_X.py's line-1 / line-2 to
    capture the picked pattern + classification (native/fallback/rejected)
  - compute_adjacency_warnings() scans option_A across all slides; any
    3+ consecutive same-pattern run produces a per-slide advisory list
  - render_card() injects an adjacency banner when warnings exist
  - CSS adds a .adjacency-banner style

Usage
-----
    py -3 build_review.py --out <orchestrator_output_dir>
Writes <out>/REVIEW.html.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path setup. twins/ is local to this skill; render_slides lives in the
# sibling slide-qc skill. This
# script does not actually import from either today; the paths are
# kept on sys.path defensively in case future helpers are added.
SKILL_ROOT = Path(__file__).resolve().parents[1]
QC_SCRIPTS = SKILL_ROOT.parent / "slide-qc" / "scripts"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(QC_SCRIPTS))

import _paths as _p  # noqa: E402
import _state  # noqa: E402  (build state manifest: mint the review-approval token)


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def file_uri(p: Path) -> str:
    return p.resolve().as_uri()


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        try:
            return p.read_text(encoding="utf-8-sig")
        except Exception:
            return ""


def fmt_bytes(b: int) -> str:
    if b <= 0:
        return "0 B"
    val = float(b)
    for unit in ("B", "KB", "MB", "GB"):
        if val < 1024:
            return f"{val:.0f} {unit}" if unit == "B" else f"{val:.1f} {unit}"
        val /= 1024
    return f"{val:.1f} TB"


# ---------------------------------------------------------------------------
# Pattern extraction + adjacency detection
# ---------------------------------------------------------------------------
FALLBACK_MERMAID_TOKEN = "# FALLBACK_MERMAID:"
SKELETON_REJECTED_TOKEN = "# SKELETON_REJECTED:"

# Header convention from prompt.md § 8:
#   Native:   line 1 = "# Slide N option <X> — pattern: <name>"
#   Fallback: line 1 = "# FALLBACK_MERMAID: ..."
#             line 2 = "# Slide N option <X> — pattern attempted: <name>"
#   Rejected: line 1 = "# SKELETON_REJECTED: ..."
#             line 2 = "# Slide N option <X> — pattern attempted: <name>"
_PATTERN_RE = re.compile(
    r"^#\s*Slide\s+\d+\s+option\s+[A-Z]\s+[—\-]\s+pattern(?:\s+attempted)?:\s*(.+?)\s*$",
    re.IGNORECASE,
)


def extract_option_pattern(py_path: Path) -> tuple[Optional[str], str]:
    """Read option_X.py and return (pattern_name, classification).

    classification is one of: 'native', 'fallback_mermaid', 'skeleton_rejected', 'unknown'.
    pattern_name is None if no header line parses.
    """
    if not py_path.exists():
        return None, "unknown"
    try:
        text = py_path.read_text(encoding="utf-8")
    except Exception:
        return None, "unknown"
    lines = text.splitlines()[:3]
    if not lines:
        return None, "unknown"
    line1 = lines[0].strip()
    if line1.startswith(FALLBACK_MERMAID_TOKEN):
        classification = "fallback_mermaid"
        pattern_line = lines[1] if len(lines) > 1 else ""
    elif line1.startswith(SKELETON_REJECTED_TOKEN):
        classification = "skeleton_rejected"
        pattern_line = lines[1] if len(lines) > 1 else ""
    else:
        classification = "native"
        pattern_line = line1
    m = _PATTERN_RE.match(pattern_line.strip())
    pattern_name = m.group(1).strip() if m else None
    return pattern_name, classification


def compute_adjacency_warnings(
    slides_by_n: dict[int, dict],
    option_letter: str = "A",
) -> dict[int, list[str]]:
    """Detect 3+ consecutive same-pattern runs across `option_letter`.

    Each affected slide gets an advisory string. The user sees the advisory
    on the slide's card in REVIEW.html.

    Returns: {slide_n: [advisory_string, ...]}
    """
    warnings: dict[int, list[str]] = {}
    if not slides_by_n:
        return warnings

    # Build ordered sequence of (slide_n, pattern_name) using option_letter.
    sorted_ns = sorted(slides_by_n.keys())
    sequence: list[tuple[int, Optional[str]]] = []
    for n in sorted_ns:
        slide = slides_by_n[n]
        pat = None
        for opt in slide.get("options", []):
            if opt.get("letter") == option_letter:
                pat = opt.get("pattern")
                break
        sequence.append((n, pat))

    # Find runs of 3+ same non-None pattern.
    i = 0
    while i < len(sequence):
        n_i, pat_i = sequence[i]
        if pat_i is None:
            i += 1
            continue
        j = i + 1
        while j < len(sequence) and sequence[j][1] == pat_i:
            j += 1
        run_len = j - i
        if run_len >= 3:
            run_slides = [sequence[k][0] for k in range(i, j)]
            msg = (
                f"Option {option_letter} runs the same pattern "
                f"({pat_i!r}) across slides {', '.join(str(s) for s in run_slides)}. "
                f"Hardline #3 forbids 3+ consecutive same-split slides. "
                f"Consider picking a different option for at least one slide in this run, "
                f"or sending the run back for regen."
            )
            for sn in run_slides:
                warnings.setdefault(sn, []).append(msg)
            i = j
        else:
            i += 1
    return warnings


# ---------------------------------------------------------------------------
# Brief parser
# ---------------------------------------------------------------------------

def parse_brief(brief_path: Path) -> dict:
    out = {
        "topic": "", "deck_type": "", "governing": "", "audience": "",
        "belief_break": "", "belief_leave": "", "say_back": "",
        "slides": [], "found": False,
    }
    if not brief_path or not brief_path.exists():
        return out
    text = read_text(brief_path)
    if not text:
        return out
    out["found"] = True

    m = re.search(r"^#\s+(?:Narrative brief:\s*)?(.+?)\s*$", text, re.M)
    if m:
        out["topic"] = m.group(1).strip()

    def _h2_block(label: str) -> str:
        pat = rf"^##\s+{re.escape(label)}\s*\n([\s\S]+?)(?=^##\s|\Z)"
        mm = re.search(pat, text, re.M)
        return mm.group(1).strip() if mm else ""

    out["deck_type"] = _h2_block("Deck type").splitlines()[0] if _h2_block("Deck type") else ""
    gov_block = _h2_block("Governing thought (the whole deck)") or _h2_block("Governing thought")
    if gov_block:
        out["governing"] = gov_block.splitlines()[0].strip()

    audience_block = _h2_block("Audience")
    if audience_block:
        out["audience"] = audience_block.splitlines()[0].strip()

    def _bold_field(label: str) -> str:
        pat = rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)"
        mm = re.search(pat, text)
        return mm.group(1).strip() if mm else ""

    out["belief_break"] = _bold_field("Audience assumption to break")
    out["belief_leave"] = _bold_field("Audience belief to leave with")
    out["say_back"] = _bold_field("The single sentence the room should say back").strip().strip('"').strip("'")

    slide_iter = list(re.finditer(r"^###\s+Slide\s+(\d+)\s*[—-]\s*(.+?)\s*$", text, re.M))
    for i, m in enumerate(slide_iter):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = slide_iter[i + 1].start() if i + 1 < len(slide_iter) else len(text)
        body = text[start:end]
        gov = ""
        gm = re.search(r"\*\*Governing thought(?:\s*\(the claim\))?:\*\*\s*(.+?)(?:\n|$)", body)
        if gm:
            gov = gm.group(1).strip()
        bullets: list[str] = []
        bm = re.search(r"\*\*(?:Evidence\s*/\s*content|Content):\*\*\s*\n([\s\S]+?)(?=\n\*\*|\n###|\Z)", body)
        if bm:
            for line in bm.group(1).splitlines():
                ls = line.strip()
                if not ls:
                    continue
                if ls.startswith("- "):
                    bullets.append(_md_inline_to_html(ls[2:].strip()))
                elif ls.startswith("  - ") or ls.startswith("\t- "):
                    if bullets:
                        bullets[-1] += " <em>" + _md_inline_to_html(ls.lstrip("- \t")) + "</em>"
        # The headline as written: no "Slide N" prefix and no dash added (the
        # panel used to add 30 em-dashes of its own, 2026-10-13).
        out["slides"].append({"n": num, "title": title, "gov": gov, "bullets": bullets})
    return out


def _md_inline_to_html(s: str) -> str:
    s_esc = html.escape(s)
    s_esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s_esc)
    s_esc = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s_esc)
    return s_esc


# ---------------------------------------------------------------------------
# Per-slide _prompt.md parser
# ---------------------------------------------------------------------------

# page_type was previously regexed out of _prompt.md via
# `**Page type (heuristic):**` — that line was an earlier prep-pass echo and
# is never written by build_deck.py. The canonical source for page_type is
# _meta.json (slides[].page_type). parse_prompt() no longer attempts to read
# it; the lookup is on _meta.json only. See the resolution.
PROMPT_FIELDS = {
    "title": r"\*\*Slide title:\*\*\s*(.+?)(?:\n|$)",
    "governing": r"\*\*Governing thought \(the claim\):\*\*\s*\n([\s\S]+?)(?:\n\n|\n\*\*)",
    "so_what": r"\*\*So-what \(the takeaway\):\*\*\s*\n([\s\S]+?)(?:\n\n|\n\*\*)",
}


def parse_prompt(prompt_path: Path) -> dict:
    out = {"title": None, "governing": None, "so_what": None, "bullets": [], "found": False}
    if not prompt_path.exists():
        return out
    text = read_text(prompt_path)
    out["found"] = True
    for key, pat in PROMPT_FIELDS.items():
        m = re.search(pat, text)
        if m:
            val = m.group(1).strip()
            val = re.sub(r"\s+", " ", val).strip()
            out[key] = val
    bm = re.search(r"\*\*Evidence\s*/\s*content:\*\*\s*\n([\s\S]+?)(?=\n\*\*|\Z)", text)
    if bm:
        for line in bm.group(1).splitlines():
            ls = line.strip()
            if ls.startswith("- "):
                out["bullets"].append(_md_inline_to_html(ls[2:].strip()))
    return out


# ---------------------------------------------------------------------------
# Slide scan — pattern capture per option
# ---------------------------------------------------------------------------

# Every letter an option can have, not the settings count. Reading the setting
# here hid options that were built: with the setting at 1 and A/B/C on disk, the
# page showed only A, while --all-variations still shipped all three.
OPTIONS = _p._ALL_OPTION_LETTERS


# ---------------------------------------------------------------------------
# Sketch facts: visual form, icons, source line
# ---------------------------------------------------------------------------

# The visual forms a sketch declares with data-visual-form on its canvas
# (reference/sketch-html-spec.md). Other values are kept as written.
VISUAL_FORMS = ("cards", "table", "chart", "flow", "timeline", "matrix", "hero-number",
                "diagram", "comparison", "text", "quote", "image", "map")
_FORM_RE = re.compile(r"""data-visual-form\s*=\s*["']([^"']+)["']""", re.I)
_FORM_META_RE = re.compile(r"""<meta\s+name\s*=\s*["']visual-form["']\s+content\s*=\s*["']([^"']+)["']""", re.I)
_ICON_RE = re.compile(r"""data-icon-name\s*=\s*["']([^"']*)["']|"""
                      r"""<img[^>]+src\s*=\s*["'][^"']*?icons/([A-Za-z0-9_.\-]+?)\.(?:svg|png|xml)["']""", re.I)
_FOOTER_RE = re.compile(r"""data-template-field\s*=\s*["']footer["']""", re.I)


TITLE_MAX_LINES = 2


def chrome_fit_notes(html_path: Path) -> list:
    """Major notes from the sketch render's check of the template's title and
    takeaway (render_html.py writes option_X.sketch.chrome.json after adding
    the slide's _chrome.css, 2026-10-13). Measured against the template's own
    values, never against what other pages do:
      TITLE_TOO_LONG     the title takes 3 or more lines in the template's
                         title style (the box holds 2)
      BODY_UNDER_CHROME  a body shape sits under the title or takeaway as
                         the template draws them (above --body-top)"""
    check = html_path.with_name(html_path.stem + ".sketch.chrome.json")
    try:
        data = json.loads(check.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    notes = []
    lines = int(data.get("title_lines") or 0)
    if lines > TITLE_MAX_LINES:
        notes.append({"severity": "Major", "code": "TITLE_TOO_LONG",
                      "detail": f"in the template's title style the title takes {lines} lines; "
                                f"the title box holds {TITLE_MAX_LINES}. Shorten the title (ask "
                                "the user before changing the brief's wording), then re-render "
                                "the sketch"})
    covered = data.get("covered") or []
    if covered:
        ids = ", ".join(sorted({str(c.get("id")) for c in covered})[:6])
        by = " and ".join(sorted({str(c.get("by")) for c in covered}))
        top = data.get("body_top")
        where = f" ({int(top)} px from the top)" if top else ""
        notes.append({"severity": "Major", "code": "BODY_UNDER_CHROME",
                      "detail": f"body shape(s) {ids} sit under the template's {by}; move them "
                                f"down to --body-top{where} or lower (Replace with a note), "
                                "or shorten the title"})
    return notes


def sketch_facts(html_path: Path, slide_meta: Optional[dict]) -> tuple[Optional[str], list]:
    """(visual form the sketch declares or None, notes for its card).

    Notes are {severity, code, detail}: an icon name not on the allowed list
    (Critical: a placeholder would ship in its place, so the option is blocked
    until the designer uses an allowed name; owner's decision 2026-10-21), an
    old name of an allowed icon (Advisory: it works, the note gives its plain
    name), and a brief source line the sketch left out of its footer (Major)."""
    try:
        text = html_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, []
    m = _FORM_RE.search(text) or _FORM_META_RE.search(text)
    form = " ".join(m.group(1).strip().lower().split()) if m else None
    notes = []
    try:
        import icon_svg
        names = sorted({(a or b).strip() for a, b in _ICON_RE.findall(text)})
        for name in names:
            w = icon_svg.warning_for(name)
            if w:
                sev = "Advisory" if w["code"] == "ICON_OLD_NAME" else "Critical"
                notes.append({"severity": sev, "code": w["code"], "detail": w["detail"]})
    except Exception:
        pass
    notes += chrome_fit_notes(html_path)
    src = ((slide_meta or {}).get("source") or "").strip()
    if src and not _FOOTER_RE.search(text):
        notes.append({"severity": "Major", "code": "SOURCE_LINE_MISSING",
                      "detail": f'the brief gives this page a source line ("{src}") but the '
                                'design has no footer element for it; the page would ship with '
                                'no source'})
    return form, notes


def compute_form_warnings(slides: list) -> Optional[dict]:
    """Deck-level sameness check on the visual forms the sketches declare.

    A page's form is the one most of its options share (option A's on a tie).
    Warns when one form is on at least half of the pages (4 or more pages
    with a known form) or on 3 or more pages in a row. Pages whose sketches
    declare no form are listed as unknown, not skipped. None when the deck
    has no sketches. The check that read the pattern from option_X.py
    headers never ran on sketch decks, and split names cannot see "cards on
    every page" anyway (2026-10-08)."""
    from collections import Counter
    pages = []
    for s in slides:
        sk = [o for o in s.get("options", []) if o.get("is_sketch")]
        if not sk:
            continue
        forms = [o.get("visual_form") for o in sk if o.get("visual_form")]
        if forms:
            c = Counter(forms)
            top = max(c.values())
            form = next(f for f in forms if c[f] == top)
        else:
            form = None
        pages.append((s["n"], form))
    if not pages:
        return None
    known = [(n, f) for n, f in pages if f]
    counts = Counter(f for _, f in known)
    unknown = [n for n, f in pages if not f]
    warnings = []
    if len(known) >= 4 and counts:
        form, k = counts.most_common(1)[0]
        if k * 2 >= len(pages):
            warnings.append(f"{k} of {len(pages)} pages use the same visual form "
                            f"({form}). Ask for a different form on some of them "
                            f"(Replace these, with a note), or confirm it is intended.")
    i = 0
    while i < len(pages):
        j = i
        while j + 1 < len(pages) and pages[i][1] and pages[j + 1][1] == pages[i][1]:
            j += 1
        if pages[i][1] and j - i + 1 >= 3:
            warnings.append(f"slides {', '.join(str(pages[k][0]) for k in range(i, j + 1))} "
                            f"in a row are all {pages[i][1]}.")
        i = j + 1
    return {"pages": pages, "counts": dict(counts), "unknown": unknown, "warnings": warnings}


def render_form_banner(slides: list) -> str:
    """The deck at a glance: how many pages use each visual form, and a
    warning when one form dominates or repeats on neighbors."""
    res = compute_form_warnings(slides)
    if not res:
        return ""
    mix = ", ".join(f"{f} {k}" for f, k in sorted(res["counts"].items(), key=lambda kv: -kv[1]))
    parts = [f"Visual forms across {len(res['pages'])} sketched pages: {html.escape(mix) or 'none declared'}"]
    if res["unknown"]:
        parts.append("form unknown (the sketch does not say) on slide "
                     + ", ".join(str(n) for n in res["unknown"]))
    body = ". ".join(parts) + "."
    if res["warnings"]:
        items = "".join(f"<li>{html.escape(w)}</li>" for w in res["warnings"])
        return ('<div class="font-banner" id="form-banner">'
                '<div class="font-banner-title"><span class="font-banner-icon">&#9888;</span> '
                'Many pages look alike</div>'
                f'<div class="font-banner-body">{body}<ul>{items}</ul></div></div>')
    return ('<div class="qc-brief-banner" id="form-banner">'
            '<div class="qc-brief-banner-title">Visual forms</div>'
            f'<div>{body}</div></div>')


def render_sketch_notes(slide: dict) -> str:
    rows = []
    for o in slide.get("options", []):
        for nt in o.get("sketch_notes") or []:
            rows.append(f'<li><strong>Option {o["letter"]}, {html.escape(nt["severity"])}</strong>'
                        f' ({html.escape(nt["code"])}): {html.escape(nt["detail"])}</li>')
    if not rows:
        return ""
    return ('<div class="adjacency-banner sketch-notes">'
            '<div class="adjacency-banner-title">&#9888; Check before picking</div>'
            f'<ul>{"".join(rows)}</ul></div>')


def scan_slide(out_dir: Path, slide_num: int, slide_meta: Optional[dict]) -> dict:
    slide_id = _p.slide_key(slide_num)
    src_dir = out_dir / slide_id
    # finalize_deck.py writes themed PPTX + PNG directly into the slide dir
    # (raw pre-theme output is stashed in _raw/ subdir, not the other way around).
    # The "themed_" variable names below remain semantically correct — they refer
    # to the themed deliverable, which happens to live in the same dir as src.
    themed_dir = src_dir

    prompt = parse_prompt(src_dir / _p.PROMPT_MD)

    title = prompt.get("title")
    if not title and slide_meta:
        title = slide_meta.get("title")
    if not title:
        title = f"Slide {slide_num}"

    # page_type now comes only from _meta.json (canonical). See the resolution.
    page_type = (slide_meta or {}).get("page_type") or ""
    if page_type:
        page_type = page_type.split("\n")[0].strip()

    options = []
    slide_content_lines: list = []     # content findings shown once per slide
    # Only render tiles for options that were ACTUALLY built for this slide. A
    # slide built with a single option must show ONE tile, not one tile plus
    # empty B/C "missing" slots.
    def _option_built(letter: str) -> bool:
        return (
            (src_dir / _p.option_py_name(letter)).exists()
            or (src_dir / f"option_{letter}.html").exists()
            or (src_dir / f"option_{letter}_native.py").exists()
            or (themed_dir / _p.option_pptx_name(letter)).exists()
            or (themed_dir / _p.option_png_name(letter)).exists()
            or (themed_dir / _p.option_sketch_png_name(letter)).exists()
        )
    built_letters = [l for l in OPTIONS if _option_built(l)]
    if not built_letters:
        built_letters = list(_p.option_letters())  # nothing built yet: fall back
    # A fingerprint of this slide's option files. The page keeps a pick only
    # while the stamp it was made against still matches, so rebuilding slide 3
    # clears slide 3's pick and leaves every other slide's alone. Picks used to
    # carry over onto a rebuilt slide (one click, no looking), and after an
    # insert they landed on the wrong slide.
    # (_state computes it, so a chat approval of picks can check the files
    # are still the ones the opened page showed.)
    slide_stamp = _state.option_files_stamp(src_dir)
    for letter in built_letters:
        # The finished, on-template render when finalize has made one; the
        # worker's sketch otherwise. The page says which it is showing.
        finished_png = themed_dir / _p.option_png_name(letter)
        sketch_png = themed_dir / _p.option_sketch_png_name(letter)
        if finished_png.exists():
            png, png_kind = finished_png, "finished"
        elif sketch_png.exists():
            png, png_kind = sketch_png, "sketch"
        else:
            png, png_kind = finished_png, "none"
        themed_pptx = themed_dir / _p.option_pptx_name(letter)
        src_pptx = src_dir / _p.option_pptx_name(letter)
        src_py = src_dir / _p.option_py_name(letter)
        themed_exists = themed_pptx.exists()
        qc_path = themed_dir / _p.option_qc_json_name(letter)
        qc_summary = None
        qc_failed_checks: list = []
        # Findings that get their own plain line on the card (owner's decision,
        # 2026-10-09): type-scale breaks ("fix it, or give a reason"), text
        # fit, and, once per slide, a takeaway that repeats the title.
        qc_plain: list = []
        if qc_path.exists():
            try:
                qc_data = json.loads(qc_path.read_text(encoding="utf-8"))
                qc_summary = qc_data.get("summary")
                for c in qc_data.get("checks", []):
                    if not c.get("pass"):
                        qc_failed_checks.append(f"{c.get('check')} [{c.get('severity')}]: {c.get('detail', '')}")
                        lines = [str(x) for x in (c.get("plain") or []) if x]
                        if not lines:
                            continue
                        if c.get("slide_level"):
                            for x in lines:
                                if x not in slide_content_lines:
                                    slide_content_lines.append(x)
                        else:
                            qc_plain.append({"block": c.get("severity") == "block",
                                             "advisory": bool(c.get("advisory")),
                                             "lines": lines})
            except Exception:
                qc_summary = None

        # extract pattern + classification from the .py header
        pattern, classification = extract_option_pattern(src_py)

        # when the translator wrote a
        # per-zone SSIM + warnings report (Spec 4 §8 + Spec 6), surface it in
        # REVIEW.html so the user sees the fidelity story alongside the option
        # PNG. Path convention is sibling to the .py file:
        #   slide_NN/option_X_translation_report.json
        # Missing report is the common case for direct-path slides — we just
        # carry empty data through; render_card decides what to show.
        translation_report_path = themed_dir / f"option_{letter}_translation_report.json"
        ssim_per_zone: dict = {}
        translation_warnings: list = []
        translation_pass: Optional[bool] = None
        if translation_report_path.exists():
            try:
                tr = json.loads(translation_report_path.read_text(encoding="utf-8"))
                ssim_per_zone = (tr.get("translator_self_check", {}) or {}).get("ssim_per_zone", {}) or {}
                translation_pass = (tr.get("translator_self_check", {}) or {}).get("pass")
                # Spec 6 severity mapping: codes that contain MAJOR / CRITICAL /
                # advisory mappings are inferred by code prefix. The translator
                # report's warnings array carries {code, detail} dicts.
                for w in tr.get("warnings", []) or []:
                    # Most real reports write warnings as plain strings. The
                    # dict-only parse raised on the first one, the except below
                    # swallowed it, and every translator warning vanished from
                    # the page.
                    if isinstance(w, str):
                        w = {"code": "", "detail": w}
                    elif not isinstance(w, dict):
                        continue
                    code = (w.get("code") or w.get("id") or "").upper()
                    detail = w.get("detail") or w.get("message") or ""
                    if "CRITICAL" in code or code in ("EDITABILITY_VIOLATION", "TRANSLATOR_BLOCKED",
                                                      "ICON_UNKNOWN", "ICON_NO_PREVIEW"):
                        sev = "Critical"
                    elif "MAJOR" in code or "MISMATCH" in code or "BELOW_MAJOR" in code \
                            or code == "WRAP_RISK":     # text may run onto an extra line
                        sev = "Major"
                    else:
                        sev = "Advisory"
                    translation_warnings.append({"code": w.get("code", ""), "detail": detail, "severity": sev})
            except Exception:
                # Malformed report is non-blocking; just don't surface it.
                pass

        sketch_html = src_dir / f"option_{letter}.html"
        visual_form, sketch_notes = (sketch_facts(sketch_html, slide_meta)
                                     if sketch_html.exists() else (None, []))
        # A Critical sketch note (an icon that is not on the allowed list)
        # blocks the option: its card says "Needs a fix" (2026-10-21).
        crit = [n for n in sketch_notes if n.get("severity") == "Critical"]
        if crit:
            qc_summary = dict(qc_summary or {})
            qc_summary["block"] = int(qc_summary.get("block", 0) or 0) + len(crit)
            qc_failed_checks = [f"{n['code']} [Critical]: {n['detail']}" for n in crit] + qc_failed_checks

        options.append({
            "letter": letter,
            "is_sketch": sketch_html.exists(),
            "visual_form": visual_form,
            "sketch_notes": sketch_notes,
            "png": png,
            "png_exists": png.exists(),
            "png_kind": png_kind,
            "themed_pptx": themed_pptx,
            "themed_exists": themed_exists,
            "src_pptx": src_pptx,
            "src_exists": src_pptx.exists(),
            "themed_size": themed_pptx.stat().st_size if themed_exists else 0,
            "qc_summary": qc_summary,
            "qc_failed_checks": qc_failed_checks,
            "qc_plain": qc_plain,
            "pattern": pattern,
            "classification": classification,
            # Sketch-path translation QC fields
            "translation_report_path": translation_report_path if translation_report_path.exists() else None,
            "ssim_per_zone": ssim_per_zone,
            "translation_warnings": translation_warnings,
            "translation_pass": translation_pass,
        })

    # Gap 3: worker context-ack telemetry. When build_deck.py
    # has written `_context.md` and the worker has followed the soft-
    # enforcement protocol, it leaves `_context_ack.txt` next to it with a
    # one-line citation of the constraint that informed its pattern pick.
    # Surface absence as an advisory chip — non-blocking; the user decides
    # whether to re-dispatch.
    #
    # Audit blocker: when the template was registered WITHOUT
    # a reference_slide_n, _context.md still gets written (it carries design
    # rules + brief metadata) but contains a sentinel string flagging the
    # absence of canonical anchor. In that case there's no meaningful
    # constraint for the worker to cite, and a yellow ⚠ chip on every slide
    # of every build is pure noise. Detect the sentinel and suppress the
    # chip entirely.
    context_md_path = src_dir / "_context.md"
    context_ack_path = src_dir / "_context_ack.txt"
    context_present = context_md_path.exists()
    context_has_reference = False
    if context_present:
        try:
            _ctx_head = context_md_path.read_text(
                encoding="utf-8", errors="replace"
            )[:600]
            # Sentinel from _format_reference_block_for_context() — see
            # scripts/build_deck.py. If absent, the user registered with
            # reference_slide_n and the context bundle is meaningful.
            context_has_reference = (
                "No reference slide was captured" not in _ctx_head
            )
        except Exception:
            context_has_reference = False
    ack_present = context_ack_path.exists()
    ack_text = ""
    if ack_present:
        try:
            ack_text = context_ack_path.read_text(
                encoding="utf-8", errors="replace"
            ).strip().splitlines()[0] if context_ack_path.read_text(
                encoding="utf-8", errors="replace"
            ).strip() else ""
        except Exception:
            ack_text = ""

    return {
        "n": slide_num,
        "slide_id": slide_id,
        "title": title,
        "page_type": page_type,
        "governing": prompt.get("governing"),
        "so_what": prompt.get("so_what"),
        "bullets": prompt.get("bullets", []),
        "prompt_path": src_dir / _p.PROMPT_MD,
        "prompt_found": prompt.get("found", False),
        "options": options,
        "content_lines": slide_content_lines,
        "stamp": slide_stamp,
        "pinned": (slide_meta or {}).get("pinned_source_page") or "",
        "fixed_id": (slide_meta or {}).get("slide_id") or "",
        "page_copy": (slide_meta or {}).get("page_copy") or {},
        "context_present": context_present,
        "context_has_reference": context_has_reference,
        "context_ack_present": ack_present,
        "context_ack_text": ack_text,
    }


def discover_slide_count(out_dir: Path) -> int:
    n = 0
    for child in out_dir.iterdir():
        if child.is_dir() and re.fullmatch(r"slide_\d+", child.name):
            try:
                n = max(n, int(child.name.split("_")[1]))
            except ValueError:
                pass
    return n


# ---------------------------------------------------------------------------
# Storyline rendering
# ---------------------------------------------------------------------------

def render_preview_banner(slides: list) -> str:
    """Loud in-page notice when options have no rendered preview.

    build_review used to print `missing PNGs: N` / `missing themed PPTX: N` to the
    log and say NOTHING in the page. A 13-slide review was handed over with 36 of
    39 tiles unviewable and it was invisible to the reviewer. Surface it where the
    decision is actually made.
    """
    total = sum(len(s["options"]) for s in slides)
    no_png = sum(1 for s in slides for o in s["options"] if not o["png_exists"])
    pre_graft = sum(1 for s in slides for o in s["options"]
                    if o.get("png_kind") == "sketch")
    out = ""
    if no_png:
        out += (
            '<div class="font-banner">'
            '<div class="font-banner-title"><span class="font-banner-icon">&#9888;</span> '
            f'{no_png} of {total} options have no rendered preview</div>'
            '<div class="font-banner-body">'
            'Those tiles show no image, so they cannot be judged on sight. Picking still '
            'works (picks are recorded by option letter), but render the missing options '
            'and rebuild this page if you want to see them. '
            '<strong>Do not approve a deck you could not look at.</strong></div>'
            '</div>'
        )
    if pre_graft:
        # A pre-graft preview is the design as the worker drew it, before the
        # template's title, takeaway and page number land on it. That is where
        # collisions appear: on one deck eight slides were approved from clean
        # previews and shipped with the takeaway buried under body content.
        out += (
            '<div class="font-banner">'
            '<div class="font-banner-title"><span class="font-banner-icon">&#9888;</span> '
            f'{pre_graft} of {total} previews are sketches</div>'
            '<div class="font-banner-body">'
            'These show the design as it was drawn, before the template\'s title, '
            'takeaway and page number are put on it. Only the options you pick are '
            'converted, and you will see each one finished, on the template, in a '
            '<strong>final check</strong> before anything is built. That is where '
            'a collision with the template shows up.</div>'
            '</div>'
        )
    return out


def render_storyline_html(storyline: dict, slides: list, meta: Optional[dict] = None) -> str:
    """The storyline panel: the approved storyline file as written, or the
    slide headlines alone (scripts/review_storyline.py, owner's decision
    2026-10-13). What it must show is kept in storyline["_panel"] for the
    check main() runs after writing the page."""
    import review_storyline
    panel = review_storyline.build_panel(meta, storyline, slides)
    storyline["_panel"] = panel
    return panel["html"] + _page_map_section(meta)


def _page_map_section(meta: Optional[dict]) -> str:
    """"Pages you gave us" (map_source_pages.py) under the storyline panel,
    outside its checked text: each supplied page, its picture, and the slide
    it goes to or "not used" (owner's direction 2026-10-14: no page of its
    own). Empty without a page map; never stops the page."""
    try:
        import _rulings
        import map_source_pages
        bp = (meta or {}).get("brief")
        out = (meta or {}).get("out")
        sd = _rulings.session_dir(out=out, brief=bp)
        return map_source_pages.render_section(sd)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# QC banner stub (humanizer + render trimmed)
# ---------------------------------------------------------------------------

def render_qc_banner(out_dir: Path) -> str:
    qc_path = _p.brief_qc_json(out_dir)
    if not qc_path.exists():
        # Only source_ledger.py writes brief_qc.json (for a replicated supplied
        # page), so on most builds it is absent; the old "not found" box showed
        # on every review page as noise.
        return ""
    try:
        payload = json.loads(read_text(qc_path))
    except Exception as exc:
        return (
            '<div class="qc-brief-banner">'
            '<div class="qc-brief-banner-title">Brief-time QC report</div>'
            '<details class="qc-brief-section qc-brief-info" open>'
            '<summary><span class="qc-brief-icon">i</span>INFO &middot; brief_qc.json unreadable</summary>'
            f'<ul><li>{html.escape(str(exc))}</li></ul>'
            '</details></div>'
        )
    blocking = list(payload.get("blocking") or [])
    warnings = list(payload.get("warnings") or [])
    summary = payload.get("summary") or ""
    parts: list[str] = []
    parts.append('<div class="qc-brief-banner">')
    parts.append('<div class="qc-brief-banner-title">Brief-time QC report</div>')
    if summary:
        parts.append(f'<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px;">{html.escape(summary)}</div>')
    if blocking:
        items = "".join(f"<li>{html.escape(str(line))}</li>" for line in blocking)
        parts.append(f'<details class="qc-brief-section qc-brief-blocking" open>'
                     f'<summary><span class="qc-brief-icon">!</span>Must fix &middot; {len(blocking)}</summary>'
                     f'<ul>{items}</ul></details>')
    if warnings:
        items = "".join(f"<li>{html.escape(str(line))}</li>" for line in warnings)
        parts.append(f'<details class="qc-brief-section qc-brief-warning">'
                     f'<summary><span class="qc-brief-icon">~</span>Worth a look &middot; {len(warnings)}</summary>'
                     f'<ul>{items}</ul></details>')
    parts.append('</div>')
    return "".join(parts)


def render_font_banner(out_dir: Path) -> str:
    meta_path = _p.finalize_meta_json(out_dir)
    if not meta_path.exists():
        return ""
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    missing = meta.get("font_missing") or []
    if not missing:
        return ""
    missing_list = ", ".join(html.escape(f) for f in missing)
    return (
        '<div class="font-banner">'
        '<div class="font-banner-title"><span class="font-banner-icon">&#9888;</span> '
        'Thumbnails rendered with font substitution</div>'
        '<div class="font-banner-body">'
        f'The client template uses <strong>{missing_list}</strong>, which is not '
        'installed on this machine. The .pptx files themselves are correct; '
        'PNG thumbnails below show a fallback font.</div>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Per-slide card — adjacency banner + classification badge
# ---------------------------------------------------------------------------

FEEDBACK_FIELDS = [
    ("headline",   "Headline / title",         "Anything to change about the action title?"),
    ("layout",     "Layout / structure",       "Spacing, hierarchy, layout choice: what to change?"),
    ("content",    "Content / data accuracy",  "Wrong number, missing nuance, wording: what to fix?"),
    ("visual",     "Visual polish",            "Colors, alignment, type: anything off?"),
    ("other",      "Other notes",              "Anything else for the redesign?"),
]

# One-click feedback so the reviewer doesn't have to type the common notes.
# A clicked chip is stored in the same feedback store (a synthetic "quick"
# field), so it flows into the copied compile command with no extra plumbing.
QUICK_FEEDBACK = [
    "Too sparse, add detail",
    "Too dense, simplify",
    "Content overlaps / cut off",
    "Wrong layout / structure",
    # owner's decision 2026-10-16: counted, so the wrong-visual rate can be measured
    "Wrong kind of visual",
    "Change the accent color",
    "Title too long, reword",
    "Fix a number / wording",
    "More visual, less text",
    "Add process structure: numbers, icons",
]

# What a chip asks the designer to do, spelled out in the copied feedback. The
# label stays short on the page; the worker gets an instruction it can act on.
# Pages rarely numbered their steps or used shape markers unless told to in
# words every time, so that chip carries the full direction.
QUICK_FEEDBACK_EXPANDED = {
    "Wrong kind of visual": (
        "The kind of visual is wrong: redesign the slide with the visual chosen on the "
        "Storyline tab, or the one named in the notes."),
    "Add process structure: numbers, icons": (
        "Make the structure visible: number the steps or items (01, 02, 03 or "
        "numbers in circles), give each one a simple shape marker or icon drawn "
        "with native shapes (circle, chevron, small rounded square, not emoji or "
        "clip art), and where the items happen in order, connect them with "
        "arrows, chevrons or a line so the sequence reads at a glance."),
    "More visual, less text": (
        "Turn sentences into a visual: a diagram, a chart, numbered steps or "
        "icon-led rows; keep only the words that carry the point."),
}


def render_option_tile(slide: dict, opt: dict, themed_path_str: str) -> str:
    letter = opt["letter"]
    sid = slide["slide_id"]
    page_type = (slide.get("page_type") or "").strip() or "—"

    if opt["png_exists"]:
        thumb = (
            f'<div class="thumb"><img src="{html.escape(file_uri(opt["png"]))}" '
            f'alt="{sid} option {letter}" loading="lazy"></div>'
        )
    else:
        thumb = '<div class="thumb missing">no thumbnail</div>'

    qc_summary = opt.get("qc_summary") or {}
    qc_failed = opt.get("qc_failed_checks") or []
    n_block = int(qc_summary.get("block", 0)) if qc_summary else 0
    n_warn = int(qc_summary.get("warn", 0)) if qc_summary else 0
    if qc_summary is None or qc_summary == {}:
        qc_badge = ""
    elif n_block > 0:
        tooltip = " | ".join(qc_failed[:6]) or "blocking issue"
        qc_badge = f'<div class="qc-badge block" title="{html.escape(tooltip)}">Needs a fix</div>'
    elif n_warn > 0:
        tooltip = " | ".join(qc_failed[:6]) or f"{n_warn} warning(s)"
        qc_badge = f'<div class="qc-badge warn" title="{html.escape(tooltip)}">{n_warn} to check</div>'
    else:
        qc_badge = ""  # a clean option needs no badge

    # classification badge — bottom-right of frame
    classification = opt.get("classification", "native")
    class_badge_html = ""
    if classification == "fallback_mermaid":
        class_badge_html = '<div class="class-badge fallback" title="Mermaid fallback render">MERMAID</div>'
    elif classification == "skeleton_rejected":
        class_badge_html = '<div class="class-badge rejected" title="The designer could not build this layout from the brief">Not built</div>'

    vqc_btn = ""  # the quality check runs on the finished deck, not per option

    # pattern label under the option-meta line
    pattern = opt.get("pattern")
    pattern_html = ""  # internal layout names mean nothing to the reviewer

    # "All options in one deck" mode only (hidden otherwise): keep this option
    # in that deck or leave it out, so "B and C, not A" is the user's own
    # recorded choice instead of files moved aside plus an override.
    keep_btn = (
        f'<button type="button" class="keep-toggle" data-slide="{sid}" '
        f'data-letter="{letter}" onclick="toggleKeep(\'{sid}\', \'{letter}\')" '
        'title="All options in one deck: keep this option in it, or leave it out">'
        'Kept in the all-options deck</button>')

    # Each finding that matters gets its own plain line under the picture
    # (not only the badge's hover text): a stop in red, a "fix it, or give a
    # reason" Major in amber. At most 4 lines per check, then a count.
    qc_lines_html = ""
    rows = []
    for grp in opt.get("qc_plain") or []:
        lines = grp.get("lines") or []
        cls = ("qc-line block" if grp.get("block") else
               "qc-line advisory" if grp.get("advisory") else "qc-line major")
        rows += [f'<div class="{cls}">{html.escape(x)}</div>' for x in lines[:4]]
        if len(lines) > 4:
            rows.append(f'<div class="{cls}">and {len(lines) - 4} more like it</div>')
    if rows:
        qc_lines_html = '<div class="qc-lines">' + "".join(rows) + "</div>"

    return f"""
<div class="option" data-slide="{sid}" data-letter="{letter}" data-pptx="{html.escape(themed_path_str)}">
  <div class="option-frame">{thumb}{qc_badge}{class_badge_html}</div>
  <div class="option-meta">
    <span class="option-letter">Option {letter}</span>
    {pattern_html}
    {vqc_btn}
    {keep_btn}
  </div>
  {qc_lines_html}
</div>
"""


def render_adjacency_banner(slide_n: int, warnings: list[str]) -> str:
    """Render the adjacency advisory banner on a slide's card."""
    if not warnings:
        return ""
    items = "".join(f"<li>{html.escape(w)}</li>" for w in warnings)
    return (
        '<div class="adjacency-banner">'
        '<div class="adjacency-banner-title">'
        '<span class="adjacency-icon">&#8634;</span> Adjacency advisory'
        '</div>'
        f'<ul>{items}</ul>'
        '</div>'
    )


def render_context_ack_chip(slide: dict) -> str:
    """Gap 3: per-slide worker context-ack telemetry chip.

    Shows one of three states next to the slide title:
      - green: worker wrote `_context_ack.txt` with a citation; show the
        first line so the user can see what the worker reasoned against.
      - yellow: `_context.md` was generated AND a reference slide was
        registered, but the worker didn't write an ack file. Advisory.
      - hidden: no `_context.md` (older brief) OR `_context.md` exists but
        the template was registered without a reference slide — the chip
        would be noise on every slide if shown here, so suppress.
    """
    if not slide.get("context_present"):
        return ""
    # Suppress the chip when no reference slide was registered — there's no
    # canonical constraint for the worker to have cited, so a yellow ⚠ on
    # every slide of every build is pure noise we were asked not to
    # ship.
    if not slide.get("context_has_reference"):
        return ""
    if slide.get("context_ack_present"):
        # The designer's own note ("Body zone 184-667px ...") is working
        # detail, not something the person picking needs: say nothing when
        # all is well.
        return ""
    return (
        '<div class="context-chip context-chip-warn">'
        '<span class="context-chip-icon">&#9888;</span> '
        '<strong>Check this slide matches the rest of the deck.</strong> '
        "Its designer may not have followed the template's sample slide."
        '</div>'
    )


def render_steer_receipt(slide: dict) -> str:
    """The steer receipt (owner's decision, 2026-10-14): one row per ruling
    the user gave for this slide (their exact words, from add_ruling.py)
    beside the designer's one-line answer from _steer_answers.txt. A ruling
    with no answer, or added after the design was made, is red, so the user
    sees it before looking at the picture. Below it, what the automatic
    checks from the user's repeated steers found (steer_checks.py). Empty
    when the slide has neither. Never stops the page."""
    try:
        import _context_pack
        import steer_checks
        slide_dir = Path(slide["prompt_path"]).parent
        out_dir = slide_dir.parent
        rows = _context_pack.receipt(out_dir, slide["n"])
        found = steer_checks.run_slide(out_dir, slide["n"])
    except Exception:
        return ""
    if not rows and not found:
        return ""
    tr = []
    for r in rows:
        style = "" if r["ok"] else ' style="background:#fde8e8;"'
        ans = html.escape(r["answer"]) if r["ok"] else (
            '<strong style="color:#b42318;">Not answered: ' + html.escape(r["why"]) + "</strong>")
        reading = (f'<div style="color:#667085;font-size:12px;">Chat\'s reading: '
                   f'{html.escape(r["reading"])}</div>') if r.get("reading") else ""
        tr.append(f'<tr{style}><td style="padding:4px 8px;vertical-align:top;">R{r["n"]}</td>'
                  f'<td style="padding:4px 8px;vertical-align:top;">&ldquo;{html.escape(r["quote"])}'
                  f'&rdquo;{reading}</td><td style="padding:4px 8px;vertical-align:top;">{ans}</td></tr>')
    missing = sum(1 for r in rows if not r["ok"])
    head = ""
    if rows:
        head = (f'<div class="field-label">Your rulings for this slide: {len(rows)}'
                + (f', <span style="color:#b42318;">{missing} not answered by the designer</span>'
                   if missing else ", each answered") + "</div>"
                '<table style="border-collapse:collapse;width:100%;font-size:13px;">'
                '<tr><th style="text-align:left;padding:4px 8px;">#</th>'
                '<th style="text-align:left;padding:4px 8px;">What you said</th>'
                '<th style="text-align:left;padding:4px 8px;">What the designer changed</th></tr>'
                + "".join(tr) + "</table>")
    checks = ""
    if found:
        checks = ('<div class="field-label" style="margin-top:6px;">Automatic checks from your '
                  f'repeated steers: {len(found)} to look at</div><ul style="margin:2px 0 0 18px;">'
                  + "".join(f"<li>{html.escape(f)}</li>" for f in found[:8])
                  + (f"<li>... {len(found) - 8} more (steer_checks.py run)</li>" if len(found) > 8 else "")
                  + "</ul>")
    border = "#b42318" if (missing or found) else "#d0d5dd"
    return (f'<div class="steer-receipt" style="border:1px solid {border};border-radius:6px;'
            f'padding:8px 10px;margin:8px 0;">{head}{checks}</div>')


def render_sketch_qc_section(slide: dict) -> str:
    """Per-slide block showing translator self-check results for any
    sketch-path options on this slide.

    Rendered between the option-tile row and the decision buttons. Shows:
      - Per-zone SSIM scores (title / subtitle / body / footer) per option
      - R4 severity chips (Critical red / Major yellow / Advisory gray)
        for any warning the translator emitted.

    Empty string when no option on this slide carries a translation report
    (direct-path builds always hit this path).
    """
    pattern_b_opts = [
        o for o in slide.get("options", [])
        if o.get("translation_report_path") is not None
    ]
    if not pattern_b_opts:
        return ""

    def _ssim_cell(score: Optional[float]) -> str:
        if score is None:
            return '<span class="ssim-na">—</span>'
        try:
            s = float(score)
        except (TypeError, ValueError):
            return '<span class="ssim-na">—</span>'
        # Per Spec 5 §3 thresholds.
        if s >= 0.90:
            cls = "ssim-pass"
        elif s >= 0.85:
            cls = "ssim-major"
        elif s >= 0.70:
            cls = "ssim-major"
        else:
            cls = "ssim-critical"
        return f'<span class="{cls}">{s:.2f}</span>'

    SEVERITY_CSS = {
        "Critical": "r4-chip-critical",
        "Major":    "r4-chip-major",
        "Advisory": "r4-chip-advisory",
    }

    rows = []
    for o in pattern_b_opts:
        letter = o["letter"]
        ssim = o.get("ssim_per_zone") or {}
        ssim_html = (
            f'<span class="ssim-zone">title {_ssim_cell(ssim.get("title"))}</span>'
            f'<span class="ssim-zone">subtitle {_ssim_cell(ssim.get("subtitle"))}</span>'
            f'<span class="ssim-zone">body {_ssim_cell(ssim.get("body"))}</span>'
            f'<span class="ssim-zone">footer {_ssim_cell(ssim.get("footer"))}</span>'
        )
        warnings = o.get("translation_warnings") or []
        if warnings:
            chip_html = "".join(
                f'<span class="r4-chip {SEVERITY_CSS.get(w.get("severity", "Advisory"), "r4-chip-advisory")}" '
                f'title="{html.escape(w.get("detail", ""))}">'
                f'{html.escape(w.get("severity", "Advisory"))}: {html.escape(w.get("code", ""))}'
                f'</span>'
                for w in warnings
            )
        else:
            chip_html = '<span class="r4-chip r4-chip-pass">no warnings</span>'
        rows.append(
            f'<div class="sketch-row">'
            f'<div class="sketch-letter">Option {letter}</div>'
            f'<div class="sketch-ssim">{ssim_html}</div>'
            f'<div class="sketch-chips">{chip_html}</div>'
            f'</div>'
        )

    return (
        '<div class="sketch-qc">'
        '<div class="sketch-qc-title">'
        '<span class="sketch-qc-icon">&#9678;</span> Sketch-path translation QC '
        '<span class="sketch-qc-hint">(per-zone SSIM thresholds: pass &#8805; 0.90; '
        'major 0.85&#8211;0.90; critical &lt; 0.70 per Spec 5)</span>'
        '</div>'
        f'{"".join(rows)}'
        '</div>'
    )


def _page_copy_note(slide: dict) -> str:
    """One line on the card of a page made by script (clone_pages.py,
    2026-10-14): what it is a copy of, and where a comment on it goes."""
    pc = slide.get("page_copy") or {}
    role, m = pc.get("role"), pc.get("master")
    if role == "copy" and isinstance(m, int):
        txt = (f"<strong>A copy of slide {m}'s design</strong>, with this page's own words. "
               f"Pick the same design as slide {m}; a comment here is applied to slide {m}, "
               "and every copy is made again from it.")
    elif role == "copy":
        txt = ("<strong>Filled from the design kept for this template</strong>, word for word "
               "from the storyline. Comment to change it, or ask for a new design.")
    elif role == "master" and pc.get("copies"):
        txt = (f"<strong>Designed once for every section divider</strong>: slides "
               f"{', '.join(map(str, pc['copies']))} are copies of this design.")
    else:
        return ""
    return f'<div class="redo-note" style="display:block;">{txt}</div>'


def render_card(slide: dict, adjacency_warnings: Optional[dict] = None) -> str:
    sid = slide["slide_id"]
    n = slide["n"]
    title = html.escape(slide.get("title") or f"Slide {n}")
    adjacency = (adjacency_warnings or {}).get(n, [])
    adjacency_banner = render_adjacency_banner(n, adjacency)
    # Gap 3: worker context-ack chip (green ✓ with citation, or yellow ⚠
    # when ack is missing). Empty string when there's no _context.md to
    # judge against (older builds).
    context_chip = render_context_ack_chip(slide)

    themed_paths = {
        o["letter"]: (str(o["themed_pptx"].resolve()) if o["themed_exists"] else "")
        for o in slide["options"]
    }
    option_tiles = "".join(
        render_option_tile(slide, o, themed_paths.get(o["letter"], ""))
        for o in slide["options"]
    )

    letters = [o["letter"] for o in slide["options"]]
    pick_buttons = "".join(
        f'<button class="pick" data-letter="{letter}" '
        f'onclick="pickOption(\'{sid}\', \'{letter}\')">PICK {letter}</button>'
        for letter in letters
    )
    # "Replace these" throws this slide's options away and designs new ones
    # (owner's decision, 2026-09-30). It replaced a "+1/+2/+3 more" picker that
    # had nothing behind it: no step added options to one slide, and the page
    # then hid whatever did get built.
    none_btn = (
        f'<button class="none" onclick="pickNone(\'{sid}\')" '
        f'title="Discard these options and design one new one for this slide">'
        '&#8635; REPLACE THESE</button>'
        # One new design by default; "+3 designs" asks three for this slide
        # only (owner's decision 2026-10-13). The page's message carries a
        # "Three designs for:" line that redesign_round.py start --three records.
        f'<button class="none three" onclick="pickThree(\'{sid}\')" '
        f'title="Three new designs instead of one: takes longer and uses more tokens">'
        '+3 DESIGNS</button>'
        # Leaving a slide out is the user's call, recorded with their picks.
        # It replaced compile --drop, which let a slide be dropped with no
        # approval at all, down to an empty deck reported as deliverable.
        f'<button class="pick leave" data-letter="-" '
        f'onclick="pickOption(\'{sid}\', \'-\')" '
        f'title="Leave this slide out of the deck">LEAVE OUT</button>'
    )
    more_picker = ""
    # A content finding (the takeaway repeats the title): once per slide, as
    # its own line; the user's wording choice, never fixed automatically.
    content_html = "".join(
        '<div class="content-line">Your call (wording): ' + html.escape(x) + "</div>"
        for x in slide.get("content_lines") or [])
    n_opts = len(slide["options"])
    layout = "solo" if n_opts == 1 else "multi"
    # per-card inline rule: multi mode uses one column per option
    row_style = "" if layout == "solo" else f' style="grid-template-columns: repeat({n_opts}, 1fr);"'
    chips_html = "".join(
        f'<button type="button" class="chip" data-slide="{sid}" '
        f'data-chip="{html.escape(text)}" onclick="toggleChip(this)">{html.escape(text)}</button>'
        for text in QUICK_FEEDBACK
    )
    feedback_html = "".join(
        f'<div class="feedback-field">'
        f'<label for="fb-{sid}-{key}">{label}</label>'
        f'<textarea id="fb-{sid}-{key}" data-slide="{sid}" data-field="{key}" '
        f'placeholder="{html.escape(placeholder)}"></textarea>'
        f'</div>'
        for (key, label, placeholder) in FEEDBACK_FIELDS
    )
    return f"""
<div class="card" id="card-{sid}" data-slide="{sid}" data-stamp="{slide.get('stamp', '')}" data-layout="{layout}" data-count="{n_opts}">
  <div class="card-header-row">
    <div style="flex:1;">
      <div class="card-num">SLIDE {n}{(' (' + html.escape(slide['fixed_id']) + ')') if slide.get('fixed_id') else ''}</div>
      <div class="card-name">{title}</div>
    </div>
    <div class="kept-mark" id="kept-{sid}" style="display:none;">Kept from last round</div>
    <div class="status-badge pending" id="badge-{sid}">Not decided yet</div>
  </div>

  {adjacency_banner}
  {content_html}
  {render_sketch_notes(slide)}
  {context_chip}
  {render_steer_receipt(slide)}
  {('<div class="content-line visual-line">' + html.escape(slide["visual_line"]) + '</div>') if slide.get("visual_line") else ""}
  {('<div class="redo-note" style="display:block;">&#128204; <strong>Option A reproduces the page you supplied</strong> (' + html.escape(slide["pinned"]) + '). Its figures are checked against the brief before anything compiles.</div>') if slide.get("pinned") else ""}
  {_page_copy_note(slide)}

  <div class="card-body">
  <div class="options-row" data-count="{n_opts}"{row_style}>
    {option_tiles}
  </div>


  <div class="card-controls">
    <div>
      <div class="field-label">Decision</div>
      <div class="decision-buttons">
        {pick_buttons}
        {none_btn}
      </div>
      <div class="hint-text">Pick an option, or Replace these to get one new design for this slide. +3 designs gets three new designs to choose from instead; it takes longer and uses more tokens.</div>
      {more_picker}

      <div class="redo-note" id="regen-{sid}" style="display:none;">
        &#8635; Marked to replace. Say what you want different in the notes below; it goes
        with the request when you click <strong>&#10003; Build my deck</strong>.
      </div>
    </div>

    <div>
      <div class="quick-fb">
        <div class="field-label">Quick feedback</div>
        <div class="hint-text">Click any that apply. No typing needed. On a picked slide they are
        applied to that design before it is converted; "Wrong layout / structure" or asking for
        a different design gets new designs instead.</div>
        <div class="chip-row">
          {chips_html}
        </div>
      </div>
      <div class="field-label">More detail (optional)</div>
      <div class="hint-text">Only if a chip isn't enough. Skip what doesn't apply.</div>
      <div class="feedback-grid">
        {feedback_html}
      </div>
    </div>
  </div>
  </div>
</div>
"""


# ---------------------------------------------------------------------------
# CSS — adjacency-banner + classification-badge + pattern-label
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg: #F4F5F7;          /* app background — soft neutral gray so white cards pop */
  --panel: #FFFFFF;       /* cards, topbar, dialog, toast */
  --panel-2: #EEF1F6;     /* insets: option tiles, textareas, buttons, chips */
  --text: #17202E;        /* primary near-black slate (~14:1 on white) */
  --text-dim: #475569;    /* secondary text / labels (7.4:1 on white) */
  --accent: #A100FF;      /* bright purple — UNCHANGED */
  --accent-soft: #7A0FB8; /* darkened purple — used as text/marks on light bg */
  --approve: #15803D;     /* green-700 — readable as text on white */
  --tweak: #B45309;       /* amber-700 — readable as text on white */
  --reject: #B91C1C;      /* red-700 — AA as text on white */
  --info: #2563EB;        /* blue-600 */
  --pending: #94A3B8;     /* neutral border / muted */
  --border: #E2E8F0;      /* slate-200 hairline */
  --shadow: rgba(15,23,42,0.08);
  --shadow-strong: rgba(15,23,42,0.16);
  --approve-tint: rgba(21,128,61,0.12);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: 'Inter', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.45; padding-bottom: 90px; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code { font-family: Consolas, monospace; font-size: 12px; color: var(--text-dim); word-break: break-all; }

.topbar { position: sticky; top: 0; z-index: 100; background: var(--panel); border-bottom: 2px solid var(--border); padding: 14px 24px; display: flex; align-items: center; gap: 18px; }
.topbar .title { font-size: 17px; font-weight: 700; }
.topbar .title-sub { font-size: 11px; color: var(--text-dim); margin-top: 2px; }
.topbar-meta { font-size: 11px; color: var(--text-dim); margin-top: 6px; display: grid; grid-template-columns: max-content 1fr; gap: 2px 10px; max-width: 1100px; }
.topbar-meta .k { color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; }
.topbar-meta .v { word-break: break-all; }
.summary { display: flex; gap: 10px; flex: 1; margin-left: 16px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.pill { padding: 5px 12px; border-radius: 14px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.pill .num { font-weight: 800; font-variant-numeric: tabular-nums; }
.pill.approve { background: rgba(22,163,74,0.15); color: var(--approve); border: 1px solid var(--approve); }
.pill.reject  { background: rgba(220,38,38,0.15); color: var(--reject);  border: 1px solid var(--reject); }
.pill.pending { background: rgba(100,116,139,0.15); color: var(--text-dim); border: 1px solid var(--pending); }

.storyline-section { background: var(--panel); border-bottom: 1px solid var(--border); padding: 8px 24px 12px; }
.storyline-section summary { font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 1.5px; cursor: pointer; padding: 8px 0; outline: none; list-style: none; }
.storyline-section summary::-webkit-details-marker { display: none; }
.storyline-section summary:hover .storyline-summary-text { color: var(--text); }
.storyline-section[open] summary { border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.storyline-body { max-width: 1200px; margin: 0 auto; padding: 8px 0; }
/* The approved storyline, shown as written: its own styles are dropped and
   these style it (review_storyline.py). */
.sl-embed { font-family: 'Inter', sans-serif; font-size: 14px; line-height: 1.55; color: var(--text); max-width: 860px; }
.sl-embed h1 { font-size: 22px; font-weight: 800; margin: 0 0 12px; }
.sl-embed h2 { font-size: 17px; font-weight: 700; margin: 18px 0 8px; }
.sl-embed h3, .sl-embed h4 { font-size: 14px; font-weight: 700; margin: 14px 0 6px; }
.sl-embed p { margin: 6px 0; }
.sl-embed ul, .sl-embed ol { margin: 4px 0 8px; padding-left: 24px; }
.sl-embed li { margin: 3px 0; }
.sl-embed table { border-collapse: collapse; margin: 8px 0; font-size: 13px; }
.sl-embed th, .sl-embed td { border: 1px solid var(--border); padding: 4px 8px; text-align: left; vertical-align: top; }
.sl-embed .dot, .sl-embed .dd-gov { font-weight: 700; margin-top: 12px; }
.sl-embed .note, .sl-embed .bridge { color: var(--text-dim); }
.sl-embed .sl-gov { font-weight: 700; color: var(--accent-soft); margin-bottom: 10px; }
.sl-embed .sl-heads li { font-weight: 600; padding: 2px 0; }
.sl-warn { margin: 0 0 8px; padding: 7px 12px; background: rgba(202,138,4,0.14); border-left: 3px solid var(--tweak); color: #78350F; font-size: 12px; line-height: 1.4; }
.dd-container { font-family: 'Inter', sans-serif; line-height: 1.5; color: var(--text); }
.dd-title { font-size: 22px; font-weight: 800; color: var(--text); margin: 0 0 14px; }
.dd-deck-meta { display: grid; grid-template-columns: max-content 1fr; gap: 4px 14px; font-size: 13px; margin-bottom: 16px; }
.dd-deck-meta .lbl { color: var(--text-dim); font-weight: 700; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; padding-top: 3px; }
.dd-deck-meta .val { color: var(--text); }
.dd-deck-meta .val.gov { color: var(--accent-soft); font-weight: 600; }
.dd-callout { background: rgba(161,0,255,0.08); border-left: 3px solid var(--accent); padding: 10px 14px; font-size: 12px; color: var(--text-dim); font-style: italic; margin: 14px 0; }
.dd-slide { padding: 10px 0 14px; border-top: 1px solid var(--border); }
.dd-slide:first-of-type { border-top: 0; }
.dd-slide-title { font-size: 10px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.dd-gov { font-size: 14px; font-weight: 700; color: var(--text); margin: 0 0 8px; line-height: 1.35; }
.dd-gov::before { content: "● "; color: var(--accent); }
.dd-gov.missing { color: var(--text-dim); font-style: italic; font-weight: 500; }
.dd-bullets { list-style: none; margin: 4px 0 0; padding-left: 22px; }
.dd-bullets li { font-size: 13px; color: var(--text-dim); padding: 3px 0; position: relative; line-height: 1.5; }
.dd-bullets li::before { content: "– "; color: var(--accent-soft); position: absolute; left: -16px; }

/* Gap 3: worker context-ack chip */
.context-chip { margin: 0 20px 10px; padding: 8px 12px; border-radius: 4px; font-size: 12px; line-height: 1.4; }
.context-chip-icon { margin-right: 6px; font-weight: 700; }
.context-chip-ok { background: rgba(16,185,129,0.12); border-left: 3px solid #10B981; color: #065F46; }
.context-chip-ok strong { color: #047857; }
.context-chip-warn { background: rgba(202,138,4,0.14); border-left: 3px solid var(--tweak); color: #78350F; }
.context-chip-warn strong { color: var(--tweak); }

/* adjacency advisory banner */
.adjacency-banner { margin: 0 20px 12px; padding: 10px 14px; background: rgba(202,138,4,0.14); border-left: 4px solid var(--tweak); border-radius: 4px; color: #78350F; font-size: 13px; line-height: 1.45; }
.adjacency-banner-title { font-size: 11px; font-weight: 800; color: var(--tweak); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.adjacency-icon { color: var(--tweak); margin-right: 4px; }
.adjacency-banner ul { margin: 4px 0 0; padding-left: 18px; }
.adjacency-banner li { padding: 2px 0; }

/* Sketch-path translation QC */
.sketch-qc { margin: 0 20px 14px; padding: 10px 14px; background: rgba(99,102,241,0.10); border-left: 4px solid #6366F1; border-radius: 4px; color: #3730A3; font-size: 12.5px; line-height: 1.5; }
.sketch-qc-title { font-size: 11px; font-weight: 800; color: #4338CA; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.sketch-qc-icon { color: #4338CA; margin-right: 4px; }
.sketch-qc-hint { font-weight: 500; text-transform: none; letter-spacing: 0; color: var(--text-dim); font-size: 11px; margin-left: 6px; }
.sketch-row { display: grid; grid-template-columns: 80px 1fr 1fr; gap: 14px; padding: 4px 0; align-items: center; }
.sketch-letter { font-weight: 700; color: #3730A3; font-size: 12px; }
.sketch-ssim { display: flex; gap: 12px; flex-wrap: wrap; font-size: 11.5px; color: var(--text-dim); }
.sketch-ssim .ssim-zone { display: inline-flex; gap: 4px; align-items: center; }
.sketch-ssim .ssim-pass     { color: #047857; font-weight: 600; font-variant-numeric: tabular-nums; }
.sketch-ssim .ssim-major    { color: var(--tweak); font-weight: 600; font-variant-numeric: tabular-nums; }
.sketch-ssim .ssim-critical { color: var(--reject); font-weight: 700; font-variant-numeric: tabular-nums; }
.sketch-ssim .ssim-na       { color: var(--text-dim); }
.sketch-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.r4-chip { display: inline-block; padding: 2px 8px; border-radius: 11px; font-size: 10.5px; font-weight: 700; letter-spacing: 0.25px; }
.r4-chip-critical { background: rgba(248,113,113,0.16); color: #991B1B; border: 1px solid rgba(248,113,113,0.35); }
.r4-chip-major    { background: rgba(251,191,36,0.16); color: #92400E; border: 1px solid rgba(251,191,36,0.35); }
.r4-chip-advisory { background: rgba(148,163,184,0.16); color: #475569; border: 1px solid rgba(148,163,184,0.30); }
.r4-chip-pass     { background: rgba(16,185,129,0.14); color: #065F46; border: 1px solid rgba(16,185,129,0.30); }

/* classification badge on option frame */
.class-badge { position: absolute; bottom: 6px; right: 6px; padding: 3px 8px; border-radius: 10px; font-size: 9px; font-weight: 800; letter-spacing: 0.6px; line-height: 1.1; z-index: 2; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: help; }
.class-badge.fallback { background: var(--info); color: #fff; }
.class-badge.rejected { background: var(--reject); color: #fff; }

/* pattern label under option meta */
.option-pattern { color: var(--accent-soft); margin-top: 2px; font-size: 11px; font-weight: 600; font-style: italic; }

.font-banner { background: #FEF3C7; border-bottom: 2px solid #F59E0B; padding: 14px 24px; color: #78350F; }
.font-banner-title { font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.font-banner-icon { color: #D97706; margin-right: 6px; }
.font-banner-body { font-size: 13px; line-height: 1.5; }

.vision-qc-btn { display: inline-block; margin-left: auto; padding: 3px 10px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid var(--border); background: var(--panel); color: var(--text-dim); border-radius: 3px; cursor: pointer; transition: all 0.15s; }
.vision-qc-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
.vision-qc-btn.copied { background: var(--approve); color: white; border-color: var(--approve); }

.qc-brief-banner { background: var(--panel-2); border-bottom: 1px solid var(--border); padding: 12px 24px; }
.qc-brief-banner-title { font-size: 10px; font-weight: 800; color: var(--text); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.qc-brief-section { margin-top: 6px; padding: 8px 12px; border-radius: 4px; border-left: 3px solid; font-size: 11px; line-height: 1.5; }
.qc-brief-blocking { background: rgba(220,38,38,0.08); border-color: var(--reject); }
.qc-brief-warning  { background: rgba(202,138,4,0.08); border-color: var(--tweak); }
.qc-brief-info     { background: rgba(37,99,235,0.08); border-color: var(--info); }
.qc-brief-section summary { font-weight: 800; cursor: pointer; outline: none; display: flex; align-items: center; gap: 6px; padding: 2px 0; list-style: none; }
.qc-brief-section summary::-webkit-details-marker { display: none; }
.qc-brief-blocking summary { color: var(--reject); }
.qc-brief-warning  summary { color: var(--tweak); }
.qc-brief-info     summary { color: var(--info); }
.qc-brief-icon { display: inline-block; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-weight: 800; }
.qc-brief-blocking .qc-brief-icon { background: var(--reject); color: white; }
.qc-brief-warning  .qc-brief-icon { background: var(--tweak); color: white; }
.qc-brief-info     .qc-brief-icon { background: var(--info); color: white; }
.qc-brief-section ul { list-style: none; margin: 0; padding: 0; }
.qc-brief-section li { padding: 4px 0 4px 12px; position: relative; color: var(--text); }
.qc-brief-section li::before { content: '•'; position: absolute; left: 0; color: currentColor; }

.cards { padding: 20px; display: flex; flex-direction: column; gap: 20px; max-width: 1880px; margin: 0 auto; }
.card { background: var(--panel); border-radius: 8px; border: 1px solid var(--border); overflow: hidden; }
.card-header-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 14px 20px 10px; border-bottom: 1px solid var(--border); }
.card-num { font-size: 11px; color: var(--text-dim); font-weight: 700; letter-spacing: 1px; }
.card-name { font-size: 16px; font-weight: 700; margin-top: 3px; }
.status-badge { font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 12px; }
.status-badge.pending { background: rgba(100,116,139,0.18); color: var(--text-dim); border: 1px solid var(--pending); }
.status-badge.picked  { background: rgba(22,163,74,0.18); color: var(--approve); border: 1px solid var(--approve); }
.status-badge.none    { background: rgba(220,38,38,0.18); color: var(--reject); border: 1px solid var(--reject); }
/* A pick carried over from the last round (recorded by record_picks.py) */
.kept-mark { font-size: 10px; font-weight: 600; padding: 3px 8px; margin-right: 8px; border-radius: 10px; color: var(--text-dim); background: var(--panel-2); }
.kept-mark.edited { color: var(--approve); }

/* MULTI (2-3 options): thumbnails compare side-by-side across the top; the
   column count comes from an inline style keyed to the option count. */
.options-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 14px 20px; }
.option { background: var(--panel-2); border: 2px solid var(--border); border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform 0.12s, box-shadow 0.12s, border-color 0.12s; }
.option:hover { transform: translateY(-2px); box-shadow: 0 8px 18px var(--shadow-strong); border-color: var(--accent); }
.option.picked { border-color: var(--approve); background: var(--approve-tint); box-shadow: 0 0 0 3px var(--approve-tint), 0 8px 20px var(--shadow-strong); }
.option.picked .option-frame::after { content: "\2713  PICKED"; position: absolute; top: 8px; left: 8px; z-index: 3; background: var(--approve); color: #fff; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; padding: 4px 9px; border-radius: 6px; box-shadow: 0 2px 6px var(--shadow-strong); }
/* Once a pick exists on a multi-option card, fade the non-picked tiles. */
.card.has-pick .options-row[data-count="2"] .option:not(.picked),
.card.has-pick .options-row[data-count="3"] .option:not(.picked) { opacity: 0.5; }

/* SOLO (1 option): big HERO thumbnail on the left, decision + feedback stacked
   on the right. Eye path: see the slide -> decide -> annotate. */
.card[data-layout="solo"] .card-body { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(340px, 1fr); grid-template-areas: "thumb controls" "qc qc"; gap: 22px; align-items: start; padding: 16px 20px 18px; }
.card[data-layout="solo"] .options-row  { grid-area: thumb;    display: block; padding: 0; max-width: 1120px; }
.card[data-layout="solo"] .sketch-qc    { grid-area: qc;       margin: 0; }
.card[data-layout="solo"] .card-controls{ grid-area: controls; grid-template-columns: 1fr; gap: 18px; padding: 0; border-top: none; }
.card[data-layout="solo"] .feedback-grid{ grid-template-columns: 1fr; }
@media (max-width: 1100px) {
  .card[data-layout="solo"] .card-body { grid-template-columns: 1fr; grid-template-areas: "thumb" "controls" "qc"; }
  .card[data-layout="solo"] .options-row { max-width: none; }
}
.option-frame { background: #fff; width: 100%; aspect-ratio: 16/9; overflow: hidden; position: relative; }
.option-frame .thumb { width: 100%; height: 100%; }
.option-frame .thumb img { width: 100%; height: 100%; object-fit: contain; display: block; background: #fff; }
.option-frame .thumb.missing { display: flex; align-items: center; justify-content: center; background: rgba(185,28,28,0.10); color: var(--reject); font-size: 11px; font-weight: 600; }
.option-meta { padding: 8px 10px 10px; font-size: 11px; }
.option-letter { font-size: 11px; font-weight: 800; color: var(--accent); text-transform: uppercase; }
.option-taxon { color: var(--text-dim); margin-top: 2px; font-size: 11px; }
.qc-badge { position: absolute; top: 6px; right: 6px; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: 800; letter-spacing: 0.5px; line-height: 1.1; z-index: 2; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: help; }
.qc-badge.ok    { background: var(--approve); color: #fff; }
.qc-badge.warn  { background: var(--tweak);   color: #fff; }
.qc-badge.block { background: var(--reject);  color: #fff; }
.qc-lines { margin-top: 6px; display: flex; flex-direction: column; gap: 3px; }
.qc-line { font-size: 12px; line-height: 1.35; padding: 3px 6px; border-left: 3px solid var(--tweak); background: rgba(0,0,0,0.03); }
.qc-line.block { border-left-color: var(--reject); }
.qc-line.advisory { border-left-color: var(--border); color: var(--text-dim); }
.content-line { font-size: 13px; line-height: 1.4; margin: 6px 0; padding: 6px 10px; border-left: 3px solid var(--tweak); background: rgba(0,0,0,0.03); }

.card-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 14px 20px 18px; border-top: 1px solid var(--border); }
.decision-buttons { display: flex; flex-wrap: wrap; gap: 6px; }
.decision-buttons button { flex: 1 1 120px; padding: 11px 6px; font-size: 11px; font-weight: 700; border-radius: 5px; border: 2px solid transparent; background: var(--panel-2); color: var(--text-dim); cursor: pointer; transition: all 0.15s; font-family: inherit; }
.decision-buttons button:hover { filter: brightness(1.18); border-color: var(--accent); color: var(--accent); }
.decision-buttons button.none:hover { border-color: var(--reject); color: var(--reject); }
.decision-buttons button.active.pick { background: var(--approve); color: white; border-color: var(--approve); }
.decision-buttons button.active.none { background: var(--reject); color: white; border-color: var(--reject); }

textarea { width: 100%; min-height: 44px; background: var(--panel-2); color: var(--text); border: 1px solid var(--border); border-radius: 5px; padding: 7px 10px; font-family: inherit; font-size: 12px; line-height: 1.4; resize: vertical; }
.field-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
.hint-text { font-size: 11px; color: var(--text-dim); margin-bottom: 10px; font-style: italic; }
.feedback-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; }
.feedback-field label { display: block; font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 4px; }
.redo-note { margin-top: 12px; padding: 10px 12px; background: rgba(185,28,28,0.06); border-left: 3px solid var(--reject); border-radius: 4px; font-size: 12px; line-height: 1.5; color: var(--text); }
.redo-note strong { color: var(--accent); }

footer.summary-footer { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255,255,255,0.96); border-top: 1px solid var(--border); box-shadow: 0 -2px 12px var(--shadow); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 14px; z-index: 50; backdrop-filter: blur(6px); }
footer.summary-footer .count { font-size: 14px; font-weight: 700; color: var(--text); }
footer.summary-footer .count .num { color: var(--accent); }
footer.summary-footer .btns { display: flex; gap: 8px; flex-wrap: wrap; }
button.btn { background: var(--accent); color: #fff; border: none; padding: 9px 14px; border-radius: 5px; font-size: 12px; font-weight: 700; font-family: inherit; cursor: pointer; transition: opacity 0.12s; }
button.btn:hover { opacity: 0.85; }
button.btn.ghost { background: transparent; border: 1px solid var(--border); color: #334155; }
button.btn.primary { background: var(--accent); color: #fff; border: 1px solid var(--accent); }
button.btn.big { padding: 13px 26px; font-size: 14px; letter-spacing: 0.3px; }
button.btn.small { padding: 6px 11px; font-size: 11px; }

dialog#picks-dialog { background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 0; max-width: 720px; width: 90vw; }
dialog#picks-dialog::backdrop { background: rgba(0,0,0,0.6); }
dialog#picks-dialog .dlg-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
dialog#picks-dialog pre { margin: 0; padding: 16px 18px; background: #0F172A; color: #86EFAC; font-size: 12px; font-family: Consolas, monospace; max-height: 60vh; overflow: auto; white-space: pre-wrap; word-break: break-all; }
dialog#picks-dialog .dlg-foot { padding: 12px 18px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 8px; }

#toast { position: fixed; bottom: 88px; left: 50%; transform: translateX(-50%); background: var(--panel); border: 1px solid var(--accent); box-shadow: 0 6px 20px var(--shadow-strong); color: var(--text); padding: 9px 16px; border-radius: 5px; font-size: 12px; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 200; max-width: 80vw; }
#toast.show { opacity: 1; }

/* Quick-feedback chips */
.quick-fb { margin-bottom: 12px; }
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.chip { font-size: 11px; font-weight: 600; padding: 6px 11px; border-radius: 999px; border: 1.5px solid var(--panel-2); background: var(--panel-2); color: var(--text-dim); cursor: pointer; font-family: inherit; transition: all 0.14s; }
.chip:hover { border-color: var(--accent); color: var(--accent); }
.chip.selected { background: var(--accent); border-color: var(--accent); color: #fff; }

/* All options in one deck: a keep / leave-out switch per option */
.keep-toggle { display: none; margin-top: 6px; font-size: 11px; font-weight: 700; padding: 5px 9px; border-radius: 5px; border: 1.5px solid var(--approve); background: #fff; color: var(--approve); cursor: pointer; font-family: inherit; }
.keep-toggle.off { border-color: var(--reject); color: var(--reject); }
body.all-mode .keep-toggle { display: inline-block; }
body.all-mode .option.left-out .option-frame { opacity: 0.35; }
#btn-all-cancel, #all-mode-hint { display: none; }
body.all-mode #btn-all-cancel { display: inline-block; }
body.all-mode #all-mode-hint { display: block; font-size: 12px; color: var(--text-dim); max-width: 460px; }
"""


# ---------------------------------------------------------------------------
# JS — picks + feedback + clipboard logic
# ---------------------------------------------------------------------------

JS = r"""
// Store namespace: the BUILD (out dir), not the file path. Keying on
// window.location.pathname gave "REVIEW.html" and a "REVIEW (shareable).html"
// copy two independent pick stores, so picks made in one were invisible to the
// other — a silent way to lose or transpose a decision. Version bumped to v2
// because the pick store schema changed from {pptxPath: letter} to {sid: letter}.
const PICK_NS   = "::" + (window.__OUT_DIR__ || window.location.pathname);
// v3: a pick is stored with the stamp of the slide it was made on, and only
// counts while that stamp still matches (see pickForSlide).
const PICKS_KEY = "slidelab_picks_v3" + PICK_NS;
// v3: comments are scoped per slide like picks, with the slide's stamp. A
// slide whose designs changed (edited in place from these comments, or
// redesigned) starts with no comments; comments on untouched slides stay.
const FB_KEY    = "slidelab_feedback_v3" + PICK_NS;
const REGEN_KEY = "slidelab_regen_v3"    + PICK_NS;
// All-options deck: the options the user switched to Leave out, per slide,
// with the slide's stamp (a rebuilt slide starts with every option kept).
const KEEP_KEY  = "slidelab_keep_v1"     + PICK_NS;
const STAMPS = window.__STAMPS__ || {};
// Picks recorded by record_picks.py in an earlier round, for slides whose
// designs are unchanged (or were edited in place from the user's comments,
// same letter). Written into the page by build_review.py, so they show in
// any browser. A choice made on this page wins over them.
const SERVER_PICKS = window.__SERVER_PICKS__ || {};

// Must match _state.fnv1a32 / approval_check character for character.
function fnv1a32(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 0x01000193) >>> 0;
    }
    return ("00000000" + h.toString(16)).slice(-8);
}
function canonicalPicks(picks) {
    return Object.keys(picks).sort().map(k => k + "=" + picks[k]).join(";");
}
function approvalCheck(canonical) { return fnv1a32(window.__REVIEW_TOKEN__ + "|" + canonical); }
const TOTAL_SLIDES = window.__TOTAL_SLIDES__;
const SLIDE_IDS = window.__SLIDE_IDS__;
const SLIDE_MAP = window.__SLIDE_MAP__;

// Saved in the browser so choices survive closing the page. Where the browser
// refuses (a page opened from inside another file, strict company settings)
// choices are kept in memory for this visit instead of breaking the buttons.
var memStore = {};
function loadJson(key) {
  var raw = null;
  try { raw = localStorage.getItem(key); } catch (e) { raw = memStore[key] || null; }
  try { return JSON.parse(raw || "{}"); } catch (e) { return {}; }
}
function saveJson(key, obj) {
  var raw = JSON.stringify(obj);
  memStore[key] = raw;
  try { localStorage.setItem(key, raw); } catch (e) {}
}
function loadPicks()  { return loadJson(PICKS_KEY); }
function savePicks(p) { saveJson(PICKS_KEY, p); }
function loadRegens() { return loadJson(REGEN_KEY); }
function saveRegens(r){ saveJson(REGEN_KEY, r); }
function loadThrees() { return loadJson(REGEN_KEY + "_three"); }
function saveThrees(r){ saveJson(REGEN_KEY + "_three", r); }
function isThree(sid) { return isReplace(sid) && loadThrees()[sid] === STAMPS[sid]; }
function loadFb()     { return loadJson(FB_KEY); }
function loadKeep()   { return loadJson(KEEP_KEY); }
function saveKeep(k)  { saveJson(KEEP_KEY, k); }
function saveFb(f)    { saveJson(FB_KEY, f); }

function pickForSlide(sid) {
    // A pick counts only while the slide still has the options it was made on.
    // A rebuilt slide gets a new stamp, so its old pick falls away and the
    // reviewer has to look at the new design; every other slide keeps its pick.
    const v = loadPicks()[sid];
    if (v && typeof v === "object" && v.s === STAMPS[sid]) return v.l || null;  // null: cleared here
    return keptPick(sid);
}
function keptPick(sid) {
    // A pick carried over from the last round (server record), single letter only.
    const sp = SERVER_PICKS[sid];
    return (sp && typeof sp.letter === "string" && /^([A-F]|-)$/.test(sp.letter)) ? sp.letter : null;
}
function isKeptFromLastRound(sid) {
    const v = loadPicks()[sid];
    const local = (v && typeof v === "object" && v.s === STAMPS[sid]);
    const k = keptPick(sid);
    return !!k && (!local || v.l === k);
}
function fbFor(sid) {
    const v = loadFb()[sid];
    return (v && typeof v === "object" && v.s === STAMPS[sid] && v.f) ? v.f : {};
}
function setFb(sid, field, value) {
    const fb = loadFb();
    const cur = (fb[sid] && fb[sid].s === STAMPS[sid] && fb[sid].f) ? fb[sid].f : {};
    if (value) cur[field] = value; else delete cur[field];
    if (Object.keys(cur).length) fb[sid] = { s: STAMPS[sid], f: cur }; else delete fb[sid];
    saveFb(fb);
}
function isReplace(sid) { return loadRegens()[sid] === STAMPS[sid]; }

function renderSlideState(sid) {
    const card = document.getElementById("card-" + sid);
    if (!card) return;
    const letter = pickForSlide(sid);
    const isNone = isReplace(sid);

    card.querySelectorAll(".option").forEach(opt => {
        opt.classList.toggle("picked", opt.dataset.letter === letter);
    });
    card.classList.toggle("has-pick", !!letter);
    card.querySelectorAll(".decision-buttons button").forEach(btn => {
        btn.classList.remove("active");
    });
    if (letter) {
        const btn = card.querySelector(`.decision-buttons button.pick[data-letter="${letter}"]`);
        if (btn) btn.classList.add("active");
    } else if (isNone) {
        const btn = card.querySelector(isThree(sid) ? ".decision-buttons button.none.three"
                                                    : ".decision-buttons button.none:not(.three)");
        if (btn) btn.classList.add("active");
    }

    const badge = document.getElementById("badge-" + sid);
    badge.classList.remove("pending", "picked", "none");
    if (letter) { badge.classList.add("picked"); badge.textContent = letter === "-" ? "Left out" : "Picked " + letter; }
    else if (isNone) { badge.classList.add("none");
                       badge.textContent = isThree(sid) ? "Three new designs requested"
                                                        : "One new design requested"; }
    else { badge.classList.add("pending"); badge.textContent = "Not decided yet"; }

    const kept = document.getElementById("kept-" + sid);
    if (kept) {
        const on = !!letter && isKeptFromLastRound(sid);
        kept.style.display = on ? "inline-block" : "none";
        const edited = on && SERVER_PICKS[sid] && SERVER_PICKS[sid].edited;
        kept.classList.toggle("edited", !!edited);
        kept.textContent = edited ? "Kept from last round, edited from your comments"
                                  : "Kept from last round";
    }

    const regenPanel = document.getElementById("regen-" + sid);
    if (regenPanel) regenPanel.style.display = isNone ? "block" : "none";
}

function updateCounts() {
    let picked = 0, none = 0;
    SLIDE_IDS.forEach(sid => {
        if (pickForSlide(sid)) picked++;
        else if (isReplace(sid)) none++;
    });
    document.getElementById("count-picked").textContent = picked;
    document.getElementById("count-none").textContent = none;
    document.getElementById("count-pending").textContent = TOTAL_SLIDES - picked - none;
    document.getElementById("pick-count").textContent = picked;
    document.getElementById("total-slides").textContent = TOTAL_SLIDES;
}

function leftOut(sid) {
    const v = loadKeep()[sid];
    return (v && v.s === STAMPS[sid] && Array.isArray(v.out)) ? v.out : [];
}
function keptLetters(sid) {
    const out = leftOut(sid);
    return Object.keys(SLIDE_MAP[sid] || {}).filter(L => out.indexOf(L) === -1).sort();
}
function renderKeep(sid) {
    const out = leftOut(sid);
    document.querySelectorAll('.keep-toggle[data-slide="' + sid + '"]').forEach(b => {
        const off = out.indexOf(b.dataset.letter) !== -1;
        b.classList.toggle("off", off);
        b.textContent = off ? "Left out of the all-options deck" : "Kept in the all-options deck";
        const opt = b.closest(".option");
        if (opt) opt.classList.toggle("left-out", off);
    });
}
function toggleKeep(sid, letter) {
    const k = loadKeep();
    const out = leftOut(sid).slice();
    const i = out.indexOf(letter);
    if (i === -1) out.push(letter); else out.splice(i, 1);
    k[sid] = { s: STAMPS[sid], out: out };
    saveKeep(k);
    renderKeep(sid);
}
function setAllMode(on) {
    document.body.classList.toggle("all-mode", on);
    document.getElementById("btn-all").innerHTML = on
        ? "Copy the all-options message"
        : "All options in one deck &#9888;";
    SLIDE_IDS.forEach(renderKeep);
}

function renderAll() {
    SLIDE_IDS.forEach(renderSlideState);
    SLIDE_IDS.forEach(renderKeep);
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        ta.value = fbFor(ta.dataset.slide)[ta.dataset.field] || "";
    });
    // restore quick-feedback chip selections
    document.querySelectorAll(".chip[data-slide][data-chip]").forEach(chip => {
        const sel = (fbFor(chip.dataset.slide).quick || "").split("; ");
        chip.classList.toggle("selected", sel.indexOf(chip.dataset.chip) !== -1);
    });
    updateCounts();
}

function copyVisionQcPrompt(btn, pptxPath) {
    if (!pptxPath) { showToast("No themed PPTX for this option."); return; }
    const prompt =
        "Run /slide-qc on this single-slide PPTX and report findings as Critical / Major / Advisory.\n\n" +
        "PPTX: " + pptxPath + "\n\n" +
        "Use vision (render to PNG, read zone-by-zone). Don't open PowerPoint.";
    const fallback = function() {
        const ta = document.createElement("textarea");
        ta.value = prompt;
        ta.style.position = "fixed"; ta.style.left = "-9999px";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(prompt).catch(fallback);
    } else { fallback(); }
    btn.classList.add("copied"); btn.textContent = "Copied to clipboard";
    showToast("Vision QC prompt copied.");
    setTimeout(function() { btn.classList.remove("copied"); btn.innerHTML = "Vision QC &rarr;"; }, 2500);
}

function pickOption(sid, letter) {
    // A pick records an OPTION LETTER for a slide. It must not depend on a
    // themed PPTX: that artifact is written by finalize, which runs AFTER the
    // review, so gating here left every button inert on a first-pass build.
    // compile_picks resolves <out>/<slide>/option_<letter>.pptx from the letter.
    const picks = loadPicks();
    // Clicking the pick again clears it. Cleared is stored (l: null), so a
    // pick carried over from the last round does not come back.
    if (pickForSlide(sid) === letter) picks[sid] = { l: null, s: STAMPS[sid] };
    else picks[sid] = { l: letter, s: STAMPS[sid] };
    savePicks(picks);
    const regens = loadRegens();
    if (regens[sid]) { delete regens[sid]; saveRegens(regens); }
    renderSlideState(sid); updateCounts();
}

function pickNone(sid) {
    // Replace these: ONE new design (the default). From "+3 designs" it
    // switches back to one; clicked again it clears the request.
    const regens = loadRegens();
    const threes = loadThrees();
    if (isReplace(sid) && !isThree(sid)) { delete regens[sid]; }
    else {
        regens[sid] = STAMPS[sid];
        const picks = loadPicks();
        picks[sid] = { l: null, s: STAMPS[sid] };
        savePicks(picks);
    }
    delete threes[sid];
    saveRegens(regens); saveThrees(threes);
    renderSlideState(sid); updateCounts();
}

function pickThree(sid) {
    // +3 designs: three new designs for this slide instead of one. Clicked
    // again it clears the request.
    const regens = loadRegens();
    const threes = loadThrees();
    if (isThree(sid)) { delete regens[sid]; delete threes[sid]; }
    else {
        regens[sid] = STAMPS[sid];
        threes[sid] = STAMPS[sid];
        const picks = loadPicks();
        picks[sid] = { l: null, s: STAMPS[sid] };
        savePicks(picks);
    }
    saveRegens(regens); saveThrees(threes);
    renderSlideState(sid); updateCounts();
}

function wireFeedback() {
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        ta.addEventListener("input", () => setFb(ta.dataset.slide, ta.dataset.field, ta.value));
    });
}

// Quick-feedback chips: a clicked chip is stored in the same feedback store
// under a synthetic "quick" field, so it rides into the compile command like
// any typed note. Multiple chips on one slide are joined with "; ".
function toggleChip(btn) {
    btn.classList.toggle("selected");
    const sid = btn.dataset.slide;
    const card = document.getElementById("card-" + sid);
    const selected = Array.from(card.querySelectorAll(".chip.selected"))
        .map(c => c.dataset.chip);
    setFb(sid, "quick", selected.join("; "));
}

function feedbackText() {
    const bySlide = {};
    SLIDE_IDS.forEach(sid => {
        const f = fbFor(sid);
        Object.keys(f).forEach(k => {
            if (f[k] && f[k].trim()) {
                if (!bySlide[sid]) bySlide[sid] = {};
                bySlide[sid][k] = f[k];
            }
        });
    });
    if (!Object.keys(bySlide).length) return "";
    let t = "Feedback:\n";
    Object.keys(bySlide).sort().forEach(sid => {
        t += "  " + sid + ":\n";
        Object.keys(bySlide[sid]).forEach(k => {
            let v = bySlide[sid][k];
            if (k === "quick") {
                // spell out what each clicked chip asks the designer to do
                const X = window.__QUICK_EXPANDED__ || {};
                v = v.split("; ").map(c => X[c] ? c + " (" + X[c] + ")" : c).join("; ");
            }
            t += "    " + k + ": " + v.replace(/\n/g, " ") + "\n";
        });
    });
    return t;
}

// The approval in plain words: "Picks: 1B 2C 3- (check 1a2b3c4d)". record_picks.py
// turns it back into the canonical list and verifies the same check code.
function plainPicks(body) {
    if (body === "ALL") return "Picks: all options (check " + approvalCheck(body) + ")";
    const parts = body.split(";").map(p => {
        const [k, v] = p.split("=");
        return String(parseInt(k.replace("slide_", ""), 10)) + v;
    });
    return "Picks: " + parts.join(" ") + " (check " + approvalCheck(body) + ")";
}

// Copy that also works inside the one Slide Lab page (2026-10-16): the designs
// and final-check tabs sit in an embedded frame, where the browser often
// refuses navigator.clipboard. The older copy command still works there on a
// click, so try it before falling back to the select-and-Ctrl+C box.
function slCopyLegacy(text) {
    const ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.left = "-9999px"; ta.style.top = "0";
    // While the copy box is open (a modal dialog) the rest of the page cannot
    // take focus, so a textarea outside it copied nothing: put it in the box.
    const host = document.querySelector("dialog[open]") || document.body;
    host.appendChild(ta); ta.focus(); ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    host.removeChild(ta);
    return ok;
}
async function slCopy(text) {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text); return true;
        }
    } catch (e) { /* blocked in a frame: try the older way */ }
    return slCopyLegacy(text);
}

async function copyOut(cmd, label, heading) {
    // The one Slide Lab page's header line comes first (2026-10-16): the
    // recording script refuses a message from another deck or an older page.
    if (window.__HEADER__) cmd = window.__HEADER__ + "\n" + cmd;
    if (await slCopy(cmd)) showToast(label);
    else showDialog(cmd, heading + ": if nothing was copied, click in the box, Ctrl+A, Ctrl+C");
}

async function buildDeck() {
    const picks = {};
    SLIDE_IDS.forEach(sid => { const l = pickForSlide(sid); if (l) picks[sid] = l; });
    const replace = SLIDE_IDS.filter(isReplace);
    const pending = SLIDE_IDS.filter(sid => !picks[sid] && !isReplace(sid));

    // Every slide needs a decision. A partial pick list used to compile into a
    // shorter deck with nothing saying so.
    if (pending.length) {
        showToast(pending.length + " slide(s) still need a pick or Replace these: " +
                  pending.join(", "));
        return;
    }

    if (!replace.length && SLIDE_IDS.every(sid => picks[sid] === "-")) {
        showToast("Every slide is marked Leave out; there would be nothing to build.");
        return;
    }

    // Any Replace request means another design round, not a build.
    if (replace.length) {
        let cmd = "Redesign some slides in my Slide Lab deck.\n";
        cmd += "Folder: " + window.__OUT_DIR__ + "\n";
        cmd += "New designs for: " + replace.map(s => "slide " + parseInt(s.replace("slide_", ""), 10)).join(", ") + "\n";
        // One new design each unless the user clicked +3 designs on that slide.
        const threes = replace.filter(isThree);
        if (threes.length)
            cmd += "Three designs for: " + threes.map(s => "slide " + parseInt(s.replace("slide_", ""), 10)).join(", ") + "\n";
        // Check-coded like the build line, so redesign_round.py can record
        // them before the redesign and skip a second picking page.
        if (Object.keys(picks).length)
            cmd += plainPicks(canonicalPicks(picks)).replace(/^Picks:/, "Keep:") + "\n";
        const nums = s => s.map(x => parseInt(x.replace("slide_", ""), 10)).join(",");
        cmd += "(Claude: record it with redesign_round.py start --out <Folder> --slides " +
               nums(replace) + (threes.length ? " --three " + nums(threes) : "") +
               (Object.keys(picks).length ? " --kept \"<the Keep line>\"" : "") + ")\n";
        cmd += feedbackText();
        return copyOut(cmd, "Update command copied. Paste into Claude Code.",
                       "Update command (Ctrl+C to copy)");
    }

    // Every slide picked: record exactly these picks, check-coded, then convert
    // only the picked sketches and show the finished slides for a final look.
    const body = canonicalPicks(picks);
    let cmd = "Build my Slide Lab deck.\n";
    cmd += "Folder: " + window.__OUT_DIR__ + "\n";
    cmd += plainPicks(body) + "\n";
    cmd += feedbackText();
    return copyOut(cmd, "Copied. Paste it into Claude.",
                   "Copy this into Claude (Ctrl+C)");
}

async function buildAllOptions() {
    // Every option the user keeps, converted and stacked in one labeled deck,
    // for side-by-side comparison. The first click shows a keep / leave-out
    // switch on every option (all kept); the second copies the message.
    if (!document.body.classList.contains("all-mode")) {
        setAllMode(true);
        showToast("Every option is kept. Switch any you don't want to Leave out, then click again.");
        return;
    }
    const picks = {};
    let nOpts = 0, nMulti = 0;
    SLIDE_IDS.forEach(sid => {
        const ks = keptLetters(sid);
        picks[sid] = ks.length ? ks.join("") : "-";
        nOpts += ks.length;
        if (ks.length > 1) nMulti++;
    });
    if (!nOpts) { showToast("Every option is left out; there would be nothing to build."); return; }
    if (!nMulti) {
        showToast("Each slide keeps one option, so this is a normal deck: pick them and use Build my deck.");
        return;
    }
    // Converting is the expensive step, so say what it costs first.
    const nSlides = SLIDE_IDS.filter(sid => picks[sid] !== "-").length;
    const ratio = nSlides ? (nOpts / nSlides).toFixed(1) : "1";
    const msg = "All options in one deck converts every option you kept: " + nOpts +
        " of them, against " + nSlides + " for a normal build of your picks " +
        "(about " + ratio + "x the conversion cost).\n\n" +
        "Use it only when you need to compare designs side by side.\n\nContinue?";
    if (!confirm(msg)) return;
    let cmd = "Build all options in one Slide Lab deck (the options I kept, labeled).\n";
    cmd += "Folder: " + window.__OUT_DIR__ + "\n";
    cmd += plainPicks(canonicalPicks(picks)) + "\n";
    cmd += feedbackText();
    return copyOut(cmd, "All-options message copied. Paste it into Claude.",
                   "All-options message (Ctrl+C to copy)");
}

function clearAll() {
    if (!confirm("Clear all picks, replace requests, and feedback?")) return;
    // Cleared, not just forgotten: picks carried over from the last round go too.
    const cleared = {};
    SLIDE_IDS.forEach(sid => { cleared[sid] = { l: null, s: STAMPS[sid] }; });
    savePicks(cleared); saveRegens({}); saveFb({}); saveKeep({});
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => ta.value = "");
    document.querySelectorAll(".chip.selected").forEach(c => c.classList.remove("selected"));
    renderAll(); showToast("Cleared.");
}

function showDialog(text, heading) {
    const dlg = document.getElementById("picks-dialog");
    document.getElementById("picks-dlg-head").textContent = heading;
    document.getElementById("picks-dlg-body").textContent = text;
    if (typeof dlg.showModal === "function") dlg.showModal();
    else dlg.setAttribute("open", "");
    try {  // select the text, so Ctrl+C copies it when the clipboard is blocked
        const r = document.createRange();
        r.selectNodeContents(document.getElementById("picks-dlg-body"));
        const s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    } catch (e) {}
}
function showToast(msg) {
    const t = document.getElementById("toast");
    t.textContent = msg; t.classList.add("show");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => t.classList.remove("show"), 1800);
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".option").forEach(el => {
        el.addEventListener("click", (e) => {
            // Don't treat a click on a link or an in-tile button (e.g. Vision QC)
            // as a pick — only bare clicks on the thumbnail select the option.
            if (e.target.closest("a, button")) return;
            pickOption(el.dataset.slide, el.dataset.letter);
        });
    });
    document.getElementById("btn-build").addEventListener("click", buildDeck);
    document.getElementById("btn-all").addEventListener("click", buildAllOptions);
    document.getElementById("btn-all-cancel").addEventListener("click", () => setAllMode(false));
    document.getElementById("btn-clear").addEventListener("click", clearAll);
    document.getElementById("btn-dlg-copy").addEventListener("click", async () => {
        const txt = document.getElementById("picks-dlg-body").textContent;
        if (await slCopy(txt)) showToast("Copied.");
    });
    document.getElementById("btn-dlg-close").addEventListener("click", () => {
        document.getElementById("picks-dialog").close();
    });
    wireFeedback(); renderAll();
});
"""


# ---------------------------------------------------------------------------
# Build HTML — adjacency-warning computation
# ---------------------------------------------------------------------------

def build_html(out_dir: Path, meta: Optional[dict], slides: list, storyline: dict) -> str:
    slide_map: dict[str, dict[str, str]] = {}
    slide_ids: list[str] = []
    slides_by_n: dict[int, dict] = {}
    for s in slides:
        sid = s["slide_id"]
        slide_ids.append(sid)
        slides_by_n[s["n"]] = s
        slide_map[sid] = {}
        for o in s["options"]:
            # Record the best previewable artifact per option, or "" when none
            # exists yet. Picking no longer reads this (it is keyed by slide +
            # letter): gating picks on the themed PPTX, which finalize writes
            # AFTER the review, is what left the pick buttons inert.
            if o["themed_exists"]:
                slide_map[sid][o["letter"]] = str(o["themed_pptx"].resolve())
            elif o.get("src_exists"):
                slide_map[sid][o["letter"]] = str(o["src_pptx"].resolve())
            else:
                slide_map[sid][o["letter"]] = ""

    # compute adjacency warnings across option_A
    adjacency_warnings = compute_adjacency_warnings(slides_by_n, option_letter="A")

    deck_meta = (meta or {}).get("deck_meta", {}) or {}
    deck_type = deck_meta.get("deck_type") or storyline.get("deck_type") or "Slide Lab deck"
    deck_topic = storyline.get("topic") or "Untitled deck"
    governing = deck_meta.get("governing_thought") or storyline.get("governing") or ""
    generated = (meta or {}).get("generated_at") or datetime.now().isoformat(timespec="seconds")
    brief_path = (meta or {}).get("brief", "")
    template_path = (meta or {}).get("template", "")
    slide_count = (meta or {}).get("slide_count", len(slides))
    # client_slug surfaces in the topbar so reviewers can tell different
    # clients' REVIEW.html apart at a glance. Title-cased from the slug.
    client_slug_raw = (meta or {}).get("client_slug", "") or ""
    client_display = (
        client_slug_raw.replace("-", " ").replace("_", " ").title()
        or client_slug_raw
    )

    storyline_html = render_storyline_html(storyline, slides, meta)
    qc_html = render_qc_banner(out_dir)
    font_html = render_font_banner(out_dir)
    preview_html = render_preview_banner(slides)
    cards_html = "\n".join(render_card(s, adjacency_warnings) for s in slides)

    topbar_html = f"""
<div class="topbar">
  <div>
    <div class="title">{html.escape(deck_topic)}: pick a design for each slide ({slide_count} slides)</div>
    <div class="title-sub">{html.escape(deck_type)} &middot; Pick an option for every slide, or Replace these to get new designs.</div>
    <div class="topbar-meta">
      <div class="k">Generated</div><div class="v">{html.escape(generated)}</div>
      <div class="k">Brief</div><div class="v"><code>{html.escape(brief_path)}</code></div>
      <div class="k">Template</div><div class="v"><code>{html.escape(template_path)}</code></div>
      <div class="k">Output</div><div class="v"><code>{html.escape(str(out_dir.resolve()))}</code></div>
      <div class="k">Client</div><div class="v">{html.escape(client_display) if client_display else '<em style="color:#64748B;">(not set)</em>'}</div>
    </div>
  </div>
  <div class="summary">
    <div class="pill approve">&#10003; <span class="num" id="count-picked">0</span></div>
    <div class="pill reject">&#10007; <span class="num" id="count-none">0</span></div>
    <div class="pill pending">&#9675; <span class="num" id="count-pending">{slide_count}</span></div>
  </div>
</div>
"""

    footer_html = """
<footer class="summary-footer">
  <div class="count"><span class="num" id="pick-count">0</span> / <span id="total-slides">0</span> picked &middot; <span style="color:#64748B;font-weight:400;font-size:12px;">picks auto-save in this browser</span></div>
  <div class="btns">
    <div id="all-mode-hint">All options in one deck: every option is kept unless you switch it to Leave out. Click the button again to copy the message.</div>
    <button class="btn ghost small" id="btn-clear">&#x1F5D1; Clear</button>
    <button class="btn ghost small" id="btn-all-cancel">Back to one pick per slide</button>
    <button class="btn ghost small" id="btn-all" title="Converts every option you keep, not just your picks: several times the tokens. Use sparingly.">All options in one deck &#9888;</button>
    <button class="btn primary big" id="btn-build">&#10003; Build my deck</button>
  </div>
</footer>
<div id="toast"></div>
<dialog id="picks-dialog">
  <div class="dlg-head"><h3 id="picks-dlg-head">Output</h3></div>
  <pre id="picks-dlg-body"></pre>
  <div class="dlg-foot">
    <button class="btn ghost" id="btn-dlg-close">Close</button>
    <button class="btn" id="btn-dlg-copy">Copy</button>
  </div>
</dialog>
"""

    # The review token (only build_review mints it, bound to the content hash
    # recorded at prep). The page never shows it bare: it is folded into the
    # check code on the picks line, which record_picks.py verifies.
    review_token = _state.record_review(out_dir)
    stamps_now = {s["slide_id"]: s.get("stamp", "") for s in slides}
    # Picks recorded in an earlier round, only where that slide's designs are
    # the ones it was made on (or were edited in place from the user's
    # comments, same letter). A redesigned slide has new designs: no pick.
    server_picks = _state.remembered_picks(out_dir, stamps_now)
    js_setup = (
        f"window.__SERVER_PICKS__ = {json.dumps(server_picks)};\n"
        f"window.__TOTAL_SLIDES__ = {len(slides)};\n"
        f"window.__SLIDE_IDS__ = {json.dumps(slide_ids)};\n"
        f"window.__QUICK_EXPANDED__ = {json.dumps(QUICK_FEEDBACK_EXPANDED, ensure_ascii=False)};\n"
        f"window.__SLIDE_MAP__ = {json.dumps(slide_map)};\n"
        f"window.__STAMPS__ = {json.dumps({s['slide_id']: s.get('stamp', '') for s in slides})};\n"
        f"window.__OUT_DIR__ = {json.dumps(str(out_dir.resolve()))};\n"
        f"window.__SCRIPTS_DIR__ = {json.dumps(str(Path(__file__).resolve().parent))};\n"
        f"window.__REVIEW_TOKEN__ = {json.dumps(review_token)};\n"
        f"window.__HEADER__ = {json.dumps(_one_page_header(out_dir, 'designs', review_token))};\n"
    )

    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">"
        f"<title>{html.escape(deck_topic)} &mdash; REVIEW</title>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<style>{CSS}</style></head><body>"
        f"{topbar_html}"
        f"{storyline_html}"
        f"{font_html}"
        f"{preview_html}"
        f"{render_form_banner(slides)}"
        f"{qc_html}"
        f"<div class=\"cards\">{cards_html}</div>"
        f"{footer_html}"
        f"<script>{js_setup}{JS}</script>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# Final check (build_review.py --final)
# ---------------------------------------------------------------------------

FINAL_CSS = """
:root { --accent:#A100FF; --text:#0F172A; --dim:#64748B; --border:#E2E8F0; --bg:#F8FAFC; }
* { box-sizing: border-box; }
body { margin:0; font-family: "Segoe UI", Arial, sans-serif; color: var(--text); background: var(--bg); padding-bottom: 150px; }
header { background:#fff; border-bottom:1px solid var(--border); padding:22px 32px; }
h1 { margin:0 0 6px; font-size:22px; }
header p { margin:0; color: var(--dim); font-size:14px; max-width: 900px; line-height:1.5; }
.srccheck { margin:18px 32px 0; padding:14px 18px; background:#FFF8E6; border-left:4px solid #E0A100; font-size:14px; line-height:1.5; }
.srccheck.ok { background:#EEF7EE; border-left-color:#2E7D32; }
.srccheck table { margin-top:8px; border-collapse:collapse; }
.srccheck td { padding:4px 14px 4px 0; vertical-align:top; }
.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(460px, 1fr)); gap:22px; padding:26px 32px; }
.tile { background:#fff; border:1px solid var(--border); border-radius:8px; overflow:hidden; }
.tile img { width:100%; display:block; border-bottom:1px solid var(--border); }
.cap { padding:10px 14px; font-size:13px; }
.cap b { color: var(--accent); }
.cap .t { color: var(--dim); display:block; margin-top:3px; }
footer { position:fixed; left:0; right:0; bottom:0; background:#fff; border-top:1px solid var(--border); padding:14px 32px; display:flex; gap:16px; align-items:flex-end; }
textarea { flex:1; min-height:56px; font:inherit; font-size:13px; padding:8px; border:1px solid var(--border); border-radius:6px; }
button { font:inherit; font-weight:700; border-radius:6px; padding:12px 20px; cursor:pointer; border:1.5px solid var(--accent); }
.go { background: var(--accent); color:#fff; }
.fix { background:#fff; color: var(--accent); }
#toast { position:fixed; bottom:110px; left:50%; transform:translateX(-50%); background:#fff; border:1px solid var(--accent); padding:8px 14px; border-radius:6px; opacity:0; transition:opacity .2s; }
#toast.show { opacity:1; }
"""


def build_final_check(out_dir: Path, meta: Optional[dict]) -> int:
    """The last look before compile: every pick, finished, on the template.

    Owner's decision (2026-09-30): review the sketches, convert only the picks,
    then a short required look at the finished picks before anything is built.
    A sketch shows the design before the template's own title, takeaway and page
    number land on it, which is exactly where collisions live; this page is
    where they become visible. Its Build command carries the token compile needs,
    bound to the bytes of every file shown here.
    """
    state = _state.read_state(out_dir)
    review = state.get("review") or {}
    picks = review.get("picks") or {}
    if not picks:
        print("REFUSED: no approved picks recorded. The user picks in REVIEW.html; "
              "its Build command runs record_picks.py.", file=sys.stderr)
        return 5
    ship = [(k, L) for k, v in sorted(picks.items())
            for L in (v if isinstance(v, list) else [v]) if L != "-"]
    keys = [_state.option_key(int(k.split("_")[1]), L) for k, L in ship]
    problems: list[str] = []
    # The user's comments come before the final look (owner's decision,
    # 2026-10-09): a picked slide with comments is edited (or redesigned) first.
    for c in _state.pending_comments(state):
        problems.append(
            f"{c['slide']} still waits on the user's comment ({c['kind']}): "
            + ("edit the picked design in place, then record_picks.py --edits-done"
               if c["kind"] == "edit" else
               "redesign it (redesign_round.py finish, or REVIEW.html for three designs)")
            + f": {c['text'][:100]}")
    ok, why = _state.check_options_finalized(state, keys)
    if not ok:
        problems.append(why)
    for k, L in ship:
        for name in (_p.option_pptx_name(L), _p.option_png_name(L)):
            if not (out_dir / k / name).exists():
                problems.append(f"{k}/{name} is missing")
    # Slides that copy a supplied page: their check must be made from the
    # finished picks shown here (finalize makes it; this catches up a missing
    # or older one). A pin that cannot be read stops the page.
    cp_rows, cp_slides, cp_bind = [], [], {}
    if not problems:
        try:
            import source_ledger
            _stale = source_ledger.stale_slides(out_dir, state)
            if _stale:
                _built, _errs = source_ledger.build_slides(out_dir, only=set(_stale))
                for _n, _why in _errs:
                    problems.append(f"copied page, slide {_n}: {_why}")
            _gp = [g for g in source_ledger.gate_problems(out_dir)
                   if g[1] in ("missing", "stale")]
            if _gp and not problems:
                problems.append(source_ledger.gate_message(out_dir, _gp))
            cp_rows, cp_slides, cp_bind = source_ledger.final_check_rows(out_dir)
        except Exception as exc:
            problems.append(f"the copied-page check could not run ({type(exc).__name__}: "
                            f"{exc}); run source_ledger.py build --out <out> --all-picked")
    if problems:
        print("NOT READY for the final check:", file=sys.stderr)
        for p in problems[:12]:
            print(f"  - {p}", file=sys.stderr)
        print("Translate any picked sketches, run finalize_deck.py, then try again.",
              file=sys.stderr)
        return 5

    digests = {key: _state.file_digest(out_dir / k / _p.option_pptx_name(L))
               for key, (k, L) in zip(keys, ship)}
    token = _state.record_final_check(out_dir, digests, ledger=cp_bind)

    titles = {_p.slide_key(int(s["n"])): (s.get("title") or "")
              for s in (meta or {}).get("slides", []) if isinstance(s.get("n"), int)}
    tiles = "".join(
        f'<div class="tile"><img src="{html.escape(k)}/{html.escape(_p.option_png_name(L))}" '
        f'alt="{html.escape(k)} option {html.escape(L)}">'
        f'<div class="cap"><b>{html.escape(k.replace("_", " ").title())} &middot; '
        f'option {html.escape(L)}</b>'
        f'<span class="t">{html.escape(titles.get(k, ""))}</span></div></div>'
        for k, L in ship)

    all_options = bool(review.get("all_options"))
    flags = ""
    if all_options:
        flags += " --all-variations --badge"
    if (meta or {}).get("adopted_source"):
        flags += f' --splice-into "{meta["adopted_source"]}"'
    scripts = str(Path(__file__).resolve().parent)
    compile_cmd = (f'py -3 "{scripts}\\compile_picks.py" --out "{out_dir}" '
                   f'--final-token {token}{flags}')
    what = (f"the {len(ship)} options you kept, labeled" if all_options
            else f"{len(ship)} slide(s)")
    # Plain lines the Build it message carries so Claude adds the right options.
    extra_lines = ""
    if all_options:
        extra_lines += "Deck: all options, labeled\n"
    if (meta or {}).get("adopted_source"):
        extra_lines += f"Put back into: {meta['adopted_source']}\n"
    # Numbers and labels on the picks that the brief does not contain, and
    # figures written two ways: the person approving sees what to verify.
    try:
        import source_check
        src_block = source_check.html_block(source_check.check(
            out_dir, [(k, out_dir / k / _p.option_pptx_name(L)) for k, L in ship]))
    except Exception:
        src_block = ""
    # Body text 12 pt (10.5 pt at the lowest), at most 3 body sizes (type_scale.py).
    try:
        import type_scale
        ts_rows = []
        for k, L in ship:
            f = out_dir / k / _p.option_pptx_name(L)
            if f.exists():
                res = type_scale.check_pptx(f, with_notes=True)
                ts_rows.append((f"Slide {int(k.split('_')[-1])}",
                                res[0][1] if res else [], res[0][2] if res else []))
        ts_block = type_scale.html_block(ts_rows)
    except Exception:
        ts_block = ""
    cp_block = _copied_page_table(cp_rows, cp_slides)
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Final check</title><style>{FINAL_CSS}</style></head><body>
<header><h1>Final check: this is exactly what will be built</h1>
<p>Every pick below is finished and on your template ({what}): the real title,
takeaway and page number, which the sketches did not have. Look for anything
overlapping, cut off or crowded. If it is right, click <b>Build it</b> (or
just tell Claude "build it" while this page is open). If not, say what is wrong
in the box instead.</p></header>
{cp_block}
{src_block}
{ts_block}
<div class="grid">{tiles}</div>
<div id="copybox" style="display:none;position:fixed;left:32px;right:32px;bottom:110px;background:#fff;border:1px solid var(--accent);border-radius:6px;padding:10px;z-index:50;">
<div style="font-size:13px;margin-bottom:6px;">If nothing was copied: click in the box, press Ctrl+A then Ctrl+C, and paste it into the chat.</div>
<textarea id="copytext" readonly style="width:100%;min-height:120px;"></textarea></div>
<footer>
<textarea id="fix" placeholder="Something needs fixing? Say which slide and what."></textarea>
<button class="fix" id="btn-fix">Send fixes</button>
<button class="go" id="btn-go">&#10003; Build it</button>
</footer><div id="toast"></div>
<script>
const OUT = {json.dumps(str(out_dir))};
const TOKEN = {json.dumps(token)};
const EXTRA = {json.dumps(extra_lines)};
const HEADER = {json.dumps(_one_page_header(out_dir, "final", token))};
function toast(m) {{ const t = document.getElementById("toast"); t.textContent = m;
  t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1800); }}
// The older copy command, on a textarea that is on the page (a hidden box
// cannot be selected, so copying from it copied nothing).
function copyLegacy(text) {{
  const t = document.createElement("textarea");
  t.value = text; t.setAttribute("readonly", "");
  t.style.position = "fixed"; t.style.left = "-9999px"; t.style.top = "0";
  document.body.appendChild(t); t.focus(); t.select();
  let ok = false;
  try {{ ok = document.execCommand("copy"); }} catch (e) {{ ok = false; }}
  document.body.removeChild(t);
  return ok;
}}
async function copy(text, label) {{
  // "\\n" here: a plain newline inside this Python string broke the whole
  // script, so Build it and Send fixes did nothing (2026-10-16).
  if (HEADER) text = HEADER + "\\n" + text;
  const box = document.getElementById("copybox"), ta = document.getElementById("copytext");
  ta.value = text;
  let ok = false;
  try {{ if (navigator.clipboard && navigator.clipboard.writeText) {{
    await navigator.clipboard.writeText(text); ok = true; }} }} catch (e) {{}}
  if (!ok) ok = copyLegacy(text);
  window.__slidelabLastCopy = {{ text: text, ok: ok }};
  if (ok) {{ box.style.display = "none"; toast(label); }}
  else {{ box.style.display = "block"; ta.focus(); ta.select(); toast("Copy blocked: press Ctrl+C in the box."); }} }}
{_COPIED_PAGE_JS}
document.getElementById("btn-go").onclick = () => {{
  const cp = cpAnswers();
  if (cp === null) return;
  if (cp.replace.length) {{
    copy("Fix these before building my Slide Lab deck.\\nFolder: " + OUT +
         "\\nWhat is wrong: figures copied from the earlier page to replace:\\n" +
         cp.replace.join("\\n") + "\\n", "Copied. Paste it into Claude.");
    return;
  }}
  copy("Build it: I checked the finished slides.\\nFolder: " + OUT +
       "\\nFinal check: " + TOKEN + "\\n" + cp.line + EXTRA,
       "Copied. Paste it into Claude.");
}};
document.getElementById("btn-fix").onclick = () => {{
  const t = document.getElementById("fix").value.trim();
  if (!t) {{ toast("Say what needs fixing first."); return; }}
  copy("Fix these before building my Slide Lab deck.\\nFolder: " + OUT +
       "\\nWhat is wrong: " + t + "\\n", "Copied. Paste it into Claude.");
}};
</script></body></html>"""
    dest = out_dir / "FINAL-CHECK.html"
    one = _one_page_write(out_dir, page, dest, "final")
    print(f"FINAL-CHECK.html written: {dest}")
    if one:
        print(f"Slide Lab page (one file for the whole build, tab 3 Final check): {one}")
    print(f"  {len(ship)} finished option(s). Show it to the user (--open) and wait "
          "for the Build it message it copies, or for the user to say \"build it\" in "
          "chat once it is open (compile_picks.py --approved-in-chat).")
    return 0


# The copied-page table (owner's decision, 2026-10-13, the lighter check):
# the figures that came from a copied page onto a shipping slide and are not
# in the brief word for word, one row each, answered Keep or Replace here.
# Build it stays shut until every row is answered; a Replace turns the
# message into a fix request. Approving this page answers every row on it.
_COPIED_PAGE_JS = r"""
function cpAnswers() {
  const rows = Array.from(document.querySelectorAll("tr.cp-row"));
  const replace = []; let missing = 0;
  rows.forEach(tr => {
    const v = (tr.querySelector("input[type=radio]:checked") || {}).value;
    if (!v) { missing++; return; }
    if (v === "replace") {
      const w = (tr.querySelector("input.cp-with") || {}).value || "";
      replace.push("- slide " + tr.dataset.slide + ": " + JSON.stringify(tr.dataset.figure) +
                   " -> " + (w.trim() || "the brief's figure"));
    }
  });
  if (missing) {
    toast("Answer every row of the copied-page table first (Keep or Replace).");
    document.getElementById("copied-pages").scrollIntoView({behavior: "smooth"});
    return null;
  }
  const line = rows.length ? ("Copied-page figures: all " + rows.length + " kept\n") : "";
  return {replace: replace, line: line};
}
"""


def _copied_page_table(rows: list, slides: list) -> str:
    """FINAL-CHECK.html's one table of figures that came from a copied page."""
    if not slides:
        return ""
    esc = html.escape
    notes = []
    for c in slides:
        if c.get("visual_only"):
            notes.append(f"<li>Slide {c['slide']} copies {esc(c['source'])}, a PDF page or "
                         "picture: nothing on it can be read by machine, so its figures are "
                         "checked by eye only. Take every figure from the brief.</li>")
        elif c.get("brief_matches"):
            notes.append(f"<li>Slide {c['slide']}: {c['brief_matches']} more figure(s) from "
                         f"{esc(c['source'])} match the brief (counted, not listed).</li>")
    body = "".join(
        f'<tr class="cp-row" data-slide="{r["slide"]}" data-figure="{esc(str(r["figure"]))}">'
        f'<td>{r["slide"]}</td><td><b>{esc(str(r["figure"]))}</b></td>'
        f'<td>{esc(str(r.get("source_text", ""))[:160])}<br><span class="cp-src">'
        f'{esc(str(r.get("source", "")))}</span></td>'
        f'<td>{esc(str(r.get("brief_value") or "")) or "<i>no figure in the brief for this slide</i>"}</td>'
        f'<td class="cp-ans"><label><input type="radio" name="cp{i}" value="keep"> Keep</label> '
        f'<label><input type="radio" name="cp{i}" value="replace"> Replace</label>'
        f'<input class="cp-with" placeholder="with (blank = the brief\'s figure)"></td></tr>'
        for i, r in enumerate(rows))
    table = ("" if not rows else
             '<table class="cp"><thead><tr><th>Slide</th><th>Figure</th>'
             '<th>Where it was on the copied page</th><th>Closest line in the brief</th>'
             f'<th>Your answer</th></tr></thead><tbody>{body}</tbody></table>')
    head = (f"{len(rows)} figure(s) came from a page you supplied onto the slides being "
            "built and are not in the brief word for word. Keep each one, or mark it "
            "Replace (blank takes the brief's figure). <b>Build it</b> waits until every "
            "row is answered; saying \"build it\" in chat keeps them all."
            if rows else
            "No figure from the copied pages needs an answer: every one that came through "
            "matches the brief, or none came through.")
    return (f'<section id="copied-pages" class="cp-box"><h2>Numbers copied from your '
            f'pages</h2><p>{head}</p>{table}'
            + (f"<ul>{''.join(notes)}</ul>" if notes else "")
            + "<style>.cp-box{margin:12px 24px;padding:10px 14px;border:1px solid #c9c9c9;"
              "background:#fafafa}.cp-box h2{font-size:15px;margin:0 0 6px}"
              "table.cp{border-collapse:collapse;width:100%;font-size:12px}"
              "table.cp th,table.cp td{border:1px solid #ddd;padding:4px 6px;"
              "text-align:left;vertical-align:top}.cp-src{color:#777;font-size:11px}"
              ".cp-with{width:150px;margin-top:3px;font-size:11px}</style></section>")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build REVIEW.html for slide-builder output.")
    ap.add_argument("--out", required=True, help="Orchestrator output directory.")
    ap.add_argument("--final", action="store_true",
                    help="Build FINAL-CHECK.html instead: every approved pick, finished "
                         "on the template, for the user's last look before compile.")
    ap.add_argument("--template", default=None,
                    help="Client template path. Accepted for CLI consistency with "
                         "the other stages; build_review reads everything it needs "
                         "from --out and does not use it.")
    ap.add_argument("--open", action="store_true",
                    help="Open the page in the default browser after writing it "
                         "(Claude passes this so the user does not have to find the file).")
    args = ap.parse_args(argv)

    from _log import attach as _log_attach
    _log_attach(args.out, "build_review.py")

    out_dir = Path(args.out).resolve()
    if not out_dir.exists() or not out_dir.is_dir():
        print(f"[error] --out is not a directory: {out_dir}", file=sys.stderr)
        return 2

    meta_path = _p.meta_json(out_dir)
    meta: Optional[dict] = None
    if meta_path.exists():
        try:
            meta = json.loads(read_text(meta_path))
            from _meta_schema import validate_warn
            validate_warn(meta, source="build_review")
        except Exception as exc:
            print(f"[warn] _meta.json unreadable ({exc}); falling back.", file=sys.stderr)

    if meta and isinstance(meta.get("slides"), list) and meta["slides"]:
        slide_metas = {int(s["n"]): s for s in meta["slides"]}
        slide_nums = sorted(slide_metas.keys())
    else:
        n_max = discover_slide_count(out_dir)
        slide_nums = list(range(1, n_max + 1))
        slide_metas = {}
        if not slide_nums:
            print(f"[error] no slide_NN directories in {out_dir}", file=sys.stderr)
            return 3

    if args.final:
        rc = build_final_check(out_dir, meta)
        if rc == 0 and args.open:
            try:
                import slidelab_page
                _target = slidelab_page.page_path(out_dir)
                if not _target.exists():
                    _target = out_dir / "FINAL-CHECK.html"
            except Exception:
                _target = out_dir / "FINAL-CHECK.html"
            how = _open_page(_target)
            if how:
                # The page is in front of the user: their "build it" in chat
                # now counts (compile_picks.py --approved-in-chat).
                _state.record_page_opened(out_dir, "final_check", how)
        return rc

    # The Storyline tab comes first (owner's decision 2026-10-16): while it
    # waits for the user, there are no designs to show.
    _sp = (_state.read_state(out_dir).get("storyline_page") or {})
    if _sp.get("status") in ("waiting", "comments"):
        import slidelab_page
        print(f"STOPPED: the Storyline tab of {slidelab_page.page_path(out_dir)} is still "
              "waiting for the user (" + ("their Done message" if _sp.get("status") == "waiting"
                                          else "the chat to apply their comments") + "). No "
              "design should have been made yet.")
        print("Next: record the user's Storyline message with record_storyline.py --out "
              f"\"{out_dir}\" --message \"<the whole message>\", prep again, then the workers.")
        return 9
    # A Must use visual that came back as another kind is redone before the
    # user sees it (owner's decision 2026-10-16). Once per slide.
    _vres = {}
    try:
        import check_visual_type
        _vres = {e["n"]: e for e in check_visual_type.check(out_dir, meta)}
    except Exception as exc:
        print(f"     (the visual check did not run: {type(exc).__name__}: {exc})")
    _redo = [e for n, e in sorted(_vres.items()) if e["mismatch"] and n in slide_metas]
    if _redo:
        rc = _redo_wrong_visuals(out_dir, meta, _redo)
        if rc:
            return rc

    slides = [scan_slide(out_dir, n, slide_metas.get(n)) for n in slide_nums]
    for s in slides:
        try:
            import check_visual_type
            s["visual_line"] = check_visual_type.card_line(_vres.get(s["n"]))
        except Exception:
            pass
    # An adopted external deck rebuilds only some of its slides; the rest stay
    # as they are in the original and are not up for review.
    if meta and meta.get("adopted_source"):
        slides = [s for s in slides
                  if any(p.is_file() for p in (out_dir / s["slide_id"]).glob("option_*"))]

    storyline = {"slides": [], "found": False}
    if meta and meta.get("brief"):
        storyline = parse_brief(Path(meta["brief"]))
    if not storyline.get("found"):
        dm = (meta or {}).get("deck_meta", {}) or {}
        storyline = {
            "topic": (meta or {}).get("out", out_dir.name),
            "deck_type": dm.get("deck_type", ""),
            "governing": dm.get("governing_thought", ""),
            "audience": (dm.get("audience") or "").splitlines()[0] if dm.get("audience") else "",
            "belief_break": "", "belief_leave": "", "say_back": "",
            "slides": [], "found": False,
        }

    total_opts = sum(len(s["options"]) for s in slides)
    missing_png = sum(1 for s in slides for o in s["options"] if not o["png_exists"])
    missing_themed = sum(1 for s in slides for o in s["options"] if not o["themed_exists"])

    html_text = build_html(out_dir, meta, slides, storyline)
    review_path = _p.review_html(out_dir)
    review_path.write_text(html_text, encoding="utf-8")

    print(f"[ok] wrote {review_path}")
    print(f"     {len(slides)} slides, {total_opts} option tiles")
    print(f"     missing PNGs: {missing_png}, missing themed PPTX: {missing_themed}")
    panel = storyline.get("_panel") or {}
    print(f"     storyline panel: {panel.get('source') if panel.get('source') != 'headlines' else 'the slide headlines (no approved storyline file recorded)'}")
    for w in panel.get("warnings") or []:
        print(f"     WARNING: {re.sub(r'<[^>]+>', '', w)}")
    print(f"     size: {fmt_bytes(review_path.stat().st_size)}")
    # The panel must show the storyline as written (owner's decision
    # 2026-10-13): its text equal to the source, and none of the designer
    # wording the old panel showed. Checked on the page as written.
    import review_storyline
    probs = review_storyline.check_panel(review_path.read_text(encoding="utf-8"),
                                         panel.get("expected") or "")
    if probs:
        src = panel.get("source") or "the slide headlines"
        print(f"STOPPED: the storyline panel in {review_path} is not right: "
              + "; ".join(probs) + ".")
        print(f"  It shows {src}. The page was written but NOT opened.")
        if src == "headlines":
            print("  Next: fix that wording in the slide headlines of the brief "
                  f"({(meta or {}).get('brief') or 'the brief'}), re-seal it, prep again, "
                  "then run build_review.py again.")
        else:
            print(f"  Next: fix that wording in {src} (or point approved_storyline in the "
                  "brief's front matter at the storyline the user approved), prep again "
                  "(build_deck.py records it), then run build_review.py again.")
        return 6
    one = _one_page_write(out_dir, review_path.read_text(encoding="utf-8"), review_path, "designs")
    if one:
        print(f"     Slide Lab page (one file for the whole build, tab 2 Slide designs): {one}")
    if args.open:
        how = _open_page(one or review_path)
        if how:
            # Picks typed in chat now count (record_picks.py --approved-in-chat),
            # as long as no slide's options change before they are recorded.
            _state.record_page_opened(out_dir, "review", how,
                                      stamps={s["slide_id"]: s.get("stamp", "") for s in slides})
    return 0


def _one_page_header(out_dir: Path, stage: str, token: str) -> str:
    """The first line of every message the page copies (slidelab_page.py)."""
    try:
        import slidelab_page
        return slidelab_page.header(out_dir, stage, token)
    except Exception:
        return ""


def _one_page_write(out_dir: Path, page: str, dest: Path, stage: str):
    """Write REVIEW.html / FINAL-CHECK.html (kept for one release, with a
    redirect to the one page) and the one Slide Lab page with it as tab 2
    or 3. Returns the one page's path, or None."""
    try:
        import slidelab_page
        dest.write_text(slidelab_page.add_redirect(page, out_dir, stage), encoding="utf-8")
        slidelab_page.mark_part_ready(out_dir, stage)
        return slidelab_page.write(out_dir, stage)
    except Exception as exc:
        dest.write_text(page, encoding="utf-8")
        print(f"     (the Slide Lab page was not written: {type(exc).__name__}: {exc})")
        return None


def _redo_wrong_visuals(out_dir: Path, meta: Optional[dict], entries: list) -> int:
    """Prep again each Must use slide whose design is another kind of visual
    (once per slide; a second miss is shown on its card). Returns 8 when the
    parent must send workers first, else 0."""
    import subprocess
    import check_visual_type
    state = _state.read_state(out_dir)
    done = state.setdefault("visual_redo", {})
    todo = [e for e in entries if not done.get(str(e["n"]))]
    if not todo:
        for e in entries:
            print(f"     WARNING: slide {e['n']} was redone once and still is not "
                  f"{e['wanted']} (Must use): {check_visual_type.card_line(e)} It is shown on "
                  "its card; tell the user.")
        return 0
    tpl = (meta or {}).get("template") or ""
    redone = []
    for e in todo:
        check_visual_type.write_redo_feedback(out_dir, e)
        n_opts = len(e["options"]) or 1
        cmd = [sys.executable, str(Path(__file__).resolve().parent / "build_deck.py"),
               "--slide", str(e["n"]), "--out", str(out_dir), "--template", tpl,
               "--options", str(min(3, n_opts))]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(f"     WARNING: slide {e['n']} could not be prepped again for its visual "
                  f"(exit {r.returncode}): {(r.stderr or r.stdout).strip()[-300:]}")
            continue
        state = _state.read_state(out_dir)
        state.setdefault("visual_redo", {})[str(e["n"])] = {
            "at": datetime.now().isoformat(timespec="seconds"), "wanted": e["wanted"],
            "was": [o["reason"] for o in e["options"]]}
        _state._write(out_dir, state)
        redone.append(e)
    if not redone:
        return 0
    print("STOPPED before the designs tab: a slide marked Must use came back as another "
          "kind of visual, so it was prepped again (the reason is in its _prior_feedback.md):")
    for e in redone:
        print(f"  slide {e['n']}: wanted {e['wanted']}; "
              + "; ".join(f"option {o['letter']}: {o['reason']}" for o in e["options"]
                          if o["follows"] is False))
    nums = ", ".join(str(e["n"]) for e in redone)
    print(f"Send one slide-builder-worker per slide ({nums}) on its slide_NN/_prompt.md, render "
          "its sketch (render_html.py), then run build_review.py again.")
    print(f"Next: py -3 \"{Path(__file__).resolve()}\" --out \"{out_dir}\" --open")
    return 8


def _open_page(path: Path) -> str:
    """Open a page in the user's browser; never fail the build over it.
    SLIDE_LAB_NO_OPEN=1 (set by the tests) prints the path instead.

    Returns how it was shown: "browser", "test" (SLIDE_LAB_NO_OPEN: the test
    suites stand in for the browser), or "" when it could not be opened (then
    a chat approval is refused: the user may not have seen the page)."""
    import os
    if os.environ.get("SLIDE_LAB_NO_OPEN"):
        print(f"     (not opened: SLIDE_LAB_NO_OPEN) {path}")
        return "test"
    try:
        if os.name == "nt":
            os.startfile(str(path))  # noqa: S606 (local file the build just wrote)
        else:
            import webbrowser
            webbrowser.open(path.resolve().as_uri())
        print(f"     opened in your browser: {path}")
        return "browser"
    except Exception as exc:
        print(f"     (could not open it automatically: {type(exc).__name__}; open {path})")
        return ""


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
