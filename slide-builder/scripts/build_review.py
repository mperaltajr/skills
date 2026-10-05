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
        out["slides"].append({"n": num, "title": f"Slide {num} — {title}", "gov": gov, "bullets": bullets})
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
    _h = __import__("hashlib").md5()
    for f in sorted(src_dir.glob("option_*")):
        if f.is_file() and f.suffix in (".py", ".html"):
            st_ = f.stat()
            _h.update(f"{f.name}:{st_.st_size}:{int(st_.st_mtime)}".encode())
    slide_stamp = _h.hexdigest()[:10]
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
        if qc_path.exists():
            try:
                qc_data = json.loads(qc_path.read_text(encoding="utf-8"))
                qc_summary = qc_data.get("summary")
                for c in qc_data.get("checks", []):
                    if not c.get("pass"):
                        qc_failed_checks.append(f"{c.get('check')} [{c.get('severity')}]: {c.get('detail', '')}")
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
                    if "CRITICAL" in code or code in ("EDITABILITY_VIOLATION", "TRANSLATOR_BLOCKED"):
                        sev = "Critical"
                    elif "MAJOR" in code or "MISMATCH" in code or "BELOW_MAJOR" in code:
                        sev = "Major"
                    else:
                        sev = "Advisory"
                    translation_warnings.append({"code": w.get("code", ""), "detail": detail, "severity": sev})
            except Exception:
                # Malformed report is non-blocking; just don't surface it.
                pass

        options.append({
            "letter": letter,
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
        "stamp": slide_stamp,
        "pinned": (slide_meta or {}).get("pinned_source_page") or "",
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
    topic = html.escape(storyline.get("topic") or "Slide Lab deck")
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
# QC banner stub (humanizer + render trimmed)
# ---------------------------------------------------------------------------

def render_qc_banner(out_dir: Path) -> str:
    qc_path = _p.brief_qc_json(out_dir)
    if not qc_path.exists():
        # Nothing writes brief_qc.json any more (the storyline gate replaced it),
        # so the old "not found" box showed on every review page as noise.
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
    ("layout",     "Layout / structure",       "Spacing, hierarchy, layout choice — what to nudge?"),
    ("content",    "Content / data accuracy",  "Wrong number, missing nuance, wording issue — what to fix?"),
    ("visual",     "Visual polish",            "Colors, alignment, type — anything off?"),
    ("other",      "Other notes",              "Anything else worth capturing for the regen?"),
]

# One-click feedback so the reviewer doesn't have to type the common notes.
# A clicked chip is stored in the same feedback store (a synthetic "quick"
# field), so it flows into the copied compile command with no extra plumbing.
QUICK_FEEDBACK = [
    "Too sparse — add detail",
    "Too dense — simplify",
    "Content overlaps / cut off",
    "Wrong layout / structure",
    "Change the accent color",
    "Title too long — reword",
    "Fix a number / wording",
    "More visual, less text",
    "Add process structure — numbers, icons",
]

# What a chip asks the designer to do, spelled out in the copied feedback. The
# label stays short on the page; the worker gets an instruction it can act on.
# Pages rarely numbered their steps or used shape markers unless told to in
# words every time, so that chip carries the full direction.
QUICK_FEEDBACK_EXPANDED = {
    "Add process structure — numbers, icons": (
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
        qc_badge = f'<div class="qc-badge block" title="{html.escape(tooltip)}">BLOCK</div>'
    elif n_warn > 0:
        tooltip = " | ".join(qc_failed[:6]) or f"{n_warn} warning(s)"
        qc_badge = f'<div class="qc-badge warn" title="{html.escape(tooltip)}">~ {n_warn}</div>'
    else:
        qc_badge = '<div class="qc-badge ok" title="all QC checks passed">OK QC</div>'

    # classification badge — bottom-right of frame
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

    # pattern label under the option-meta line
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
        f'title="Discard these options and design new ones for this slide">'
        '&#8635; REPLACE THESE</button>'
        # Leaving a slide out is the user's call, recorded with their picks.
        # It replaced compile --drop, which let a slide be dropped with no
        # approval at all, down to an empty deck reported as deliverable.
        f'<button class="pick leave" data-letter="-" '
        f'onclick="pickOption(\'{sid}\', \'-\')" '
        f'title="Leave this slide out of the deck">LEAVE OUT</button>'
    )
    more_picker = ""
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
      <div class="card-num">SLIDE {n}</div>
      <div class="card-name">{title}</div>
    </div>
    <div class="status-badge pending" id="badge-{sid}">PENDING</div>
  </div>

  {adjacency_banner}
  {context_chip}
  {('<div class="redo-note" style="display:block;">&#128204; <strong>Option A reproduces the page you supplied</strong> (' + html.escape(slide["pinned"]) + '). Its figures are checked against the brief before anything compiles.</div>') if slide.get("pinned") else ""}

  <div class="card-body">
  <div class="options-row" data-count="{n_opts}"{row_style}>
    {option_tiles}
  </div>

  {render_sketch_qc_section(slide)}

  <div class="card-controls">
    <div>
      <div class="field-label">Decision</div>
      <div class="decision-buttons">
        {pick_buttons}
        {none_btn}
      </div>
      <div class="hint-text">Pick an option, or Replace these to get new designs for this slide.</div>
      {more_picker}

      <div class="redo-note" id="regen-{sid}" style="display:none;">
        &#8635; Marked to replace. Say what you want different in the notes below; it goes
        with the request when you click <strong>&#10003; Build my deck</strong>.
      </div>
    </div>

    <div>
      <div class="quick-fb">
        <div class="field-label">Quick feedback</div>
        <div class="hint-text">Click any that apply — no typing needed.</div>
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
  --accent: #A100FF;      /* Accenture purple — UNCHANGED */
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
const FB_KEY    = "slidelab_feedback_v2" + PICK_NS;
const REGEN_KEY = "slidelab_regen_v3"    + PICK_NS;
const STAMPS = window.__STAMPS__ || {};

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

function loadJson(key) { try { return JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) { return {}; } }
function saveJson(key, obj) { localStorage.setItem(key, JSON.stringify(obj)); }
function loadPicks()  { return loadJson(PICKS_KEY); }
function savePicks(p) { saveJson(PICKS_KEY, p); }
function loadRegens() { return loadJson(REGEN_KEY); }
function saveRegens(r){ saveJson(REGEN_KEY, r); }
function loadFb()     { return loadJson(FB_KEY); }
function saveFb(f)    { saveJson(FB_KEY, f); }

function pickForSlide(sid) {
    // A pick counts only while the slide still has the options it was made on.
    // A rebuilt slide gets a new stamp, so its old pick falls away and the
    // reviewer has to look at the new design; every other slide keeps its pick.
    const v = loadPicks()[sid];
    if (!v || typeof v !== "object") return null;
    return (v.s === STAMPS[sid] && v.l) ? v.l : null;
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
        const btn = card.querySelector(".decision-buttons button.none");
        if (btn) btn.classList.add("active");
    }

    const badge = document.getElementById("badge-" + sid);
    badge.classList.remove("pending", "picked", "none");
    if (letter) { badge.classList.add("picked"); badge.textContent = letter === "-" ? "LEFT OUT" : "DECIDED " + letter; }
    else if (isNone) { badge.classList.add("none"); badge.textContent = "REPLACE REQUESTED"; }
    else { badge.classList.add("pending"); badge.textContent = "PENDING"; }

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

function renderAll() {
    SLIDE_IDS.forEach(renderSlideState);
    const fb = loadFb();
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        const k = ta.dataset.slide + "_" + ta.dataset.field;
        if (fb[k]) ta.value = fb[k];
    });
    // restore quick-feedback chip selections
    document.querySelectorAll(".chip[data-slide][data-chip]").forEach(chip => {
        const sel = (fb[chip.dataset.slide + "_quick"] || "").split("; ");
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
    if (pickForSlide(sid) === letter) delete picks[sid];   // clicking the pick again clears it
    else picks[sid] = { l: letter, s: STAMPS[sid] };
    savePicks(picks);
    const regens = loadRegens();
    if (regens[sid]) { delete regens[sid]; saveRegens(regens); }
    renderSlideState(sid); updateCounts();
}

function pickNone(sid) {
    const regens = loadRegens();
    if (isReplace(sid)) { delete regens[sid]; }
    else {
        regens[sid] = STAMPS[sid];
        const picks = loadPicks();
        delete picks[sid];
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

// Quick-feedback chips: a clicked chip is stored in the same feedback store
// under a synthetic "quick" field, so it rides into the compile command like
// any typed note. Multiple chips on one slide are joined with "; ".
function toggleChip(btn) {
    btn.classList.toggle("selected");
    const sid = btn.dataset.slide;
    const card = document.getElementById("card-" + sid);
    const selected = Array.from(card.querySelectorAll(".chip.selected"))
        .map(c => c.dataset.chip);
    const fb = loadFb();
    const k = sid + "_quick";
    if (selected.length) fb[k] = selected.join("; "); else delete fb[k];
    saveFb(fb);
}

function feedbackText() {
    const fb = loadFb();
    const bySlide = {};
    Object.keys(fb).forEach(k => {
        const m = k.match(/^(slide_\d+)_(.+)$/);
        if (m && fb[k] && fb[k].trim()) {
            if (!bySlide[m[1]]) bySlide[m[1]] = {};
            bySlide[m[1]][m[2]] = fb[k];
        }
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

function recordCommand(body) {
    return "  py -3 \"" + window.__SCRIPTS_DIR__ + "\\record_picks.py\" --out \"" +
        window.__OUT_DIR__ + "\" --approved \"PICKS " + body + " CHECK " +
        approvalCheck(body) + "\"\n";
}

async function copyOut(cmd, label, heading) {
    try { await navigator.clipboard.writeText(cmd); showToast(label); }
    catch (e) { showDialog(cmd, heading); }
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
        let cmd = "Update my slide-lab deck, then rebuild REVIEW.html so I can review again.\n";
        cmd += "Out dir: " + window.__OUT_DIR__ + "\n";
        cmd += "Replace the options on these slides with new designs " +
               "(build_deck.py --slide N moves the old ones aside): " + replace.join(", ") + "\n";
        if (Object.keys(picks).length) cmd += "Keep these picks: " + canonicalPicks(picks) + "\n";
        cmd += feedbackText();
        return copyOut(cmd, "Update command copied. Paste into Claude Code.",
                       "Update command (Ctrl+C to copy)");
    }

    // Every slide picked: record exactly these picks, check-coded, then convert
    // only the picked sketches and show the finished slides for a final look.
    const body = canonicalPicks(picks);
    let cmd = "Build my slide-lab deck from these picks.\n";
    cmd += "Out dir: " + window.__OUT_DIR__ + "\n";
    cmd += "Record them exactly as written (do not retype them):\n" + recordCommand(body);
    cmd += "Then follow the steps it prints, and show me FINAL-CHECK.html before compiling.\n";
    cmd += feedbackText();
    return copyOut(cmd, "Build command copied. Paste into Claude Code.",
                   "Build command (Ctrl+C to copy)");
}

async function buildAllOptions() {
    // Every option converted and stacked in one deck, for side-by-side
    // comparison. Converting is the expensive step, so say what it costs first.
    let nOpts = 0;
    SLIDE_IDS.forEach(sid => { nOpts += Object.keys(SLIDE_MAP[sid] || {}).length; });
    const nSlides = SLIDE_IDS.length;
    const ratio = nSlides ? (nOpts / nSlides).toFixed(1) : "1";
    const msg = "All options in one deck converts EVERY option: " + nOpts +
        " of them, against " + nSlides + " for a normal build of your picks " +
        "(about " + ratio + "x the conversion cost).\n\n" +
        "Use it only when you need to compare every design side by side.\n\nContinue?";
    if (!confirm(msg)) return;
    let cmd = "Build ALL options in one slide-lab deck (every option, labeled).\n";
    cmd += "Out dir: " + window.__OUT_DIR__ + "\n";
    cmd += "Record the approval exactly as written:\n" + recordCommand("ALL");
    cmd += "Then follow the steps it prints, and show me FINAL-CHECK.html before compiling.\n";
    cmd += feedbackText();
    return copyOut(cmd, "All-options command copied. Paste into Claude Code.",
                   "All-options command (Ctrl+C to copy)");
}

function clearAll() {
    if (!confirm("Clear all picks, replace requests, and feedback?")) return;
    savePicks({}); saveRegens({}); saveFb({});
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

    storyline_html = render_storyline_html(storyline, slides)
    qc_html = render_qc_banner(out_dir)
    font_html = render_font_banner(out_dir)
    preview_html = render_preview_banner(slides)
    cards_html = "\n".join(render_card(s, adjacency_warnings) for s in slides)

    topbar_html = f"""
<div class="topbar">
  <div>
    <div class="title">{html.escape(deck_topic)} &middot; OPTIONS REVIEW &middot; {slide_count} slides</div>
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
    <button class="btn ghost small" id="btn-clear">&#x1F5D1; Clear</button>
    <button class="btn ghost small" id="btn-all" title="Converts every option, not just your picks: several times the tokens. Use sparingly.">All options in one deck &#9888;</button>
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
    js_setup = (
        f"window.__TOTAL_SLIDES__ = {len(slides)};\n"
        f"window.__SLIDE_IDS__ = {json.dumps(slide_ids)};\n"
        f"window.__QUICK_EXPANDED__ = {json.dumps(QUICK_FEEDBACK_EXPANDED, ensure_ascii=False)};\n"
        f"window.__SLIDE_MAP__ = {json.dumps(slide_map)};\n"
        f"window.__STAMPS__ = {json.dumps({s['slide_id']: s.get('stamp', '') for s in slides})};\n"
        f"window.__OUT_DIR__ = {json.dumps(str(out_dir.resolve()))};\n"
        f"window.__SCRIPTS_DIR__ = {json.dumps(str(Path(__file__).resolve().parent))};\n"
        f"window.__REVIEW_TOKEN__ = {json.dumps(review_token)};\n"
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
    ok, why = _state.check_options_finalized(state, keys)
    if not ok:
        problems.append(why)
    for k, L in ship:
        for name in (_p.option_pptx_name(L), _p.option_png_name(L)):
            if not (out_dir / k / name).exists():
                problems.append(f"{k}/{name} is missing")
    if problems:
        print("NOT READY for the final check:", file=sys.stderr)
        for p in problems[:12]:
            print(f"  - {p}", file=sys.stderr)
        print("Translate any picked sketches, run finalize_deck.py, then try again.",
              file=sys.stderr)
        return 5

    digests = {key: _state.file_digest(out_dir / k / _p.option_pptx_name(L))
               for key, (k, L) in zip(keys, ship)}
    token = _state.record_final_check(out_dir, digests)

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
    what = (f"all {len(ship)} options" if all_options
            else f"{len(ship)} slide(s)")
    # Numbers and labels on the picks that the brief does not contain, and
    # figures written two ways: the person approving sees what to verify.
    try:
        import source_check
        src_block = source_check.html_block(source_check.check(
            out_dir, [(k, out_dir / k / _p.option_pptx_name(L)) for k, L in ship]))
    except Exception:
        src_block = ""
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Final check</title><style>{FINAL_CSS}</style></head><body>
<header><h1>Final check: this is exactly what will be built</h1>
<p>Every pick below is finished and on your template ({what}): the real title,
takeaway and page number, which the sketches did not have. Look for anything
overlapping, cut off or crowded. If it is right, click <b>Build it</b>. If not,
say what is wrong in the box instead.</p></header>
{src_block}
<div class="grid">{tiles}</div>
<footer>
<textarea id="fix" placeholder="Something needs fixing? Say which slide and what."></textarea>
<button class="fix" id="btn-fix">Send fixes</button>
<button class="go" id="btn-go">&#10003; Build it</button>
</footer><div id="toast"></div>
<script>
const OUT = {json.dumps(str(out_dir))};
const CMD = {json.dumps(compile_cmd)};
function toast(m) {{ const t = document.getElementById("toast"); t.textContent = m;
  t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1800); }}
async function copy(text, label) {{
  try {{ await navigator.clipboard.writeText(text); toast(label); }}
  catch (e) {{ prompt("Copy this:", text); }} }}
document.getElementById("btn-go").onclick = () => copy(
  "Compile my slide-lab deck. I checked the finished slides.\\nOut dir: " + OUT +
  "\\n  " + CMD + "\\nThen run slide-qc on the deck and check_done.py before telling me it is done.\\n",
  "Build command copied. Paste into Claude Code.");
document.getElementById("btn-fix").onclick = () => {{
  const t = document.getElementById("fix").value.trim();
  if (!t) {{ toast("Say what needs fixing first."); return; }}
  copy("Fix my slide-lab deck before building it.\\nOut dir: " + OUT +
       "\\nWhat is wrong: " + t + "\\nRebuild the affected slide(s) through the pipeline, " +
       "then show me a new FINAL-CHECK.html.\\n", "Fix request copied. Paste into Claude Code.");
}};
</script></body></html>"""
    dest = out_dir / "FINAL-CHECK.html"
    dest.write_text(page, encoding="utf-8")
    print(f"FINAL-CHECK.html written: {dest}")
    print(f"  {len(ship)} finished option(s). Show it to the user and wait for the "
          "Build command it copies; that command is the only way to compile.")
    return 0


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
        return build_final_check(out_dir, meta)

    slides = [scan_slide(out_dir, n, slide_metas.get(n)) for n in slide_nums]
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
    print(f"     storyline parsed from brief: {storyline.get('found')}")
    print(f"     size: {fmt_bytes(review_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
