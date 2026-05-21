"""
build_review.py
===============

Generate a self-contained REVIEW.html for a Slide Lab orchestrator output dir.

Replaces the minimal picker-only earlier version. Mirrors the feature set of
the demo at
    sessions/2026-05-14 Slide Labs Demo/demo-preview/demo-review.html

Sections rendered, in order:
  1. Header  (deck title, brief path, template path, timestamp).
  2. Collapsible dot-dash storyline pulled from the narrative brief +
     per-slide _prompt.md files. Starts collapsed.
  3. Brief-time QC banner.  Slide Lab doesn't yet run brief-QC, so we emit a
     single INFO collapsible saying "integration pending" — the visual
     structure is identical to the demo so we can wire real results later.
  4. Per-slide cards:
       header row (SLIDE N · title · status badge),
       three option tiles with PNG thumbs + taxonomy label,
       decision buttons (PICK A/B/C + ✗ NONE — TRY AGAIN),
       section-level feedback grid (5 textareas).
  5. Sticky footer with pick count + 4 buttons:
       Copy picks (paths), Show picks JSON, Export feedback, Clear all.

Persistence: localStorage, keyed by themed-PPTX absolute path → letter
(picks) and slide_NN_<field> → text (feedback notes).

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


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def file_uri(p: Path) -> str:
    """Convert an absolute Windows path to a file:/// URI."""
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
# Brief parser (deck-level metadata + per-slide blocks)
# ---------------------------------------------------------------------------

def parse_brief(brief_path: Path) -> dict:
    """Pull deck-level fields + per-slide governing/bullets out of the brief
    markdown. Returns a dict shaped like the DEMO_STORYLINE structure used in
    build_demo_review.py.
    """
    out = {
        "topic": "",
        "deck_type": "",
        "governing": "",
        "audience": "",
        "belief_break": "",
        "belief_leave": "",
        "say_back": "",
        "slides": [],   # list of {title, gov, bullets}
        "found": False,
    }
    if not brief_path or not brief_path.exists():
        return out
    text = read_text(brief_path)
    if not text:
        return out
    out["found"] = True

    # Topic: first h1.
    m = re.search(r"^#\s+(?:Narrative brief:\s*)?(.+?)\s*$", text, re.M)
    if m:
        out["topic"] = m.group(1).strip()

    # Deck type / governing thought / audience.
    def _h2_block(label: str) -> str:
        # Captures until next ## heading.
        pat = rf"^##\s+{re.escape(label)}\s*\n([\s\S]+?)(?=^##\s|\Z)"
        mm = re.search(pat, text, re.M)
        return mm.group(1).strip() if mm else ""

    out["deck_type"] = _h2_block("Deck type").splitlines()[0] if _h2_block("Deck type") else ""
    gov_block = _h2_block("Governing thought (the whole deck)") or _h2_block("Governing thought")
    if gov_block:
        out["governing"] = gov_block.splitlines()[0].strip()

    audience_block = _h2_block("Audience")
    if audience_block:
        # First line is the audience descriptor.
        out["audience"] = audience_block.splitlines()[0].strip()

    # Belief / say-back lines (live inside Audience block in this brief).
    def _bold_field(label: str) -> str:
        pat = rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)"
        mm = re.search(pat, text)
        return mm.group(1).strip() if mm else ""

    out["belief_break"] = _bold_field("Audience assumption to break")
    out["belief_leave"] = _bold_field("Audience belief to leave with")
    out["say_back"] = _bold_field("The single sentence the room should say back").strip().strip('"').strip("'")

    # Per-slide blocks: ### Slide N — Title ... up to next ### or EOF.
    slide_iter = list(re.finditer(r"^###\s+Slide\s+(\d+)\s*[—-]\s*(.+?)\s*$", text, re.M))
    for i, m in enumerate(slide_iter):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = slide_iter[i + 1].start() if i + 1 < len(slide_iter) else len(text)
        body = text[start:end]

        # Governing thought.
        gov = ""
        gm = re.search(r"\*\*Governing thought(?:\s*\(the claim\))?:\*\*\s*(.+?)(?:\n|$)", body)
        if gm:
            gov = gm.group(1).strip()
        if gov.startswith("[") and gov.endswith("]"):
            # Placeholder marker like "[Cover slide — no governing thought required]"
            gov_clean = gov
        else:
            gov_clean = gov

        # Bullets under Evidence / content (or Content).
        bullets: list[str] = []
        bm = re.search(r"\*\*(?:Evidence\s*/\s*content|Content):\*\*\s*\n([\s\S]+?)(?=\n\*\*|\n###|\Z)", body)
        if bm:
            block = bm.group(1)
            for line in block.splitlines():
                ls = line.strip()
                if not ls:
                    continue
                if ls.startswith("- "):
                    bullets.append(_md_inline_to_html(ls[2:].strip()))
                elif ls.startswith("  - ") or ls.startswith("\t- "):
                    # Sub-bullets — concatenate with parent.
                    if bullets:
                        bullets[-1] += " <em>" + _md_inline_to_html(ls.lstrip("- \t")) + "</em>"

        out["slides"].append({
            "n": num,
            "title": f"Slide {num} — {title}",
            "gov": gov_clean,
            "bullets": bullets,
        })

    return out


def _md_inline_to_html(s: str) -> str:
    """Tiny inline markdown: **bold** + *italic*.  Escapes everything else."""
    # Order matters: bold first, then italic.
    s_esc = html.escape(s)
    s_esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s_esc)
    s_esc = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s_esc)
    return s_esc


# ---------------------------------------------------------------------------
# Per-slide _prompt.md parser (so the storyline section still works even when
# the brief is missing).
# ---------------------------------------------------------------------------

PROMPT_FIELDS = {
    "title": r"\*\*Slide title:\*\*\s*(.+?)(?:\n|$)",
    "page_type": r"\*\*Page type \(heuristic\):\*\*\s*`?([^`\n]+)`?",
    "governing": r"\*\*Governing thought \(the claim\):\*\*\s*\n([\s\S]+?)(?:\n\n|\n\*\*)",
    "so_what": r"\*\*So-what \(the takeaway\):\*\*\s*\n([\s\S]+?)(?:\n\n|\n\*\*)",
}


def parse_prompt(prompt_path: Path) -> dict:
    out = {
        "title": None,
        "page_type": None,
        "governing": None,
        "so_what": None,
        "bullets": [],
        "found": False,
    }
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
    # Bullets from the prompt's Evidence / content block.
    bm = re.search(r"\*\*Evidence\s*/\s*content:\*\*\s*\n([\s\S]+?)(?=\n\*\*|\Z)", text)
    if bm:
        for line in bm.group(1).splitlines():
            ls = line.strip()
            if ls.startswith("- "):
                out["bullets"].append(_md_inline_to_html(ls[2:].strip()))
    return out


# ---------------------------------------------------------------------------
# Slide scan
# ---------------------------------------------------------------------------

OPTIONS = ("A", "B", "C")


def scan_slide(out_dir: Path, slide_num: int, slide_meta: Optional[dict]) -> dict:
    slide_id = f"slide_{slide_num:02d}"
    src_dir = out_dir / slide_id
    themed_dir = out_dir / "themed" / slide_id

    prompt = parse_prompt(src_dir / "_prompt.md")

    title = prompt.get("title")
    if not title and slide_meta:
        title = slide_meta.get("title")
    if not title:
        title = f"Slide {slide_num}"

    page_type = prompt.get("page_type")
    if not page_type and slide_meta:
        page_type = slide_meta.get("page_type")
    if page_type:
        page_type = page_type.split("\n")[0].strip()

    options = []
    for letter in OPTIONS:
        png = themed_dir / f"option_{letter}.png"
        themed_pptx = themed_dir / f"option_{letter}.pptx"
        src_pptx = src_dir / f"option_{letter}.pptx"
        themed_exists = themed_pptx.exists()
        qc_path = themed_dir / f"option_{letter}.qc.json"
        qc_summary = None
        qc_failed_checks: list = []
        if qc_path.exists():
            try:
                qc_data = json.loads(qc_path.read_text(encoding="utf-8"))
                qc_summary = qc_data.get("summary")
                for c in qc_data.get("checks", []):
                    if not c.get("pass"):
                        qc_failed_checks.append(
                            f"{c.get('check')} [{c.get('severity')}]: {c.get('detail', '')}"
                        )
            except Exception:
                qc_summary = None
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
        })

    return {
        "n": slide_num,
        "slide_id": slide_id,
        "title": title,
        "page_type": page_type,
        "governing": prompt.get("governing"),
        "so_what": prompt.get("so_what"),
        "bullets": prompt.get("bullets", []),
        "prompt_path": src_dir / "_prompt.md",
        "prompt_found": prompt.get("found", False),
        "options": options,
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
# Storyline rendering (dot-dash)
# ---------------------------------------------------------------------------

def render_storyline_html(storyline: dict, slides: list) -> str:
    """If brief parsing succeeded, render the rich dot-dash block.  If not,
    fall back to a per-slide governing-from-prompt block so the section is
    never empty."""
    # Prefer brief slides, fall back to per-slide prompts.
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
    <div class="dd-callout">Read the dots top-to-bottom — they should form the deck's argument as a single coherent story. If the dots-alone don't make sense, the storyline is broken.</div>
    {blocks}
  </div>
</div>
</details>
"""


# ---------------------------------------------------------------------------
# Brief-QC banner (stub for slide-lab — wire real QC results later)
# ---------------------------------------------------------------------------

def _render_qc_info_stub() -> str:
    return (
        '<div class="qc-brief-banner">'
        '<div class="qc-brief-banner-title">Brief-time QC report</div>'
        '<details class="qc-brief-section qc-brief-info">'
        '<summary><span class="qc-brief-icon">i</span>INFO &middot; brief_qc.json not found</summary>'
        '<ul>'
        '<li>No <code>brief_qc.json</code> was found in this output directory. '
        'Re-run <code>build_deck.py</code> to generate it.</li>'
        '</ul>'
        '</details>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# QC humanizer — translate dev-speak QC messages into consultant English
# ---------------------------------------------------------------------------
# brief_qc.check_brief emits messages like:
#   "slide 2: title is 320 chars — will wrap to 3+ lines (A1/A2)"
#   "cover missing required field 'tagline' (A7)"
#   "closing CTA has 5 sub_asks; needs 3 (A7)"
#   "trailing ellipsis (...) — mid-thought? '...something' (A8)"
# Rule codes A1..A9 reference internal designer-brief rules consultants don't
# know. This humanizer pattern-matches each known shape and rewrites to plain
# English. The rule code is preserved as a small grey suffix for debugging.

import re as _re

# Each entry: (compiled regex on raw message, callable returning plain-English text).
# The location prefix ("slide N:" or "cover:" or "slide N.list[0].body:") is
# extracted separately and prepended after humanization so it stays consistent.

# Accept "slide N", "slide_N", "slide N.field", "cover", "closing CTA" etc as a
# location. The capture group is everything up to the first colon followed by a
# space — the "slide 1: foo" pattern (with the space) was the breaker on the
# first pass.
_LOC_RE = _re.compile(r"^([^:]{1,80}?):\s+(.+)$", _re.DOTALL)

def _humanize_loc(loc: str) -> str:
    """slide_03 → 'Slide 3'; slide 4.content.evidence → 'Slide 4 (content evidence)'."""
    if not loc:
        return ""
    loc = loc.strip()
    m = _re.match(r"^slide[_ ]?(\d+)(?:\.(.+))?$", loc, _re.IGNORECASE)
    if m:
        n = int(m.group(1))
        suffix = (m.group(2) or "").strip()
        base = f"Slide {n}"
        if not suffix:
            return base
        # "content.evidence" -> "content / evidence"; "list[0].heading" -> "list #1 heading"
        suffix = _re.sub(r"\[(\d+)\]", lambda mm: f" #{int(mm.group(1))+1}", suffix)
        suffix = suffix.replace(".", " / ").replace("_", " ")
        return f"{base} ({suffix})"
    return loc.replace("_", " ")

# Body humanizer rules: ordered list of (raw_pattern, lambda match -> plain text).
# Patterns try to match the message body (after the "loc:" prefix is removed).
_HUMAN_RULES: list[tuple[_re.Pattern, "callable"]] = [
    (_re.compile(r"^title is (\d+) chars.*will wrap to 3\+ lines", _re.I),
     lambda m: f"Title is too long ({m.group(1)} characters) — it will wrap to 3 or more lines. Shorten it so the headline fits on 1 or 2 lines."),

    (_re.compile(r"^title predicted to wrap to (\d+) lines", _re.I),
     lambda m: f"Title may wrap to {m.group(1)} lines. If that wasn't intended, shorten the title."),

    (_re.compile(r"^title is (\d+) chars \(over the (\d+)-char guideline", _re.I),
     lambda m: f"Title is slightly long ({m.group(1)} characters; recommended ≤{m.group(2)}). Tighten if you can."),

    (_re.compile(r"^([\w.]+)\[(\d+)\]\.heading is (\d+) chars \(>40", _re.I),
     lambda m: f"Item #{int(m.group(2))+1} heading is too long ({m.group(3)} characters). Keep headings under 40 — they're labels, not sentences."),

    (_re.compile(r"^([\w.]+)\[(\d+)\]\.body is (\d+) chars \(>200", _re.I),
     lambda m: f"Item #{int(m.group(2))+1} body text is too long ({m.group(3)} characters). Trim to under 200 — readers scan slides, they don't read paragraphs."),

    (_re.compile(r"^forbidden placeholder (.+)$", _re.I),
     lambda m: f"Placeholder text was left in: {m.group(1)}. Replace with real content."),

    (_re.compile(r"^cover missing required field '([^']+)'", _re.I),
     lambda m: f"Cover slide is missing the {m.group(1)}. Add it to the brief."),

    (_re.compile(r"^closing CTA missing required field '([^']+)'", _re.I),
     lambda m: f"Closing slide is missing the {m.group(1)}. The ask needs all three of: title, sub-asks, and a clear action verb."),

    (_re.compile(r"^closing CTA has (\d+) sub_asks; needs (\d+)", _re.I),
     lambda m: f"Closing slide has {m.group(1)} sub-asks — Slide Lab recommends exactly {m.group(2)}. Pick the {m.group(2)} that matter most."),

    (_re.compile(r"^editorial_emphasis has (\d+) items; trim to <=(\d+)", _re.I),
     lambda m: f"Editorial emphasis has {m.group(1)} items — that's too many to land. Trim to {m.group(2)} or fewer."),

    (_re.compile(r"^run-on sentence \((\d+) words, (\d+) chars\)[:\s]*(.*)$", _re.I | _re.DOTALL),
     lambda m: f"Run-on sentence ({m.group(1)} words). Break it into two shorter sentences." + (f' Excerpt: {m.group(3).strip()[:100]}' if m.group(3).strip() else "")),

    (_re.compile(r"^trailing ellipsis.*mid-thought.*?['\"](.+?)['\"]", _re.I | _re.DOTALL),
     lambda m: f"Text trails off with an ellipsis (\"…\") — looks unfinished. Excerpt: \"{m.group(1).strip()[:80]}\". Finish the sentence or rephrase."),

    (_re.compile(r"^dangling truncation marker.*?['\"](.+?)['\"]", _re.I | _re.DOTALL),
     lambda m: f"Text ends with a dash or comma — looks like a fragment. Excerpt: \"{m.group(1).strip()[:80]}\". Add the rest or trim it."),

    (_re.compile(r"^no terminal punctuation.*?['\"](.+?)['\"]", _re.I | _re.DOTALL),
     lambda m: f"Sentence is missing ending punctuation (\".\" \"!\" or \"?\"). Excerpt: \"{m.group(1).strip()[:80]}\"."),

    (_re.compile(r"^language_callback error:\s*(.+)$", _re.I),
     lambda m: f"Internal QC error: {m.group(1)} — flag for review."),
]

_RULECODE_RE = _re.compile(r"\s*\(([A-Z]\d(?:/[A-Z]\d)?)\)\s*$")

def humanize_qc_msg(raw: str) -> tuple[str, str, str]:
    """
    Take a raw brief_qc message and return (location, human_body, rule_code).

    location:    "Slide 2" or "Cover" or "" — already humanized
    human_body:  plain-English sentence(s)
    rule_code:   "A1/A2" or "A7" or "" — kept as a small debug suffix

    Falls back to the raw message body if no humanizer rule matches.
    """
    if not raw or not isinstance(raw, str):
        return ("", str(raw or ""), "")

    # Strip the rule code first so the body matchers don't see it
    code_match = _RULECODE_RE.search(raw)
    rule_code = code_match.group(1) if code_match else ""
    if code_match:
        raw = raw[: code_match.start()].rstrip()

    # Split off the "loc: " prefix
    m = _LOC_RE.match(raw)
    if m:
        loc_raw = m.group(1)
        body = m.group(2).strip()
        loc = _humanize_loc(loc_raw)
    else:
        loc = ""
        body = raw

    # Apply the first matching humanizer rule
    for pat, rewriter in _HUMAN_RULES:
        m2 = pat.match(body)
        if m2:
            try:
                return (loc, rewriter(m2), rule_code)
            except Exception:
                # If a rule's lambda errors out (regex group mismatch, etc.),
                # fall through to the raw body so QC still displays *something*.
                pass

    return (loc, body, rule_code)


def render_qc_banner(out_dir: Path) -> str:
    """Render the Brief-time QC banner.

    Reads <out>/brief_qc.json (produced by build_deck.py) and emits two
    collapsible sections: BLOCKING (red, open if non-empty) and WARNING
    (yellow, collapsed). Raw issue strings are humanized via humanize_qc_msg
    before display — consultants see plain English with the dev rule code as
    a small grey suffix for debug breadcrumbs.
    """
    qc_path = out_dir / "brief_qc.json"
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
            '</details>'
            '</div>'
        )

    blocking = list(payload.get("blocking") or [])
    warnings = list(payload.get("warnings") or [])
    summary = payload.get("summary") or ""

    parts: list[str] = []
    parts.append('<div class="qc-brief-banner">')
    parts.append('<div class="qc-brief-banner-title">Brief-time QC report</div>')

    if summary:
        parts.append(
            f'<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px;">'
            f'{html.escape(summary)}</div>'
        )

    def _render_qc_li(line: str) -> str:
        loc, body, code = humanize_qc_msg(line)
        loc_html = f'<span class="qc-loc">{html.escape(loc)}</span> ' if loc else ""
        body_html = html.escape(body)
        code_html = f'<span class="qc-code" title="internal designer-brief rule reference">({html.escape(code)})</span>' if code else ""
        return f'<li>{loc_html}<span class="qc-body">{body_html}</span> {code_html}</li>'

    open_attr = " open" if blocking else ""
    if blocking:
        items = "".join(_render_qc_li(line) for line in blocking)
        parts.append(
            f'<details class="qc-brief-section qc-brief-blocking"{open_attr}>'
            f'<summary><span class="qc-brief-icon">!</span>Must fix &middot; {len(blocking)}</summary>'
            f'<ul>{items}</ul>'
            f'</details>'
        )
    else:
        parts.append(
            '<details class="qc-brief-section qc-brief-info">'
            '<summary><span class="qc-brief-icon">&#10003;</span>Must fix &middot; 0 (none — brief is clean)</summary>'
            '<ul><li>No issues that block this deck from building.</li></ul>'
            '</details>'
        )

    if warnings:
        items = "".join(_render_qc_li(line) for line in warnings)
        parts.append(
            f'<details class="qc-brief-section qc-brief-warning">'
            f'<summary><span class="qc-brief-icon">~</span>Worth a look &middot; {len(warnings)}</summary>'
            f'<ul>{items}</ul>'
            f'</details>'
        )
    else:
        parts.append(
            '<details class="qc-brief-section qc-brief-info">'
            '<summary><span class="qc-brief-icon">&#10003;</span>Worth a look &middot; 0</summary>'
            '<ul><li>Nothing to flag.</li></ul>'
            '</details>'
        )

    parts.append('</div>')
    return "".join(parts)


# Back-compat shim in case anything still calls the old name.
def render_qc_banner_stub() -> str:
    return _render_qc_info_stub()
# ---------------------------------------------------------------------------
# Per-slide card
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

    # QC badge: top-right corner of the option-frame.
    qc_summary = opt.get("qc_summary") or {}
    qc_failed = opt.get("qc_failed_checks") or []
    n_block = int(qc_summary.get("block", 0)) if qc_summary else 0
    n_warn  = int(qc_summary.get("warn", 0))  if qc_summary else 0
    if qc_summary is None or qc_summary == {}:
        qc_badge = ""
    elif n_block > 0:
        tooltip = " | ".join(qc_failed[:6]) or "blocking issue"
        qc_badge = (
            f'<div class="qc-badge block" title="{html.escape(tooltip)}">BLOCK</div>'
        )
    elif n_warn > 0:
        tooltip = " | ".join(qc_failed[:6]) or f"{n_warn} warning(s)"
        qc_badge = (
            f'<div class="qc-badge warn" title="{html.escape(tooltip)}">~ {n_warn}</div>'
        )
    else:
        qc_badge = '<div class="qc-badge ok" title="all QC checks passed">OK QC</div>'

    return f"""
<div class="option" data-slide="{sid}" data-letter="{letter}" data-pptx="{html.escape(themed_path_str)}">
  <div class="option-frame">{thumb}{qc_badge}</div>
  <div class="option-meta">
    <span class="option-letter">Option {letter}</span>
    <div class="option-taxon">{html.escape(page_type)}</div>
  </div>
</div>
"""


def render_card(slide: dict) -> str:
    sid = slide["slide_id"]
    n = slide["n"]
    title = html.escape(slide.get("title") or f"Slide {n}")

    # Pre-encoded themed paths for each option (used by the JS pickers).
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

    # Feedback grid.
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
        f"None of options A/B/C landed. Pick a different layout family this time "
        f"(do not return any of the three already shown). Honor all hard "
        f"constraints in section 4 of the prompt."
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
# CSS + JS
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
body {
  font-family: 'Inter', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.45;
  padding-bottom: 90px;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code { font-family: Consolas, monospace; font-size: 12px; color: var(--text-dim); word-break: break-all; }

/* Top bar */
.topbar {
  position: sticky; top: 0; z-index: 100;
  background: var(--panel);
  border-bottom: 2px solid var(--border);
  padding: 14px 24px;
  display: flex; align-items: center; gap: 18px;
}
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

/* Storyline section */
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
.dd-bullets li strong { color: var(--text); }
.dd-bullets li em { color: var(--accent-soft); }

/* QC banner */
.qc-brief-banner { background: var(--panel-2); border-bottom: 1px solid var(--border); padding: 12px 24px; }
.qc-brief-banner-title { font-size: 10px; font-weight: 800; color: var(--text); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.qc-brief-section { margin-top: 6px; padding: 8px 12px; border-radius: 4px; border-left: 3px solid; font-size: 11px; line-height: 1.5; }
.qc-brief-blocking { background: rgba(220,38,38,0.08); border-color: var(--reject); }
.qc-brief-warning  { background: rgba(202,138,4,0.08); border-color: var(--tweak); }
.qc-brief-info     { background: rgba(37,99,235,0.08); border-color: var(--info); }
.qc-brief-section summary { font-weight: 800; cursor: pointer; outline: none; display: flex; align-items: center; gap: 6px; padding: 2px 0; list-style: none; }
.qc-brief-section summary::-webkit-details-marker { display: none; }
.qc-brief-section[open] summary { margin-bottom: 6px; }
.qc-brief-blocking summary { color: var(--reject); }
.qc-brief-warning  summary { color: var(--tweak); }
.qc-brief-info     summary { color: var(--info); }
.qc-brief-icon { display: inline-block; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-weight: 800; }
.qc-brief-blocking .qc-brief-icon { background: var(--reject); color: white; }
.qc-brief-warning  .qc-brief-icon { background: var(--tweak); color: white; }
.qc-brief-info     .qc-brief-icon { background: var(--info); color: white; }
.qc-brief-section ul { list-style: none; margin: 0; padding: 0; }
.qc-brief-section li { padding: 4px 0 4px 12px; position: relative; color: var(--text); line-height: 1.5; }
.qc-brief-section li::before { content: '•'; position: absolute; left: 0; color: currentColor; }
.qc-brief-section li .qc-loc { display: inline-block; font-weight: 700; color: var(--accent); margin-right: 4px; min-width: 64px; }
.qc-brief-section li .qc-body { color: var(--text); }
.qc-brief-section li .qc-code { font-size: 9px; color: var(--text-dim); opacity: 0.55; font-family: Consolas, 'Courier New', monospace; margin-left: 6px; cursor: help; }

/* Cards */
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
.regen-panel .open-prompt { margin-left: 10px; font-size: 11px; }

/* Sticky footer */
footer.summary-footer {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: rgba(15,23,42,0.96);
  border-top: 1px solid var(--border);
  padding: 12px 24px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 14px;
  z-index: 50;
  backdrop-filter: blur(6px);
}
footer.summary-footer .count { font-size: 14px; font-weight: 700; color: var(--text); }
footer.summary-footer .count .num { color: var(--accent); }
footer.summary-footer .btns { display: flex; gap: 8px; flex-wrap: wrap; }
button.btn { background: var(--accent); color: #fff; border: none; padding: 9px 14px; border-radius: 5px; font-size: 12px; font-weight: 700; font-family: inherit; cursor: pointer; transition: opacity 0.12s; }
button.btn:hover { opacity: 0.85; }
button.btn.ghost { background: transparent; border: 1px solid #475569; color: #CBD5E1; }
button.btn.ghost:hover { border-color: var(--accent); color: #fff; }
button.btn.small { padding: 6px 11px; font-size: 11px; }
button.btn.primary { background: var(--accent); color: #fff; border: 1px solid var(--accent); }
button.btn.primary:hover { opacity: 1; filter: brightness(1.1); box-shadow: 0 2px 12px rgba(161,0,255,0.45); }
button.btn.big { padding: 13px 26px; font-size: 14px; letter-spacing: 0.3px; }
footer.summary-footer .count .hint { font-weight: 400; color: var(--text-dim, #94A3B8); font-size: 12px; margin-left: 6px; }

/* Dialog (text export) */
dialog#picks-dialog { background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 0; max-width: 720px; width: 90vw; }
dialog#picks-dialog::backdrop { background: rgba(0,0,0,0.6); }
dialog#picks-dialog .dlg-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
dialog#picks-dialog .dlg-head h3 { margin: 0; font-size: 15px; }
dialog#picks-dialog pre { margin: 0; padding: 16px 18px; background: var(--bg); color: #86EFAC; font-size: 12px; font-family: Consolas, monospace; max-height: 60vh; overflow: auto; white-space: pre-wrap; word-break: break-all; }
dialog#picks-dialog .dlg-foot { padding: 12px 18px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 8px; }

/* Toast */
#toast { position: fixed; bottom: 88px; left: 50%; transform: translateX(-50%); background: var(--panel); border: 1px solid var(--accent); color: var(--text); padding: 9px 16px; border-radius: 5px; font-size: 12px; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 200; max-width: 80vw; }
#toast.show { opacity: 1; }
"""


# Persistence keys are derived from the absolute themed-PPTX path (for picks)
# and slide_NN_<field> (for feedback notes).  This keeps state stable across
# renames of REVIEW.html and ties it to the actual build artifacts.
JS = r"""
const PICKS_KEY = "slidelab_picks_v1::" + window.location.pathname;
const FB_KEY    = "slidelab_feedback_v1::" + window.location.pathname;
const REGEN_KEY = "slidelab_regen_v1::"    + window.location.pathname;
const TOTAL_SLIDES = window.__TOTAL_SLIDES__;
const SLIDE_IDS = window.__SLIDE_IDS__;       // ordered list of slide_NN
const SLIDE_MAP = window.__SLIDE_MAP__;       // {slide_id: {A: pptxPath, B: ..., C: ...}}

/* ----------------------------------------------------------------------
   localStorage helpers
   ---------------------------------------------------------------------- */
function loadJson(key) {
    try { return JSON.parse(localStorage.getItem(key) || "{}"); }
    catch (e) { return {}; }
}
function saveJson(key, obj) { localStorage.setItem(key, JSON.stringify(obj)); }

function loadPicks()  { return loadJson(PICKS_KEY); }     // {pptxPath: "A"|"B"|"C"}
function savePicks(p) { saveJson(PICKS_KEY, p); }
function loadRegens() { return loadJson(REGEN_KEY); }     // {slide_id: true}
function saveRegens(r){ saveJson(REGEN_KEY, r); }
function loadFb()     { return loadJson(FB_KEY); }        // {slide_id_field: text}
function saveFb(f)    { saveJson(FB_KEY, f); }

/* ----------------------------------------------------------------------
   Render state into DOM
   ---------------------------------------------------------------------- */
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
    if (letter) {
        badge.classList.add("picked");
        badge.textContent = "DECIDED " + letter;
    } else if (isNone) {
        badge.classList.add("none");
        badge.textContent = "REGEN REQUESTED";
    } else {
        badge.classList.add("pending");
        badge.textContent = "PENDING";
    }

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
    // Restore feedback textareas.
    const fb = loadFb();
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        const k = ta.dataset.slide + "_" + ta.dataset.field;
        if (fb[k]) ta.value = fb[k];
    });
    updateCounts();
}

/* ----------------------------------------------------------------------
   Pick / none actions
   ---------------------------------------------------------------------- */
function pickOption(sid, letter) {
    const map = SLIDE_MAP[sid] || {};
    const pptx = map[letter];
    if (!pptx) {
        showToast("Option " + letter + " for " + sid + " has no themed PPTX.");
        return;
    }
    const picks = loadPicks();
    // Clear any existing pick for this slide (could be a different letter).
    for (const l of Object.keys(map)) {
        if (map[l] && picks[map[l]] === l) delete picks[map[l]];
    }
    // Toggle: if same letter clicked again, leave cleared.
    const current = pickForSlide(sid);
    if (current !== letter) {
        picks[pptx] = letter;
    }
    savePicks(picks);
    // Clear regen request if any.
    const regens = loadRegens();
    if (regens[sid]) { delete regens[sid]; saveRegens(regens); }
    renderSlideState(sid);
    updateCounts();
}

function pickNone(sid) {
    const regens = loadRegens();
    if (regens[sid]) {
        delete regens[sid];
    } else {
        regens[sid] = true;
        // Clear any existing pick.
        const map = SLIDE_MAP[sid] || {};
        const picks = loadPicks();
        for (const l of Object.keys(map)) {
            if (map[l] && picks[map[l]] === l) delete picks[map[l]];
        }
        savePicks(picks);
    }
    saveRegens(regens);
    renderSlideState(sid);
    updateCounts();
}

/* ----------------------------------------------------------------------
   Feedback persistence (textareas)
   ---------------------------------------------------------------------- */
function wireFeedback() {
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => {
        ta.addEventListener("input", () => {
            const fb = loadFb();
            const k = ta.dataset.slide + "_" + ta.dataset.field;
            if (ta.value) fb[k] = ta.value;
            else delete fb[k];
            saveFb(fb);
        });
    });
}

/* ----------------------------------------------------------------------
   Footer button handlers — single "Build my deck" + Clear
   ---------------------------------------------------------------------- */
async function buildDeck() {
    /* Collect picks. If nothing picked, halt with a friendly message. */
    const picks = {};
    SLIDE_IDS.forEach(sid => {
        const letter = pickForSlide(sid);
        if (letter) picks[sid] = letter;
    });
    if (Object.keys(picks).length === 0) {
        showToast("No picks yet. Click a thumbnail on each slide first.");
        return;
    }

    /* Optional feedback collection — if user wrote any, include it in the
       command so Claude can read it. Keeps the user's input alive across
       the handoff without making them export anything. */
    const fb = loadFb();
    const fbBySlide = {};
    Object.keys(fb).forEach(k => {
        const m = k.match(/^(slide_\d+)_(.+)$/);
        if (m && fb[k] && fb[k].trim()) {
            const sid = m[1], field = m[2];
            if (!fbBySlide[sid]) fbBySlide[sid] = {};
            fbBySlide[sid][field] = fb[k];
        }
    });
    const regens = loadRegens();
    const regenSlides = Object.keys(regens).filter(s => regens[s]);

    /* Build a Claude-natural-language compile command. The string is what the
       user pastes into a Claude Code session. It tells Claude where the
       orchestrator output lives, which option to take per slide, and any
       feedback / regen flags the user left behind. Claude writes picks.json,
       then runs compile_picks.py. */
    let cmd = "Compile my slide-lab deck.\n";
    cmd += "Out dir: " + window.__OUT_DIR__ + "\n";
    cmd += "Picks: " + JSON.stringify(picks) + "\n";
    if (regenSlides.length) {
        cmd += "Regen requested (do not compile, rebuild instead): " + regenSlides.join(", ") + "\n";
    }
    if (Object.keys(fbBySlide).length) {
        cmd += "Feedback:\n";
        Object.keys(fbBySlide).sort().forEach(sid => {
            const f = fbBySlide[sid];
            cmd += "  " + sid + ":\n";
            Object.keys(f).forEach(k => {
                cmd += "    " + k + ": " + f[k].replace(/\n/g, " ") + "\n";
            });
        });
    }

    try {
        await navigator.clipboard.writeText(cmd);
        showToast("Compile command copied. Paste it into Claude Code to build your deck.");
    } catch (e) {
        showDialog(cmd, "Compile command (Ctrl+C to copy)");
    }
}

function clearAll() {
    if (!confirm("Clear all picks, regens, and feedback?")) return;
    savePicks({}); saveRegens({}); saveFb({});
    document.querySelectorAll("textarea[data-slide][data-field]").forEach(ta => ta.value = "");
    renderAll();
    showToast("Cleared.");
}

async function copyRegen(sid) {
    const ta = document.querySelector("#regen-" + sid + " textarea.regen-text");
    if (!ta) return;
    try { await navigator.clipboard.writeText(ta.value); showToast("Regen text copied."); }
    catch (e) { ta.select(); document.execCommand && document.execCommand("copy"); showToast("Selected — Ctrl+C to copy."); }
}

/* ----------------------------------------------------------------------
   Clipboard / dialog helpers
   ---------------------------------------------------------------------- */
async function copyOrShow(text, heading) {
    try { await navigator.clipboard.writeText(text); }
    catch (e) { showDialog(text, heading + " (Ctrl+C to copy)"); }
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
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => t.classList.remove("show"), 1800);
}

/* ----------------------------------------------------------------------
   Init
   ---------------------------------------------------------------------- */
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
        try { await navigator.clipboard.writeText(txt); showToast("Copied."); }
        catch (e) {}
    });
    document.getElementById("btn-dlg-close").addEventListener("click", () => {
        document.getElementById("picks-dialog").close();
    });
    wireFeedback();
    renderAll();
});
"""


# ---------------------------------------------------------------------------
# Build HTML
# ---------------------------------------------------------------------------

def build_html(out_dir: Path, meta: Optional[dict], slides: list, storyline: dict) -> str:
    # SLIDE_MAP for the JS: {slide_id: {A: themed_pptx_path, ...}}
    slide_map: dict[str, dict[str, str]] = {}
    slide_ids: list[str] = []
    for s in slides:
        sid = s["slide_id"]
        slide_ids.append(sid)
        slide_map[sid] = {}
        for o in s["options"]:
            if o["themed_exists"]:
                slide_map[sid][o["letter"]] = str(o["themed_pptx"].resolve())

    deck_meta = (meta or {}).get("deck_meta", {}) or {}
    deck_type = deck_meta.get("deck_type") or storyline.get("deck_type") or "Slide Lab deck"
    deck_topic = storyline.get("topic") or "Untitled deck"
    governing = deck_meta.get("governing_thought") or storyline.get("governing") or ""
    generated = (meta or {}).get("generated_at") or datetime.now().isoformat(timespec="seconds")
    brief_path = (meta or {}).get("brief", "")
    template_path = (meta or {}).get("template", "")
    slide_count = (meta or {}).get("slide_count", len(slides))

    storyline_html = render_storyline_html(storyline, slides)
    qc_html = render_qc_banner(out_dir)
    cards_html = "\n".join(render_card(s) for s in slides)

    topbar_html = f"""
<div class="topbar">
  <div>
    <div class="title">{html.escape(deck_topic)} &middot; OPTIONS REVIEW &middot; {slide_count} slides</div>
    <div class="title-sub">{html.escape(deck_type)} &middot; Pick A/B/C per slide or mark NONE to try again.</div>
    <div class="topbar-meta">
      <div class="k">Generated</div><div class="v">{html.escape(generated)}</div>
      <div class="k">Brief</div><div class="v"><code>{html.escape(brief_path)}</code></div>
      <div class="k">Template</div><div class="v"><code>{html.escape(template_path)}</code></div>
      <div class="k">Output</div><div class="v"><code>{html.escape(str(out_dir.resolve()))}</code></div>
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
  <div class="count"><span class="num" id="pick-count">0</span> / <span id="total-slides">0</span> picked &middot; <span class="hint">picks auto-save in this browser</span></div>
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
        f"<title>{html.escape(deck_topic)} &mdash; REVIEW</title>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<style>{CSS}</style></head><body>"
        f"{topbar_html}"
        f"{storyline_html}"
        f"{qc_html}"
        f"<div class=\"cards\">{cards_html}</div>"
        f"{footer_html}"
        f"<script>{js_setup}{JS}</script>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build REVIEW.html for a Slide Lab orchestrator output dir.")
    ap.add_argument("--out", required=True, help="Orchestrator output directory.")
    args = ap.parse_args(argv)

    out_dir = Path(args.out).resolve()
    if not out_dir.exists() or not out_dir.is_dir():
        print(f"[error] --out is not a directory: {out_dir}", file=sys.stderr)
        return 2

    meta_path = out_dir / "_meta.json"
    meta: Optional[dict] = None
    if meta_path.exists():
        try:
            meta = json.loads(read_text(meta_path))
        except Exception as exc:
            print(f"[warn] _meta.json unreadable ({exc}); falling back.", file=sys.stderr)
    else:
        print("[warn] _meta.json missing; using dir scan.", file=sys.stderr)

    # Slide numbers / metadata.
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

    # Parse the brief for the storyline.
    storyline = {"slides": [], "found": False}
    if meta and meta.get("brief"):
        storyline = parse_brief(Path(meta["brief"]))
    if not storyline.get("found"):
        # No brief — fabricate a minimal storyline shape from deck_meta + prompts.
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
    review_path = out_dir / "REVIEW.html"
    review_path.write_text(html_text, encoding="utf-8")

    print(f"[ok] wrote {review_path}")
    print(f"     {len(slides)} slides x 3 options = {total_opts} tiles")
    print(f"     missing PNGs: {missing_png}, missing themed PPTX: {missing_themed}")
    print(f"     storyline parsed from brief: {storyline.get('found')}")
    print(f"     size: {fmt_bytes(review_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
