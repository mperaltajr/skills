"""build_review.py — v2 fork

===============================

Generate a self-contained REVIEW.html for a v2 slide-builder
orchestrator output dir.

Fork from slide-builder/scripts/build_review.py with surgical v2 additions:
  - sys.path tweak for twins/ from slide-builder/
  - extract_option_pattern() reads each option_X.py's line-1 / line-2 to
    capture the picked pattern + classification (native/fallback/rejected)
  - compute_adjacency_warnings() scans option_A across all slides; any
    3+ consecutive same-pattern run produces a per-slide advisory list
  - render_card() injects an adjacency banner when warnings exist
  - CSS adds a .adjacency-banner style

Everything else is verbatim from v1.

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

# Path setup. twins/ is local to this skill (re-homed Phase 2 cleanup
# 2026-05-26); render_slides lives in the sibling slide-qc skill. This
# script does not actually import from either today; the paths are
# kept on sys.path defensively in case future helpers are added.
SKILL_ROOT = Path(__file__).resolve().parents[1]
QC_SCRIPTS = SKILL_ROOT.parent / "slide-qc" / "scripts"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(QC_SCRIPTS))

import _paths as _p  # noqa: E402


# ---------------------------------------------------------------------------
# IO helpers — verbatim from v1
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
# v2 ADDITION — pattern extraction + adjacency detection
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
# Brief parser — verbatim from v1
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
        out["slides"].append({"n": num, "title": f"Slide {num} — {title}", "gov": gov, "bullets": bullets})
    return out


def _md_inline_to_html(s: str) -> str:
    s_esc = html.escape(s)
    s_esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s_esc)
    s_esc = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s_esc)
    return s_esc


# ---------------------------------------------------------------------------
# Per-slide _prompt.md parser — verbatim from v1
# ---------------------------------------------------------------------------

# page_type was previously regexed out of _prompt.md via
# `**Page type (heuristic):**` — that line was a v1 prep-pass echo and is
# never written by v2's build_deck.py. The canonical source for page_type is
# _meta.json (slides[].page_type). parse_prompt() no longer attempts to read
# it; the lookup is on _meta.json only. See P4.28 resolution (2026-05-26).
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
# Slide scan — v1 base + v2 pattern capture per option
# ---------------------------------------------------------------------------

OPTIONS = ("A", "B", "C")


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

    # page_type now comes only from _meta.json (canonical). See P4.28 resolution.
    page_type = (slide_meta or {}).get("page_type") or ""
    if page_type:
        page_type = page_type.split("\n")[0].strip()

    options = []
    for letter in OPTIONS:
        png = themed_dir / _p.option_png_name(letter)
        themed_pptx = themed_dir / _p.option_pptx_name(letter)
        src_pptx = src_dir / _p.option_pptx_name(letter)
        src_py = src_dir / _p.option_py_name(letter)
        themed_exists = themed_pptx.exists()
        qc_path = themed_dir / _p.option_qc_json_name(letter)
        qc_summary = None
        qc_failed_checks: list = []
        if qc_path.exists():
            try:
                qc_data = json.loads(qc_path.read_text(encoding="utf-8"))
                qc_summary = qc_data.get("summary")
                for c in qc_data.get("checks", []):
                    if not c.get("pass"):
                        qc_failed_checks.append(f"{c.get('check')} [{c.get('severity')}]: {c.get('detail', '')}")
            except Exception:
                qc_summary = None

        # v2 addition: extract pattern + classification from the .py header
        pattern, classification = extract_option_pattern(src_py)

        options.append({
            "letter": letter,
            "png": png,
            "png_exists": png.exists(),
            "themed_pptx": themed_pptx,
            "themed_exists": themed_exists,
            "src_pptx": src_pptx,
            "src_exists": src_pptx.exists(),
            "themed_size": themed_pptx.stat().st_size if themed_exists else 0,
            "qc_summary": qc_summary,
            "qc_failed_checks": qc_failed_checks,
            # v2 fields
            "pattern": pattern,
            "classification": classification,
        })

    # Gap 3 (2026-06-08): worker context-ack telemetry. When build_deck.py
    # has written `_context.md` and the worker has followed the soft-
    # enforcement protocol, it leaves `_context_ack.txt` next to it with a
    # one-line citation of the constraint that informed its pattern pick.
    # Surface absence as an advisory chip — non-blocking; the user decides
    # whether to re-dispatch.
    #
    # Audit blocker (2026-06-08): when the template was registered WITHOUT
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
# Storyline rendering — verbatim from v1
# ---------------------------------------------------------------------------

def render_storyline_html(storyline: dict, slides: list) -> str:
    brief_slides = storyline.get("slides") or []
    by_num = {s["n"]: s for s in brief_slides}

    def _slide_block(slide: dict) -> str:
        n = slide["n"]
        brief_s = by_num.get(n)
        title = (brief_s or {}).get("title") or f"Slide {n} — {slide.get('title') or ''}".strip(" —")
        gov = (brief_s or {}).get("gov") or slide.get("governing") or ""
        bullets = (brief_s or {}).get("bullets") or slide.get("bullets") or []
        parts = [f'<div class="dd-slide-title">{html.escape(title)}</div>']
        if gov and not (gov.startswith("[") and gov.endswith("]")):
            parts.append(f'<div class="dd-gov">{html.escape(gov)}</div>')
        elif gov:
            parts.append(f'<div class="dd-gov missing">{html.escape(gov)}</div>')
        else:
            parts.append('<div class="dd-gov missing">(no governing thought in brief)</div>')
        if bullets:
            items = "".join(f"<li>{b}</li>" for b in bullets)
            parts.append(f'<ul class="dd-bullets">{items}</ul>')
        return f'<div class="dd-slide">{"".join(parts)}</div>'

    blocks = "".join(_slide_block(s) for s in slides)
    topic = html.escape(storyline.get("topic") or "Slide Lab v2 deck")
    deck_type = html.escape(storyline.get("deck_type") or "—")
    gov = html.escape(storyline.get("governing") or "—")
    audience = html.escape(storyline.get("audience") or "—")
    bbreak = html.escape(storyline.get("belief_break") or "—")
    bleave = html.escape(storyline.get("belief_leave") or "—")
    sback = html.escape(storyline.get("say_back") or "—")
    return f"""
<details class="storyline-section">
<summary><span class="storyline-summary-text">▶ Storyline (dot-dash) — click to expand</span></summary>
<div class="storyline-body">
  <div class="dd-container">
    <h1 class="dd-title">Dot-dash storyline: {topic}</h1>
    <div class="dd-deck-meta">
      <div class="lbl">Deck type</div><div class="val">{deck_type}</div>
      <div class="lbl">Governing thought</div><div class="val gov">{gov}</div>
      <div class="lbl">Audience</div><div class="val">{audience}</div>
      <div class="lbl">Belief to break</div><div class="val">{bbreak}</div>
      <div class="lbl">Belief to leave with</div><div class="val">{bleave}</div>
      <div class="lbl">Room should say back</div><div class="val">{sback}</div>
    </div>
    <div class="dd-callout">Read the dots top-to-bottom — they should form the deck's argument as a single coherent story.</div>
    {blocks}
  </div>
</div>
</details>
"""


# ---------------------------------------------------------------------------
# QC banner stub — verbatim from v1 (humanizer + render trimmed for v2)
# ---------------------------------------------------------------------------

def _render_qc_info_stub() -> str:
    return (
        '<div class="qc-brief-banner">'
        '<div class="qc-brief-banner-title">Brief-time QC report</div>'
        '<details class="qc-brief-section qc-brief-info">'
        '<summary><span class="qc-brief-icon">i</span>INFO &middot; brief_qc.json not found</summary>'
        '<ul><li>No <code>brief_qc.json</code> in this output directory. '
        'v2\'s build_deck.py does not yet produce one — wire later if needed.</li></ul>'
        '</details></div>'
    )


def render_qc_banner(out_dir: Path) -> str:
    qc_path = _p.brief_qc_json(out_dir)
    if not qc_path.exists():
        return _render_qc_info_stub()
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
# Per-slide card — v1 base + v2 adjacency banner + classification badge
# ---------------------------------------------------------------------------

FEEDBACK_FIELDS = [
    ("headline",   "Headline / title",         "Anything to change about the action title?"),
    ("layout",     "Layout / structure",       "Spacing, hierarchy, layout choice — what to nudge?"),
    ("content",    "Content / data accuracy",  "Wrong number, missing nuance, wording issue — what to fix?"),
    ("visual",     "Visual polish",            "Colors, alignment, type — anything off?"),
    ("other",      "Other notes",              "Anything else worth capturing for the regen?"),
]


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
        qc_badge = f'<div class="qc-badge block" title="{html.escape(tooltip)}">BLOCK</div>'
    elif n_warn > 0:
        tooltip = " | ".join(qc_failed[:6]) or f"{n_warn} warning(s)"
        qc_badge = f'<div class="qc-badge warn" title="{html.escape(tooltip)}">~ {n_warn}</div>'
    else:
        qc_badge = '<div class="qc-badge ok" title="all QC checks passed">OK QC</div>'

    # v2 addition: classification badge — bottom-right of frame
    classification = opt.get("classification", "native")
    class_badge_html = ""
    if classification == "fallback_mermaid":
        class_badge_html = '<div class="class-badge fallback" title="Mermaid fallback render">MERMAID</div>'
    elif classification == "skeleton_rejected":
        class_badge_html = '<div class="class-badge rejected" title="SKELETON_REJECTED — no PPTX produced">REJECTED</div>'

    vqc_btn = (
        f'<button class="vision-qc-btn" '
        f'onclick="copyVisionQcPrompt(this, \'{html.escape(themed_path_str)}\')" '
        f'title="Copy a paste-ready Claude prompt to run slide-qc vision review">'
        f'Vision QC &rarr;</button>'
        if themed_path_str else ''
    )

    # v2 addition: pattern label under the option-meta line
    pattern = opt.get("pattern")
    pattern_html = (
        f'<div class="option-pattern">{html.escape(pattern)}</div>'
        if pattern else ""
    )

    return f"""
<div class="option" data-slide="{sid}" data-letter="{letter}" data-pptx="{html.escape(themed_path_str)}">
  <div class="option-frame">{thumb}{qc_badge}{class_badge_html}</div>
  <div class="option-meta">
    <span class="option-letter">Option {letter}</span>
    <div class="option-taxon">{html.escape(page_type)}</div>
    {pattern_html}
    {vqc_btn}
  </div>
</div>
"""


def render_adjacency_banner(slide_n: int, warnings: list[str]) -> str:
    """v2 ADDITION: render the adjacency advisory banner on a slide's card."""
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
    """Gap 3 (2026-06-08): per-slide worker context-ack telemetry chip.

    Shows one of three states next to the slide title:
      - green: worker wrote `_context_ack.txt` with a citation; show the
        first line so the user can see what the worker reasoned against.
      - yellow: `_context.md` was generated AND a reference slide was
        registered, but the worker didn't write an ack file. Advisory.
      - hidden: no `_context.md` (older brief) OR `_context.md` exists but
        the template was registered without a reference slide — the chip
        would be noise on every slide if shown here, so suppress (audit
        blocker, 2026-06-08).
    """
    if not slide.get("context_present"):
        return ""
    # Suppress the chip when no reference slide was registered — there's no
    # canonical constraint for the worker to have cited, so a yellow ⚠ on
    # every slide of every build is pure noise that Mario asked us not to
    # ship.
    if not slide.get("context_has_reference"):
        return ""
    if slide.get("context_ack_present"):
        cite = html.escape(slide.get("context_ack_text") or "(empty citation)")
        return (
            '<div class="context-chip context-chip-ok">'
            '<span class="context-chip-icon">&#10003;</span> '
            f'<strong>Worker used your reference slide.</strong> {cite}'
            '</div>'
        )
    return (
        '<div class="context-chip context-chip-warn">'
        '<span class="context-chip-icon">&#9888;</span> '
        '<strong>Worker may not have used your reference slide.</strong> '
        'Output could drift from your canonical example. Spot-check the slide '
        'in PowerPoint; if it looks off-brand, re-dispatch this slide.'
        '</div>'
    )


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
    none_btn = (
        f'<button class="none" onclick="pickNone(\'{sid}\')">'
        '&#10007; NONE &mdash; TRY AGAIN</button>'
    )
    feedback_html = "".join(
        f'<div class="feedback-field">'
        f'<label for="fb-{sid}-{key}">{label}</label>'
        f'<textarea id="fb-{sid}-{key}" data-slide="{sid}" data-field="{key}" '
        f'placeholder="{html.escape(placeholder)}"></textarea>'
        f'</div>'
        for (key, label, placeholder) in FEEDBACK_FIELDS
    )
    prompt_uri = file_uri(slide["prompt_path"]) if slide["prompt_path"].exists() else ""
    regen_text = (
        f"Re-dispatch slide {n} ({slide.get('title')}) with stronger visual treatment.\n"
        f"Original prompt: {str(slide['prompt_path'].resolve())}\n"
        f"None of options A/B/C landed. Pick a different pattern this time."
    )

    return f"""
<div class="card" id="card-{sid}" data-slide="{sid}">
  <div class="card-header-row">
    <div style="flex:1;">
      <div class="card-num">SLIDE {n}</div>
      <div class="card-name">{title}</div>
    </div>
    <div class="status-badge pending" id="badge-{sid}">PENDING</div>
  </div>

  {adjacency_banner}
  {context_chip}

  <div class="options-row">
    {option_tiles}
  </div>

  <div class="card-controls">
    <div>
      <div class="field-label">Decision</div>
      <div class="decision-buttons">
        {pick_buttons}
        {none_btn}
      </div>
      <div class="hint-text">Pick one option, or click NONE to mark for regeneration.</div>

      <div class="regen-panel" id="regen-{sid}" style="display:none;">
        <div class="field-label" style="margin-top:14px;">Regen instruction (copy-paste into new session)</div>
        <textarea readonly class="regen-text" rows="5">{html.escape(regen_text)}</textarea>
        <div style="margin-top:6px;">
          <button class="btn ghost small" onclick="copyRegen('{sid}')">Copy regen text</button>
          {f'<a class="open-prompt" href="{html.escape(prompt_uri)}" target="_blank" rel="noopener">Open _prompt.md</a>' if prompt_uri else ''}
        </div>
      </div>
    </div>

    <div>
      <div class="field-label">Section-level feedback</div>
      <div class="hint-text">Leave feedback on any section. Skip what doesn't apply.</div>
      <div class="feedback-grid">
        {feedback_html}
      </div>
    </div>
  </div>
</div>
"""


# ---------------------------------------------------------------------------
# CSS — v1 base + v2 adjacency-banner + classification-badge + pattern-label
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg: #0F172A;
  --panel: #1E293B;
  --panel-2: #273448;
  --text: #E2E8F0;
  --text-dim: #94A3B8;
  --accent: #A100FF;
  --accent-soft: #C780FF;
  --approve: #16A34A;
  --tweak: #CA8A04;
  --reject: #DC2626;
  --info: #2563EB;
  --pending: #64748B;
  --border: #334155;
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

/* Gap 3 (2026-06-08): worker context-ack chip */
.context-chip { margin: 0 20px 10px; padding: 8px 12px; border-radius: 4px; font-size: 12px; line-height: 1.4; }
.context-chip-icon { margin-right: 6px; font-weight: 700; }
.context-chip-ok { background: rgba(16,185,129,0.12); border-left: 3px solid #10B981; color: #6EE7B7; }
.context-chip-ok strong { color: #10B981; }
.context-chip-warn { background: rgba(202,138,4,0.14); border-left: 3px solid var(--tweak); color: #FDE68A; }
.context-chip-warn strong { color: var(--tweak); }

/* v2 addition: adjacency advisory banner */
.adjacency-banner { margin: 0 20px 12px; padding: 10px 14px; background: rgba(202,138,4,0.14); border-left: 4px solid var(--tweak); border-radius: 4px; color: #FDE68A; font-size: 13px; line-height: 1.45; }
.adjacency-banner-title { font-size: 11px; font-weight: 800; color: var(--tweak); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.adjacency-icon { color: var(--tweak); margin-right: 4px; }
.adjacency-banner ul { margin: 4px 0 0; padding-left: 18px; }
.adjacency-banner li { padding: 2px 0; }

/* v2 addition: classification badge on option frame */
.class-badge { position: absolute; bottom: 6px; right: 6px; padding: 3px 8px; border-radius: 10px; font-size: 9px; font-weight: 800; letter-spacing: 0.6px; line-height: 1.1; z-index: 2; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: help; }
.class-badge.fallback { background: var(--info); color: #fff; }
.class-badge.rejected { background: var(--reject); color: #fff; }

/* v2 addition: pattern label under option meta */
.option-pattern { color: var(--accent-soft); margin-top: 2px; font-size: 11px; font-weight: 600; font-style: italic; }

.font-banner { background: #FEF3C7; border-bottom: 2px solid #F59E0B; padding: 14px 24px; color: #78350F; }
.font-banner-title { font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.font-banner-icon { color: #D97706; margin-right: 6px; }
.font-banner-body { font-size: 13px; line-height: 1.5; }

.vision-qc-btn { display: inline-block; margin-left: auto; padding: 3px 10px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid var(--border); background: var(--panel); color: var(--text-dim); border-radius: 3px; cursor: pointer; transition: all 0.15s; }
.vision-qc-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
.vision-qc-btn.copied { background: #16A34A; color: white; border-color: #16A34A; }

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

.options-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 14px 20px; }
.option { background: var(--panel-2); border: 2px solid transparent; border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform 0.12s, box-shadow 0.12s, border-color 0.12s; }
.option:hover { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(0,0,0,0.35); border-color: var(--accent); }
.option.picked { border-color: var(--approve); background: rgba(22,163,74,0.10); }
.option-frame { background: #fff; width: 100%; aspect-ratio: 16/9; overflow: hidden; position: relative; }
.option-frame .thumb { width: 100%; height: 100%; }
.option-frame .thumb img { width: 100%; height: 100%; object-fit: contain; display: block; background: #fff; }
.option-frame .thumb.missing { display: flex; align-items: center; justify-content: center; background: rgba(220,38,38,0.18); color: #FCA5A5; font-size: 11px; font-weight: 600; }
.option-meta { padding: 8px 10px 10px; font-size: 11px; }
.option-letter { font-size: 11px; font-weight: 800; color: var(--accent); text-transform: uppercase; }
.option-taxon { color: var(--text-dim); margin-top: 2px; font-size: 11px; }
.qc-badge { position: absolute; top: 6px; right: 6px; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: 800; letter-spacing: 0.5px; line-height: 1.1; z-index: 2; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: help; }
.qc-badge.ok    { background: var(--approve); color: #fff; }
.qc-badge.warn  { background: var(--tweak);   color: #fff; }
.qc-badge.block { background: var(--reject);  color: #fff; }

.card-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 14px 20px 18px; border-top: 1px solid var(--border); }
.decision-buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.decision-buttons button { padding: 11px 6px; font-size: 11px; font-weight: 700; border-radius: 5px; border: 2px solid transparent; background: var(--panel-2); color: var(--text-dim); cursor: pointer; transition: all 0.15s; font-family: inherit; }
.decision-buttons button:hover { filter: brightness(1.18); border-color: var(--accent); color: var(--accent); }
.decision-buttons button.none:hover { border-color: var(--reject); color: var(--reject); }
.decision-buttons button.active.pick { background: var(--approve); color: white; border-color: var(--approve); }
.decision-buttons button.active.none { background: var(--reject); color: white; border-color: var(--reject); }

textarea { width: 100%; min-height: 44px; background: var(--panel-2); color: var(--text); border: 1px solid var(--border); border-radius: 5px; padding: 7px 10px; font-family: inherit; font-size: 12px; line-height: 1.4; resize: vertical; }
textarea.regen-text { background: rgba(220,38,38,0.06); border-color: rgba(220,38,38,0.35); color: #FCA5A5; min-height: 90px; font-family: Consolas, monospace; font-size: 11px; }
.field-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
.hint-text { font-size: 11px; color: var(--text-dim); margin-bottom: 10px; font-style: italic; }
.feedback-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; }
.feedback-field label { display: block; font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 4px; }
.regen-panel { margin-top: 10px; padding: 10px 12px; background: rgba(220,38,38,0.04); border-left: 3px solid var(--reject); border-radius: 4px; }

footer.summary-footer { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(15,23,42,0.96); border-top: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 14px; z-index: 50; backdrop-filter: blur(6px); }
footer.summary-footer .count { font-size: 14px; font-weight: 700; color: var(--text); }
footer.summary-footer .count .num { color: var(--accent); }
footer.summary-footer .btns { display: flex; gap: 8px; flex-wrap: wrap; }
button.btn { background: var(--accent); color: #fff; border: none; padding: 9px 14px; border-radius: 5px; font-size: 12px; font-weight: 700; font-family: inherit; cursor: pointer; transition: opacity 0.12s; }
button.btn:hover { opacity: 0.85; }
button.btn.ghost { background: transparent; border: 1px solid #475569; color: #CBD5E1; }
button.btn.primary { background: var(--accent); color: #fff; border: 1px solid var(--accent); }
button.btn.big { padding: 13px 26px; font-size: 14px; letter-spacing: 0.3px; }
button.btn.small { padding: 6px 11px; font-size: 11px; }

dialog#picks-dialog { background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 0; max-width: 720px; width: 90vw; }
dialog#picks-dialog::backdrop { background: rgba(0,0,0,0.6); }
dialog#picks-dialog .dlg-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
dialog#picks-dialog pre { margin: 0; padding: 16px 18px; background: var(--bg); color: #86EFAC; font-size: 12px; font-family: Consolas, monospace; max-height: 60vh; overflow: auto; white-space: pre-wrap; word-break: break-all; }
dialog#picks-dialog .dlg-foot { padding: 12px 18px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 8px; }

#toast { position: fixed; bottom: 88px; left: 50%; transform: translateX(-50%); background: var(--panel); border: 1px solid var(--accent); color: var(--text); padding: 9px 16px; border-radius: 5px; font-size: 12px; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 200; max-width: 80vw; }
#toast.show { opacity: 1; }
"""


# ---------------------------------------------------------------------------
# JS — verbatim from v1 (picks + feedback + clipboard logic unchanged)
# ---------------------------------------------------------------------------

JS = r"""
const PICKS_KEY = "slidelab_v2_picks_v1::" + window.location.pathname;
const FB_KEY    = "slidelab_v2_feedback_v1::" + window.location.pathname;
const REGEN_KEY = "slidelab_v2_regen_v1::"    + window.location.pathname;
const TOTAL_SLIDES = window.__TOTAL_SLIDES__;
const SLIDE_IDS = window.__SLIDE_IDS__;
const SLIDE_MAP = window.__SLIDE_MAP__;

function loadJson(key) { try { return JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) { return {}; } }
function saveJson(key, obj) { localStorage.setItem(key, JSON.stringify(obj)); }
function loadPicks()  { return loadJson(PICKS_KEY); }
function savePicks(p) { saveJson(PICKS_KEY, p); }
function loadRegens() { return loadJson(REGEN_KEY); }
function saveRegens(r){ saveJson(REGEN_KEY, r); }
function loadFb()     { return loadJson(FB_KEY); }
function saveFb(f)    { saveJson(FB_KEY, f); }

function pickForSlide(sid) {
    const picks = loadPicks();
    const map = SLIDE_MAP[sid] || {};
    for (const letter of Object.keys(map)) {
        if (picks[map[letter]] === letter) return letter;
    }
    return null;
}

function renderSlideState(sid) {
    const card = document.getElementById("card-" + sid);
    if (!card) return;
    const letter = pickForSlide(sid);
    const regens = loadRegens();
    const isNone = !!regens[sid];

    card.querySelectorAll(".option").forEach(opt => {
        opt.classList.toggle("picked", opt.dataset.letter === letter);
    });
    card.querySelectorAll(".decision-buttons button").forEach(btn => {
        btn.classList.remove("active");
    });
    if (letter) {
        const btn = card.querySelector(`.decision-buttons button.pick[data-letter="${letter}"]`);
        if (btn) btn.classList.add("active");
    } else if (isNone) {
        const btn = card.querySelector(".decision-buttons button.none");
        if (btn) btn.classList.add("active");
    }

    const badge = document.getElementById("badge-" + sid);
    badge.classList.remove("pending", "picked", "none");
    if (letter) { badge.classList.add("picked"); badge.textContent = "DECIDED " + letter; }
    else if (isNone) { badge.classList.add("none"); badge.textContent = "REGEN REQUESTED"; }
    else { badge.classList.add("pending"); badge.textContent = "PENDING"; }

    const regenPanel = document.getElementById("regen-" + sid);
    if (regenPanel) regenPanel.style.display = isNone ? "block" : "none";
}

function updateCounts() {
    let picked = 0, none = 0;
    SLIDE_IDS.forEach(sid => {
        if (pickForSlide(sid)) picked++;
        else if (loadRegens()[sid]) none++;
    });
    document.getElementById("count-picked").textContent = picked;
    document.getElementById("count-none").textContent = none;
    document.getElementById("count-pending").textContent = TOTAL_SLIDES - picked - none;
    document.getElementById("pick-count").textContent = picked;
    document.getElementById("total-slides").textContent = TOTAL_SLIDES;
}

function renderAll() {
    SLIDE_IDS.forEach(renderSlideState);
    const fb = loadFb();
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        const k = ta.dataset.slide + "_" + ta.dataset.field;
        if (fb[k]) ta.value = fb[k];
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
    const map = SLIDE_MAP[sid] || {};
    const pptx = map[letter];
    if (!pptx) { showToast("Option " + letter + " has no themed PPTX."); return; }
    const picks = loadPicks();
    for (const l of Object.keys(map)) {
        if (map[l] && picks[map[l]] === l) delete picks[map[l]];
    }
    const current = pickForSlide(sid);
    if (current !== letter) picks[pptx] = letter;
    savePicks(picks);
    const regens = loadRegens();
    if (regens[sid]) { delete regens[sid]; saveRegens(regens); }
    renderSlideState(sid); updateCounts();
}

function pickNone(sid) {
    const regens = loadRegens();
    if (regens[sid]) { delete regens[sid]; }
    else {
        regens[sid] = true;
        const map = SLIDE_MAP[sid] || {};
        const picks = loadPicks();
        for (const l of Object.keys(map)) {
            if (map[l] && picks[map[l]] === l) delete picks[map[l]];
        }
        savePicks(picks);
    }
    saveRegens(regens);
    renderSlideState(sid); updateCounts();
}

function wireFeedback() {
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        ta.addEventListener("input", () => {
            const fb = loadFb();
            const k = ta.dataset.slide + "_" + ta.dataset.field;
            if (ta.value) fb[k] = ta.value; else delete fb[k];
            saveFb(fb);
        });
    });
}

async function buildDeck() {
    const picks = {};
    SLIDE_IDS.forEach(sid => { const l = pickForSlide(sid); if (l) picks[sid] = l; });
    if (Object.keys(picks).length === 0) { showToast("No picks yet."); return; }
    const fb = loadFb();
    const fbBySlide = {};
    Object.keys(fb).forEach(k => {
        const m = k.match(/^(slide_\d+)_(.+)$/);
        if (m && fb[k] && fb[k].trim()) {
            if (!fbBySlide[m[1]]) fbBySlide[m[1]] = {};
            fbBySlide[m[1]][m[2]] = fb[k];
        }
    });
    const regens = loadRegens();
    const regenSlides = Object.keys(regens).filter(s => regens[s]);
    let cmd = "Compile my slide-lab v2 deck.\n";
    cmd += "Out dir: " + window.__OUT_DIR__ + "\n";
    cmd += "Picks: " + JSON.stringify(picks) + "\n";
    if (regenSlides.length) cmd += "Regen requested: " + regenSlides.join(", ") + "\n";
    if (Object.keys(fbBySlide).length) {
        cmd += "Feedback:\n";
        Object.keys(fbBySlide).sort().forEach(sid => {
            const f = fbBySlide[sid];
            cmd += "  " + sid + ":\n";
            Object.keys(f).forEach(k => { cmd += "    " + k + ": " + f[k].replace(/\n/g, " ") + "\n"; });
        });
    }
    try { await navigator.clipboard.writeText(cmd); showToast("Compile command copied. Paste into Claude Code."); }
    catch (e) { showDialog(cmd, "Compile command (Ctrl+C to copy)"); }
}

function clearAll() {
    if (!confirm("Clear all picks, regens, and feedback?")) return;
    savePicks({}); saveRegens({}); saveFb({});
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => ta.value = "");
    renderAll(); showToast("Cleared.");
}

async function copyRegen(sid) {
    const ta = document.querySelector("#regen-" + sid + " textarea.regen-text");
    if (!ta) return;
    try { await navigator.clipboard.writeText(ta.value); showToast("Regen text copied."); }
    catch (e) { ta.select(); document.execCommand && document.execCommand("copy"); showToast("Selected — Ctrl+C to copy."); }
}

function showDialog(text, heading) {
    const dlg = document.getElementById("picks-dialog");
    document.getElementById("picks-dlg-head").textContent = heading;
    document.getElementById("picks-dlg-body").textContent = text;
    if (typeof dlg.showModal === "function") dlg.showModal();
    else dlg.setAttribute("open", "");
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
            if (e.target.closest("a")) return;
            pickOption(el.dataset.slide, el.dataset.letter);
        });
    });
    document.getElementById("btn-build").addEventListener("click", buildDeck);
    document.getElementById("btn-clear").addEventListener("click", clearAll);
    document.getElementById("btn-dlg-copy").addEventListener("click", async () => {
        const txt = document.getElementById("picks-dlg-body").textContent;
        try { await navigator.clipboard.writeText(txt); showToast("Copied."); } catch (e) {}
    });
    document.getElementById("btn-dlg-close").addEventListener("click", () => {
        document.getElementById("picks-dialog").close();
    });
    wireFeedback(); renderAll();
});
"""


# ---------------------------------------------------------------------------
# Build HTML — v1 base + v2 adjacency-warning computation
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
            if o["themed_exists"]:
                slide_map[sid][o["letter"]] = str(o["themed_pptx"].resolve())

    # v2: compute adjacency warnings across option_A
    adjacency_warnings = compute_adjacency_warnings(slides_by_n, option_letter="A")

    deck_meta = (meta or {}).get("deck_meta", {}) or {}
    deck_type = deck_meta.get("deck_type") or storyline.get("deck_type") or "Slide Lab v2 deck"
    deck_topic = storyline.get("topic") or "Untitled v2 deck"
    governing = deck_meta.get("governing_thought") or storyline.get("governing") or ""
    generated = (meta or {}).get("generated_at") or datetime.now().isoformat(timespec="seconds")
    brief_path = (meta or {}).get("brief", "")
    template_path = (meta or {}).get("template", "")
    slide_count = (meta or {}).get("slide_count", len(slides))
    # v2: client_slug surfaces in the topbar so reviewers can tell FedEx vs ACN
    # REVIEW.html apart at a glance. Brand-specific overrides handle camel-case
    # capitalizations that plain title() gets wrong ("Fedex" vs "FedEx").
    # Add new brands here as encountered; fall back to title-case for unknowns.
    _BRAND_DISPLAY = {
        "fedex":     "FedEx",
        "accenture": "Accenture",
        "acn":       "Accenture",
        "nfl":       "NFL",
    }
    client_slug_raw = (meta or {}).get("client_slug", "") or ""
    client_display = (
        _BRAND_DISPLAY.get(client_slug_raw.lower().strip())
        or client_slug_raw.replace("-", " ").replace("_", " ").title()
        or client_slug_raw
    )

    storyline_html = render_storyline_html(storyline, slides)
    qc_html = render_qc_banner(out_dir)
    font_html = render_font_banner(out_dir)
    cards_html = "\n".join(render_card(s, adjacency_warnings) for s in slides)

    topbar_html = f"""
<div class="topbar">
  <div>
    <div class="title">{html.escape(deck_topic)} &middot; v2 OPTIONS REVIEW &middot; {slide_count} slides</div>
    <div class="title-sub">{html.escape(deck_type)} &middot; Pick A/B/C per slide or mark NONE.</div>
    <div class="topbar-meta">
      <div class="k">Generated</div><div class="v">{html.escape(generated)}</div>
      <div class="k">Brief</div><div class="v"><code>{html.escape(brief_path)}</code></div>
      <div class="k">Template</div><div class="v"><code>{html.escape(template_path)}</code></div>
      <div class="k">Output</div><div class="v"><code>{html.escape(str(out_dir.resolve()))}</code></div>
      <div class="k">Client</div><div class="v">{html.escape(client_display) if client_display else '<em style="color:#888;">(not set)</em>'}</div>
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
  <div class="count"><span class="num" id="pick-count">0</span> / <span id="total-slides">0</span> picked &middot; <span style="color:#94A3B8;font-weight:400;font-size:12px;">picks auto-save in this browser</span></div>
  <div class="btns">
    <button class="btn ghost small" id="btn-clear">&#x1F5D1; Clear</button>
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

    js_setup = (
        f"window.__TOTAL_SLIDES__ = {len(slides)};\n"
        f"window.__SLIDE_IDS__ = {json.dumps(slide_ids)};\n"
        f"window.__SLIDE_MAP__ = {json.dumps(slide_map)};\n"
        f"window.__OUT_DIR__ = {json.dumps(str(out_dir.resolve()))};\n"
    )

    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">"
        f"<title>{html.escape(deck_topic)} &mdash; v2 REVIEW</title>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<style>{CSS}</style></head><body>"
        f"{topbar_html}"
        f"{storyline_html}"
        f"{font_html}"
        f"{qc_html}"
        f"<div class=\"cards\">{cards_html}</div>"
        f"{footer_html}"
        f"<script>{js_setup}{JS}</script>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# Main — verbatim from v1
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build REVIEW.html for v2 slide-builder output.")
    ap.add_argument("--out", required=True, help="Orchestrator output directory.")
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

    slides = [scan_slide(out_dir, n, slide_metas.get(n)) for n in slide_nums]

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
    print(f"     {len(slides)} slides x 3 options = {total_opts} tiles")
    print(f"     missing PNGs: {missing_png}, missing themed PPTX: {missing_themed}")
    print(f"     storyline parsed from brief: {storyline.get('found')}")
    print(f"     size: {fmt_bytes(review_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
