"""Slide Lab deck orchestrator — Part A: per-slide prompt prep.

Takes a narrative brief + client template path and writes per-slide agent prompts
that any general-purpose Claude Code agent can execute to produce 3 standalone
python-pptx scripts per slide (option_A.py / option_B.py / option_C.py).

Inputs (CLI):
  --brief PATH       narrative brief .md
  --template PATH    client PPTX template
  --out PATH         output directory (created if missing)
  --slides N         optional limit to first N slides

Outputs:
  <out>/slide_NN/_prompt.md      — full agent prompt per slide
  <out>/dispatch_plan.md         — top-level dispatch instructions
  <out>/_meta.json               — run metadata + parsed brief

This script ONLY writes prompts. Agents produce option_X.py. The companion
finalize_deck.py script then executes those .py, grafts onto the
client template, and renders PNGs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Hard-coded paths to skill files referenced inside the per-slide prompts.
# ---------------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parents[1]

# Make `twins.brief_qc` importable regardless of cwd.
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from twins.brief_qc import check_brief  # noqa: E402

HELPERS_PATH = SKILL_ROOT / "twins" / "helpers.py"
REFERENCE_DIR = SKILL_ROOT / "reference"
QC_SKILL = SKILL_ROOT.parent / "slide-qc" / "SKILL.md"

RULEBOOK_FILES = [
    REFERENCE_DIR / "phase-a-rules.md",
    REFERENCE_DIR / "slot-design-rules.md",
    REFERENCE_DIR / "visual-treatment-library.md",
    REFERENCE_DIR / "page-types.md",
    REFERENCE_DIR / "rules.md",
    REFERENCE_DIR / "glossary.md",
    REFERENCE_DIR / "known-issues-and-improvements.md",
]

# Distilled rulebook — gets INLINED into every per-slide prompt so the rules
# travel with the prompt and aren't dependent on the agent reading by-path.
DESIGNER_BRIEF_PATH = REFERENCE_DIR / "designer-brief.md"

# Production exemplar library — the canonical "do" set for Slide Lab builds.
# See exemplars/INDEX.md for the catalog and per-slide WHY notes.
EXEMPLARS_ROOT = SKILL_ROOT / "exemplars" / "do"


# ---------------------------------------------------------------------------
# Brief parsing
# ---------------------------------------------------------------------------
@dataclass
class SlideBrief:
    n: int
    title: str
    raw_section: str
    governing_thought: str = ""
    so_what: str = ""
    editorial_emphasis: str = ""
    evidence: str = ""
    not_section: str = ""
    chart_type: str = ""
    content: str = ""  # cover/screenshot slides use plain "Content:" instead

    def is_screenshot_placeholder(self) -> bool:
        return "screenshot placeholder" in self.governing_thought.lower() or \
               "screenshot placeholder" in self.editorial_emphasis.lower()

    def is_cover(self) -> bool:
        return "cover slide" in self.governing_thought.lower() or self.n == 1


_FIELD_HEADERS = {
    "governing_thought": [
        r"\*\*Governing thought.*?:\*\*",
    ],
    "so_what": [
        r"\*\*So-what.*?:\*\*",
    ],
    "editorial_emphasis": [
        r"\*\*Editorial emphasis:\*\*",
    ],
    "evidence": [
        r"\*\*Evidence / content:\*\*",
        r"\*\*Evidence/content:\*\*",
    ],
    "content": [
        r"\*\*Content:\*\*",
    ],
    "not_section": [
        r"\*\*What this slide is NOT:\*\*",
    ],
    "chart_type": [
        r"\*\*Chart type:\*\*",
    ],
}


def _extract_field(section: str, patterns: list[str]) -> str:
    """Pull text after one of the labeled headers, up to the next ** header or end."""
    for pat in patterns:
        m = re.search(pat, section)
        if not m:
            continue
        start = m.end()
        # Stop at the next bolded header (start of next field) or end of section.
        rest = section[start:]
        stop = re.search(r"\n\*\*[A-Z][^*]{0,60}:\*\*", rest)
        body = rest[: stop.start()] if stop else rest
        return body.strip()
    return ""


def parse_brief(brief_path: Path) -> tuple[list[SlideBrief], dict]:
    """Parse a narrative brief markdown into SlideBrief objects and deck metadata."""
    text = brief_path.read_text(encoding="utf-8")

    # Deck-level metadata captured for _meta.json / dispatch_plan.md.
    deck_meta = {
        "deck_type": "",
        "narrative_framework": "",
        "governing_thought": "",
        "audience": "",
    }
    m = re.search(r"## Deck type\s*\n(.+?)(?:\n##|\n---)", text, re.DOTALL)
    if m:
        deck_meta["deck_type"] = m.group(1).strip()
    m = re.search(r"## Narrative framework\s*\n(.+?)(?:\n##|\n---)", text, re.DOTALL)
    if m:
        deck_meta["narrative_framework"] = m.group(1).strip()
    m = re.search(r"## Governing thought.*?\n(.+?)(?:\n##|\n---)", text, re.DOTALL)
    if m:
        deck_meta["governing_thought"] = m.group(1).strip()
    m = re.search(r"## Audience\s*\n(.+?)(?:\n##|\n---|\Z)", text, re.DOTALL)
    if m:
        deck_meta["audience"] = m.group(1).strip()

    # Each ### Slide <id> [— Title] section, terminated by the next ### or ## or EOF.
    # The slide id accepts BOTH digit IDs ("### Slide 1") and letter IDs ("### Slide A").
    # The title is OPTIONAL — some real briefs use "### Slide 1" with no dash/title.
    # Letter IDs get mapped A=1, B=2, ... Z=26 so slide_NN/ directory naming stays int.
    slide_re = re.compile(
        r"###\s+Slide\s+(\w+)\s*(?:[—\-:]\s*(.+?))?\n(.*?)(?=\n###\s+Slide\s+\w+|\n##\s|\Z)",
        re.DOTALL,
    )

    def _slide_id_to_int(raw: str) -> int:
        raw = raw.strip()
        if raw.isdigit():
            return int(raw)
        if len(raw) == 1 and raw.isalpha():
            return ord(raw.upper()) - ord("A") + 1
        m_digits = re.match(r"^\d+", raw)
        if m_digits:
            return int(m_digits.group(0))
        # Last resort: use position-in-document. Caller resorts by n anyway.
        return 0

    slides: list[SlideBrief] = []
    for match in slide_re.finditer(text):
        n = _slide_id_to_int(match.group(1))
        title = (match.group(2) or "").strip()
        body = match.group(3)

        slides.append(SlideBrief(
            n=n,
            title=title,
            raw_section=body.strip(),
            governing_thought=_extract_field(body, _FIELD_HEADERS["governing_thought"]),
            so_what=_extract_field(body, _FIELD_HEADERS["so_what"]),
            editorial_emphasis=_extract_field(body, _FIELD_HEADERS["editorial_emphasis"]),
            evidence=_extract_field(body, _FIELD_HEADERS["evidence"]),
            content=_extract_field(body, _FIELD_HEADERS["content"]),
            not_section=_extract_field(body, _FIELD_HEADERS["not_section"]),
            chart_type=_extract_field(body, _FIELD_HEADERS["chart_type"]),
        ))

    slides.sort(key=lambda s: s.n)
    return slides, deck_meta


# ---------------------------------------------------------------------------
# Brief-QC adapter: SlideBrief list -> narrative dict shape brief_qc expects.
# ---------------------------------------------------------------------------
def _slidebrief_to_qc_narrative(slides: list[SlideBrief]) -> list[dict]:
    """Convert SlideBrief objects into the per-slide dict shape `check_brief`
    expects (slide_num, governing_thought, so_what, editorial_emphasis, content)."""
    narrative: list[dict] = []
    for s in slides:
        em_text = s.editorial_emphasis or ""
        em_items = [ln.strip(" -*\t") for ln in em_text.splitlines() if ln.strip(" -*\t")]
        if not em_items and em_text.strip():
            em_items = [em_text.strip()]
        content: dict = {}
        if s.evidence:
            content["evidence"] = s.evidence
        if s.content:
            content["body"] = s.content
        if s.not_section:
            content["not"] = s.not_section
        if s.chart_type:
            content["chart_type"] = s.chart_type
        narrative.append({
            "slide_num": s.n,
            "governing_thought": s.governing_thought,
            "so_what": s.so_what,
            "editorial_emphasis": em_items,
            "content": content,
        })
    return narrative


# ---------------------------------------------------------------------------
# Page-type classification (heuristic) + visual directions library
# ---------------------------------------------------------------------------
def classify_page_type(s: SlideBrief) -> str:
    """Return a coarse page-type slug used to pick visual directions."""
    if s.is_cover():
        return "cover"
    if s.is_screenshot_placeholder():
        return "screenshot-placeholder"

    blob = " ".join([s.editorial_emphasis, s.evidence, s.so_what, s.title]).lower()
    chart = (s.chart_type or "").lower()

    # Strong signals first.
    if "the ask dominates" in blob or "one clear cta" in blob or "the ask " in blob:
        return "recommendation-cta"
    if "contrast" in blob and ("two column" in blob or "two outputs" in blob or "side by side" in blob or "mirrored" in blob):
        return "comparison-2-panel"
    if "three column" in blob or "three columns" in blob or "3 column" in blob:
        return "comparison-3-card"
    if "ecosystem" in blob or "coordinated" in blob:
        return "ecosystem-three-state"
    if "compounding forces" in blob or "anchor" in blob and "supporting" in blob:
        return "anchor-with-supporting-cards"
    if "single finding" in blob or "one strong reframe" in blob or "conclusion dominates" in blob:
        return "single-finding"
    if "hero number" in blob or "hero stat" in blob:
        return "hero-number"
    if "waterfall" in chart or "bar" in chart:
        return "data-deep-dive"

    # Data Tables — when the slide IS a table (risk register, scoring matrix,
    # vendor comparison, status-by-workstream, KPI dashboard). Trigger on either
    # explicit table phrasing in the brief, or structural markers (multiple
    # rows of parallel metrics with named columns).
    table_signals = (
        "risk register", "scoring matrix", "decision matrix",
        "vendor comparison", "status by workstream", "kpi dashboard",
        "requirements traceability", "table of", "tabular",
        "rows = ", "rows: ", "rows by",
    )
    if any(sig in blob for sig in table_signals):
        return "data-tables"

    # Sensible default.
    return "single-finding"


# Each direction = a short brief the agent uses to differentiate the three options.
# Three directions per page type so the agent always gets exactly three.
DIRECTIONS: dict[str, list[dict]] = {
    "cover": [
        {
            "name": "Dark full-bleed minimal type",
            "tagline": "Typography is the visual; brand-primary fills the canvas.",
            "core_treatment": "Full-bleed BRAND_PRIMARY fill. Hero title at ~48% canvas height, "
                              "large white type. Tagline directly below in BRAND_ACCENT_SOFT italic. "
                              "Single 64px BRAND_ACCENT rule = the only accent. Faint meta bottom-left.",
        },
        {
            "name": "Light editorial with accent rule",
            "tagline": "White canvas, structured hierarchy, single brand-accent rule.",
            "core_treatment": "White background. Top-left BRAND_PRIMARY eyebrow. Hero title in TEXT_DARK, "
                              "tagline below in BRAND_PRIMARY. Optional supporting triplet (three small "
                              "definition rows derived from the brief's actual deck themes — NEVER reuse "
                              "phrases from this rulebook's examples) left-aligned. One BRAND_ACCENT 56px "
                              "rule above the meta.",
        },
        {
            "name": "Asymmetric split (brand block + content)",
            "tagline": "Brand-primary block on the left, content on the right.",
            "core_treatment": "Left 35% = BRAND_PRIMARY block with WHITE title and BRAND_ACCENT_SOFT tagline. "
                              "Right 65% = white panel with the three sub-tagline definitions stacked, "
                              "meta block at the bottom of the right panel.",
        },
    ],
    "comparison-2-panel": [
        {
            "name": "Symmetric 2-column with vertical divider",
            "tagline": "Equal weight, neutral chrome, single convergence band as the punchline.",
            "core_treatment": "Two equal panels separated by a 1-2px vertical divider in CARD_BORDER. "
                              "Each panel has uppercase TEXT_MID label, TEXT_DARK heading (22px bold), "
                              "TEXT_MID body. Convergence band at y=602 (BRAND_PRIMARY fill, WHITE italic) "
                              "carries the punchline. ONE accent moment = the band.",
        },
        {
            "name": "Mirrored panels with accent-soft on the 'good' side",
            "tagline": "Neutral panel vs accent-tinted panel — the delta IS the argument.",
            "core_treatment": "Left panel: neutral light-gray bg + neutral border + neutral label. "
                              "Right panel: BRAND_ACCENT_SOFT tint bg + accent-tinted border + BRAND_PRIMARY "
                              "label and heading. Equal width, equal height, single convergence band at bottom.",
        },
        {
            "name": "Asymmetric hero + supporting contrast",
            "tagline": "One panel dominates (the answer); the other is shown as foil at reduced weight.",
            "core_treatment": "Right panel = ~60% width, BRAND_PRIMARY fill, WHITE bold heading, large body. "
                              "Left panel = ~40%, white bg, CARD_BORDER 1px outline, smaller TEXT_MID type. "
                              "Title bottom-anchored. Footer page number only.",
        },
    ],
    "comparison-3-card": [
        {
            "name": "Three equal cards with stepped numerals",
            "tagline": "Parallel structure — three cards, one shared accent strip.",
            "core_treatment": "Three CARD_BG cards (CARD_BORDER outline). Each has a large BRAND_PRIMARY "
                              "numeral top-left, 20px bold BRAND_PRIMARY heading, 14px TEXT_DARK body, "
                              "12px italic TEXT_MID meta line bottom. One 3px BRAND_ACCENT left edge per card.",
        },
        {
            "name": "Three columns with shared header band",
            "tagline": "Header band carries the spine; columns share their connection visually.",
            "core_treatment": "Top header band (BRAND_PRIMARY, 64px tall) spans the three columns and carries "
                              "the unifying phrase. Below: three transparent columns separated by 1px dividers. "
                              "Each column has uppercase eyebrow, TEXT_DARK heading, TEXT_MID body bullets.",
        },
        {
            "name": "Three icon-anchored cards",
            "tagline": "Each card is led by a glyph anchor, body sits beneath.",
            "core_treatment": "Three vertical cards. Top of each card = 56px icon block (BRAND_ACCENT_SOFT "
                              "circular bg + BRAND_PRIMARY glyph). Below: TEXT_DARK heading (18px bold), "
                              "TEXT_MID body (14px). Bottom of each card: small italic TEXT_FAINT signature line.",
        },
    ],
    "ecosystem-three-state": [
        {
            "name": "Think / Argue / Build columns with output band",
            "tagline": "Three skill columns up top; a single outputs band ties them.",
            "core_treatment": "Three columns (Think / Argue / Build) each ~380px tall. Column header = "
                              "BRAND_PRIMARY label + tagline; body = bulleted skills (14px, TEXT_DARK). "
                              "Bottom band (BRAND_PRIMARY fill, 64px tall) = 'Outputs' with WHITE italic listing.",
        },
        {
            "name": "Connected nodes flow",
            "tagline": "Three nodes in a left-to-right flow, connected by arrows in BRAND_ACCENT.",
            "core_treatment": "Three circular/oval BRAND_PRIMARY nodes connected with thin BRAND_ACCENT lines. "
                              "Each node has WHITE title centered. Below each node: small panel with TEXT_DARK "
                              "skills listed (14px). Outputs as a single faint line at the bottom.",
        },
        {
            "name": "Stacked three-row ecosystem",
            "tagline": "Vertical stack — each row is a stage with its skills inline.",
            "core_treatment": "Three full-width rows. Each row: left 25% = BRAND_PRIMARY block with WHITE stage "
                              "label; right 75% = white panel with skills as inline pills (BRAND_ACCENT_SOFT bg, "
                              "12px BRAND_PRIMARY type). Faint TEXT_MID rule between rows.",
        },
    ],
    "anchor-with-supporting-cards": [
        {
            "name": "Hero anchor band + 3 supporting cards",
            "tagline": "Big anchor up top, three subordinate cards below as evidence.",
            "core_treatment": "Top anchor band (BRAND_PRIMARY fill, 152px tall) with WHITE 26px bold takeaway "
                              "and BRAND_ACCENT_SOFT eyebrow. Below: three equal CARD_BG cards with 3px "
                              "BRAND_ACCENT left edge, TEXT_DARK heading and TEXT_MID body.",
        },
        {
            "name": "Left anchor panel + right list of forces",
            "tagline": "Anchor occupies the left third; supporting forces stack vertically on the right.",
            "core_treatment": "Left panel (~38% width) = BRAND_PRIMARY fill, WHITE bold takeaway. "
                              "Right panel: three numbered rows, each with TEXT_DARK bold label, "
                              "TEXT_MID body. 1px CARD_BORDER between rows. No additional accents.",
        },
        {
            "name": "Top headline + bottom 3-card row with shared rule",
            "tagline": "Plain bold headline up top; three cards share a single horizontal accent rule.",
            "core_treatment": "Headline alone in body zone (32px bold TEXT_DARK, 60% width). 2px BRAND_ACCENT "
                              "horizontal rule spans below it. Three CARD_BG cards sit beneath that rule, "
                              "each with TEXT_DARK heading and TEXT_MID body. Single accent = the rule.",
        },
    ],
    "single-finding": [
        {
            "name": "Hero takeaway + 3 supporting bullets",
            "tagline": "One bold conclusion as the visual hero; bullets are clearly subordinate.",
            "core_treatment": "Top half = hero takeaway (36px bold TEXT_DARK, 70% width). Below: three TEXT_MID "
                              "supporting bullets with 14px body, each prefixed by a 12px BRAND_PRIMARY square. "
                              "ONE accent moment = a 56px BRAND_ACCENT rule under the takeaway.",
        },
        {
            "name": "Reframe statement + 3 compounding forces",
            "tagline": "Reframe headline on top, three forces below as parallel rows.",
            "core_treatment": "Headline (28px bold TEXT_DARK, full width). Three rows beneath, each row: left "
                              "= BRAND_PRIMARY uppercase label (11px, letter-spaced); right = TEXT_DARK 16px "
                              "claim + TEXT_MID 13px body. Subtle CARD_BORDER divider between rows.",
        },
        {
            "name": "Big quote-style reframe with attribution rule",
            "tagline": "The conclusion reads like a pull-quote — single accent rule on its left.",
            "core_treatment": "Hero headline left-aligned, 40px bold TEXT_DARK, max 8 words per line. To its left, "
                              "a 4px BRAND_ACCENT vertical rule running its full height. Below: three short "
                              "TEXT_MID one-liners (13px) prefixed by BRAND_PRIMARY chevron glyph.",
        },
    ],
    "data-deep-dive": [
        {
            "name": "Chart-dominant + right takeaway panel",
            "tagline": "Chart left (65%), takeaway right (35%) — chart is annotated to prove the headline.",
            "core_treatment": "Left ~62% = python-pptx native bar/waterfall chart (use add_rect bars; "
                              "no PIL). Right ~35% = TEXT_DARK takeaway heading, TEXT_MID body, plus a "
                              "BRAND_ACCENT callout pill ('$3.4M gap'). Chart bars in TEXT_MID, callout bar in "
                              "BRAND_ACCENT — one accent moment.",
        },
        {
            "name": "Full-width chart with inline annotation",
            "tagline": "Chart spans the canvas; a single annotation line points to the key bar.",
            "core_treatment": "Bars span full width (1180px). Annotation line + label sits inline next to the "
                              "key bar (BRAND_ACCENT). Below the chart: 14px TEXT_MID takeaway sentence. "
                              "No legend. One accent moment = the annotated bar.",
        },
        {
            "name": "Hero number + supporting chart strip",
            "tagline": "Big number stat (BRAND_PRIMARY) anchors; small chart strip underneath as evidence.",
            "core_treatment": "Top half = 96px BRAND_PRIMARY hero number, 16px BRAND_PRIMARY label, 18px "
                              "TEXT_DARK supporting claim. Bottom half = thin horizontal bar chart (height "
                              "180px) with TEXT_MID bars + ONE BRAND_ACCENT bar where it matters.",
        },
    ],
    "recommendation-cta": [
        {
            "name": "Hero CTA band + 3 sub-ask cards",
            "tagline": "Primary ask is the visual hero; sub-asks are clearly subordinate.",
            "core_treatment": "Top hero band (152px tall, BRAND_PRIMARY fill) with WHITE 26px bold primary ask "
                              "and BRAND_ACCENT_SOFT eyebrow. 6px BRAND_ACCENT left strip on the hero. Below: "
                              "three CARD_BG cards with 3px BRAND_ACCENT left strip, BRAND_PRIMARY numeral, "
                              "BRAND_PRIMARY heading, TEXT_DARK body, TEXT_MID italic meta. Contact line at bottom.",
        },
        {
            "name": "Single centered CTA with surrounding sub-asks",
            "tagline": "One bold center CTA card; sub-asks sit faintly above and below.",
            "core_treatment": "Center: 60% width BRAND_PRIMARY card, 180px tall, WHITE 28px bold CTA, "
                              "BRAND_ACCENT_SOFT supporting line. Above the card: TEXT_FAINT eyebrow + "
                              "context (16px). Below: three TEXT_MID one-line sub-asks separated by BRAND_ACCENT dots.",
        },
        {
            "name": "Left CTA stack + right contact card",
            "tagline": "Asks listed vertically on the left; right side carries name/email/feedback box.",
            "core_treatment": "Left 60% = primary ask header (BRAND_PRIMARY bold, 28px) + three numbered "
                              "sub-asks (TEXT_DARK 16px). Right 40% = BRAND_PRIMARY card with WHITE contact "
                              "block (name, email, 'feedback skill') + BRAND_ACCENT 4px top rule.",
        },
    ],
    "hero-number": [
        {
            "name": "Centered hero number with supporting line",
            "tagline": "One big number; everything else recedes.",
            "core_treatment": "Centered 144px BRAND_PRIMARY hero number. Above: 11px BRAND_ACCENT eyebrow. "
                              "Below: 22px TEXT_DARK supporting claim, then 14px TEXT_MID context line. "
                              "ONE 56px BRAND_ACCENT rule between number and claim.",
        },
        {
            "name": "Hero number left, narrative right",
            "tagline": "Number anchors the left; story sits to its right.",
            "core_treatment": "Left ~45% = hero number stack (BRAND_PRIMARY 144px, BRAND_ACCENT eyebrow). "
                              "Right ~55% = 22px TEXT_DARK heading, three 14px TEXT_MID body rows. "
                              "Footer page number only.",
        },
        {
            "name": "Hero number with subordinate comparison strip",
            "tagline": "Number on top; small comparison strip underneath says 'vs what'.",
            "core_treatment": "Top half = BRAND_PRIMARY hero number centered (132px) + supporting claim. "
                              "Bottom half = horizontal strip with two micro-stats (each 36px TEXT_DARK number, "
                              "11px TEXT_MID label) separated by 1px CARD_BORDER vertical divider.",
        },
    ],
    "data-tables": [
        {
            "name": "Full-width table with bottom takeaway band",
            "tagline": "Table is the slide; one-sentence takeaway lives in a band below.",
            "core_treatment": "Use add_table(slide, headers=[...], rows=[...]) with mandatory column "
                              "headers in BRAND_PRIMARY band + WHITE text, banded rows for legibility, "
                              "right-aligned numeric columns. Below the table: BRAND_PRIMARY full-width "
                              "band 42px tall with WHITE italic takeaway sentence (use add_convergence). "
                              "ONE column or ONE row highlighted with BRAND_ACCENT (the accent moment).",
        },
        {
            "name": "Table with right-hand takeaway panel",
            "tagline": "Table occupies left 70%; right 30% holds the takeaway and one supporting number.",
            "core_treatment": "Left ~70% = add_table with headers + banded rows. Right ~30% = "
                              "BRAND_PRIMARY card with WHITE 22px takeaway sentence + one supporting "
                              "hero number (48px WHITE bold). ONE column in the table highlighted with "
                              "BRAND_ACCENT to link visually to the right-panel takeaway.",
        },
        {
            "name": "Two stacked mini-tables with shared header",
            "tagline": "Two related tables on the same slide, sharing column meaning.",
            "core_treatment": "Top table = first dataset (header + 3-4 rows). Bottom table = second "
                              "dataset (header + 3-4 rows), aligned column-by-column with the top. "
                              "Use add_table for both. ONE row in the bottom table accented with "
                              "BRAND_ACCENT (the load-bearing row).",
        },
    ],
    "screenshot-placeholder": [
        {
            "name": "Full-bleed screenshot with label band",
            "tagline": "Screenshot fills the body; small label band underneath.",
            "core_treatment": "Body zone (y=156 to y=580) = CARD_BG rectangle with CARD_BORDER outline as the "
                              "screenshot placeholder. TEXT_FAINT 'SCREENSHOT PLACEHOLDER' centered inside. "
                              "Below: BRAND_PRIMARY 16px bold label + TEXT_MID 13px italic caption.",
        },
        {
            "name": "Screenshot left, caption stack right",
            "tagline": "Screenshot occupies 65% on the left; caption + bullets on the right 35%.",
            "core_treatment": "Left 65% = CARD_BG screenshot placeholder rectangle with CARD_BORDER outline. "
                              "Right 35% = BRAND_PRIMARY 20px bold label, TEXT_DARK 14px caption, "
                              "TEXT_MID 13px bullet list of what to look for.",
        },
        {
            "name": "Framed screenshot with caption ribbon",
            "tagline": "Browser-frame style chrome around the screenshot; ribbon caption beneath.",
            "core_treatment": "Top: 16px BRAND_PRIMARY 'browser chrome bar' rect across the screenshot area. "
                              "Main: CARD_BG rectangle with CARD_BORDER outline (the screenshot). Bottom: "
                              "BRAND_PRIMARY ribbon (40px tall, WHITE bold label) flush with the bottom of the image.",
        },
    ],
}


def directions_for(page_type: str) -> list[dict]:
    return DIRECTIONS.get(page_type, DIRECTIONS["single-finding"])


# ---------------------------------------------------------------------------
# Reference exemplar picker
# ---------------------------------------------------------------------------
# Maps the classifier's page-type slugs to one or two exemplars from
# exemplars/do/<slug>/. Chart page-types get BOTH chart exemplars so the agent
# sees the bottom-band variant and the right-card variant together. Keep ≤2 per
# page-type to avoid prompt bloat.
PAGE_TYPE_TO_EXEMPLAR: dict[str, list[str]] = {
    "cover": ["cover-fullbleed-dark", "dark-hero-foil", "cover", "hero-numeral-divider"],
    "comparison-2-panel": ["2panel-convergence", "2panel-delta-spine"],
    "comparison-3-card": ["3pillar-icon-circles", "dark-header-cards", "three-column-vanilla", "three-col-progressive"],
    "ecosystem-three-state": ["3pillar-icon-circles"],
    "anchor-with-supporting-cards": ["anchor-with-cards", "anchor-with-cards-4"],
    "single-finding": [],  # Old single-finding deleted (spacing + accent issues). Needs a clean hero-takeaway-with-bullets replacement; single-finding-v2 is a hero-metric variant, lives under hero-number instead.
    "data-deep-dive": ["chart-bottom-takeaway", "chart-right-takeaway"],
    "recommendation-cta": ["recommendation-cta"],
    "hero-number": ["hero-kpi-tile", "single-finding-v2"],
    "screenshot-placeholder": [],  # Was pointing at single-finding which is removed. Replacement needed.
    "data-tables": [],  # Exemplars to be promoted from _staging/data-tables/ in batch D.
}

# One-line descriptions surfaced alongside each exemplar path in the prompt.
EXEMPLAR_DESCRIPTIONS: dict[str, str] = {
    "cover-fullbleed-dark": "Full-bleed BRAND_PRIMARY cover; typography IS the visual; one accent rule under the tagline.",
    "dark-hero-foil": "Asymmetric cover: 35% dark left block + 65% white right panel with stacked definitions and meta.",
    "anchor-with-cards": "Left BRAND_PRIMARY anchor panel + right column of numbered evidence rows; 4px accent on the panel seam.",
    "2panel-convergence": "Symmetric two-column comparison with hairline divider + BRAND_PRIMARY convergence band as the punchline.",
    "3pillar-icon-circles": "Three parallel cards led by BRAND_PRIMARY circle icon containers (same color, WHITE glyph, MECE rule).",
    "single-finding": "36px bold hero takeaway + 3 subordinate bullets + one 56px BRAND_ACCENT rule.",
    "hero-kpi-tile": "96px BRAND_PRIMARY hero number anchors the top; compact 3-row bar strip proves it (accent on the one load-bearing bar).",
    "recommendation-cta": "Top hero ASK band + 3 sub-ask cards; accent extends from 6px hero strip to 3px card strips (one moment, not four).",
    "chart-bottom-takeaway": "Grouped multi-series bars + full-width BRAND_PRIMARY takeaway band below; callout pill on chart = single accent.",
    "chart-right-takeaway": "Same chart as sibling, but takeaway moves to a right-hand card (sibling-box 2-column grid; accent pill INSIDE the card).",
}


def exemplar_paths_for(page_type: str) -> list[tuple[Path, str]]:
    """Return [(path, one-line description)] for the exemplars assigned to a
    page-type. Falls back to `single-finding` if no mapping exists. Limited to
    2 entries to keep prompt size bounded."""
    slugs = PAGE_TYPE_TO_EXEMPLAR.get(page_type, ["single-finding"])
    found: list[tuple[Path, str]] = []
    for slug in slugs:
        p = EXEMPLARS_ROOT / slug / "exemplar.py"
        if p.exists():
            found.append((p, EXEMPLAR_DESCRIPTIONS.get(slug, "")))
    # Fallback if nothing matched on disk.
    if not found:
        fallback = EXEMPLARS_ROOT / "single-finding" / "exemplar.py"
        if fallback.exists():
            found.append((fallback, EXEMPLAR_DESCRIPTIONS.get("single-finding", "")))
    return found[:2]


# ---------------------------------------------------------------------------
# Per-slide prompt assembly
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """# Slide {n} build prompt — `{title_clean}`

You are building **slide {n}** of a 10-slide deck using **Path C** (custom
python-pptx + Slide Lab helpers). Produce **three structurally distinct
options** as standalone runnable Python scripts.

---

## 1. Brief content (only this slide)

**Slide title:** {title}

**Page type (heuristic):** `{page_type}`

**Governing thought (the claim):**
{governing_thought}

**So-what (the takeaway):**
{so_what}

**Editorial emphasis:**
{editorial_emphasis}

**Evidence / content:**
{evidence}

{cover_content_block}

**What this slide is NOT:**
{not_section}

**Chart type:** {chart_type}

---

## 2. The three visual directions you must implement

Each option must be structurally distinct from the other two (different layout
family, different focal point — not just colour swaps).

### Option A — {a_name}
*{a_tagline}*

{a_treatment}

### Option B — {b_name}
*{b_tagline}*

{b_treatment}

### Option C — {c_name}
*{c_tagline}*

{c_treatment}

---

## 3. DESIGNER BRIEF — read carefully and follow every rule

The following rulebook is the load-bearing reference for this build. Every rule
below is enforced. Read it before you write any code; refer back to specific
sections when uncertain.

<<<DESIGNER_BRIEF_START>>>
{designer_brief}
<<<DESIGNER_BRIEF_END>>>

---

## 4. Required tooling — helpers

**Helpers (the only API you should use to draw shapes):**
- `{helpers_path}`

Import what you need from `twins.helpers`:
```python
from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    add_chrome, add_convergence, add_source, add_footnote,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
)
```

**Reference exemplars (study these closely before writing — these are the
canonical "do" examples for this page-type. Read each `exemplar.py`, then
the sibling `WHY.md` in the same folder for the rationale. Inspect
`exemplar.png` if you can):**
{example_block}

**Deeper-reading only (do NOT rely on these — the inlined DESIGNER BRIEF above
is authoritative; open these files only for an edge case the brief doesn't
cover):**
{rulebook_block}
- `{qc_skill}` — slide-qc sections 5b + 5c (categorical visual checks, cross-slide consistency)

---

## 5. Hard constraints — non-negotiable (recap of the most-broken rules)

- **Title bottom-anchor at y≈100.** Use `add_title_block(slide, title=..., subtitle=...)`. The helper handles the anchor. Do NOT place a raw title shape at y=40.
- **Brand palette only.** Use the named constants (`BRAND_PRIMARY`, `BRAND_ACCENT`, `TEXT_DARK`, `TEXT_MID`, `TEXT_FAINT`, `CARD_BG`, `CARD_BORDER`, `WHITE`, `BRAND_ACCENT_SOFT`). **No raw hex literals** except for one-off neutral panel tints clearly named at the top of the file.
- **Footer chrome only.** `add_footer(slide, page_num={n})`. No "DRAFT", no "CONFIDENTIAL", no client-name tags, no signature lines.
- **Body font floor = 14px.** Pass `font_size_px=14` minimum on body text. Eyebrows can be 11px, meta lines 12px italic, but body claims must be ≥14px.
- **One accent moment per slide.** BRAND_ACCENT is reserved for exactly one element that the takeaway hinges on. Everything else uses BRAND_PRIMARY / neutral tones.
- **1280×720 canvas.** `new_slide()` already gives you this. Do not change page size.
- **Invariant zones.** Top 0-50px and bottom 670-720px hold ONLY page number / source / footnote. No tagline, no client name, no AC logo.
- **No placeholder leaks.** Use blank layout via `new_slide()` (already does this). Do not add `add_slide(prs.slide_layouts[0])` yourself.
- **No external assets.** No PIL, no PNG embedding, no chart image generation. Bars/waterfalls are drawn with `add_rect` + `add_text`. Icons are unicode glyphs via `add_icon` or omitted.

---

## 6. Output spec — exactly what to write

Write **three files** in this directory (`{slide_dir}`):

- `option_A.py`
- `option_B.py`
- `option_C.py`

Each file must:
1. Open with a docstring (5-20 lines) citing the specific rulebook sections honored.
2. Insert this `sys.path` block so `twins.helpers` resolves regardless of cwd:
   ```python
   from pathlib import Path
   import sys
   sys.path.insert(0, r"{skill_root}")
   from twins.helpers import (...)
   ```
3. Define a `build()` function that returns `prs`.
4. End with:
   ```python
   if __name__ == "__main__":
       out = Path(__file__).resolve().parent / "option_X.pptx"  # match this file's letter
       prs = build()
       prs.save(str(out))
       print(f"Wrote: {{out}}")
   ```
5. Run cleanly with `python option_X.py` from any cwd — no manual env setup, no
   missing imports, no relative paths.

**Do NOT graft to the client template.** A separate finalizer script handles
graft + theme remap + render. Your job is the Slide-Lab-palette PPTX only.

**Do NOT render PNGs.** The finalizer does that too.

---

## 7. Self-check before you finish

Run through this list mentally on each option:
- [ ] Title bottom-anchored at y≈100 (using `add_title_block`)?
- [ ] Footer = `add_footer(slide, page_num={n})` only?
- [ ] One accent moment (BRAND_ACCENT used once)?
- [ ] All body text ≥14px?
- [ ] No raw hex colors outside the named-constants set?
- [ ] Three options are structurally distinct (different layout family)?
- [ ] Each `.py` runs standalone (no missing imports, no relative paths)?
- [ ] `option_X.pptx` lands in the same directory as the script?

Begin.
"""


def render_per_slide_prompt(s: SlideBrief, page_type: str, out_dir: Path, designer_brief: str) -> str:
    dirs = directions_for(page_type)
    exemplars = exemplar_paths_for(page_type)

    rulebook_block = "\n".join(f"- `{p}`" for p in RULEBOOK_FILES)
    if exemplars:
        example_block = "\n".join(
            f"- `{p}` — {desc}" if desc else f"- `{p}`"
            for p, desc in exemplars
        )
    else:
        example_block = "- (no exemplars found — design from rulebook alone)"

    cover_content_block = ""
    if s.content and not s.evidence:
        cover_content_block = f"**Content (cover/screenshot — no evidence section):**\n{s.content}\n"

    slide_dir = out_dir / f"slide_{s.n:02d}"

    return PROMPT_TEMPLATE.format(
        n=s.n,
        title=s.title,
        title_clean=s.title.replace("`", ""),
        page_type=page_type,
        governing_thought=s.governing_thought or "(none — see content section)",
        so_what=s.so_what or "(see editorial emphasis)",
        editorial_emphasis=s.editorial_emphasis or "(none)",
        evidence=s.evidence or "(none)",
        cover_content_block=cover_content_block,
        not_section=s.not_section or "(none)",
        chart_type=s.chart_type or "none",
        a_name=dirs[0]["name"],
        a_tagline=dirs[0]["tagline"],
        a_treatment=dirs[0]["core_treatment"],
        b_name=dirs[1]["name"],
        b_tagline=dirs[1]["tagline"],
        b_treatment=dirs[1]["core_treatment"],
        c_name=dirs[2]["name"],
        c_tagline=dirs[2]["tagline"],
        c_treatment=dirs[2]["core_treatment"],
        helpers_path=HELPERS_PATH,
        rulebook_block=rulebook_block,
        qc_skill=QC_SKILL,
        example_block=example_block,
        slide_dir=slide_dir,
        skill_root=SKILL_ROOT,
        designer_brief=designer_brief,
    )


# ---------------------------------------------------------------------------
# Dispatch plan
# ---------------------------------------------------------------------------
DISPATCH_TEMPLATE = """# Slide Lab dispatch plan

Generated: {ts}

Brief: `{brief}`
Template: `{template}`
Out: `{out}`

## Deck-level metadata

- Deck type: {deck_type}
- Narrative framework: {narrative_framework}
- Governing thought: {governing_thought}

## Per-slide plan

| Slide | Title | Page type | Prompt |
|-------|-------|-----------|--------|
{slide_rows}

## Next step — dispatch parallel agents

Run **{n_slides} parallel `general-purpose` Task calls** in a single response.
Each call uses the contents of that slide's `_prompt.md` as the prompt body.

Each agent will write three files into its slide directory:
`option_A.py`, `option_B.py`, `option_C.py`.

After all agents return, run the finalizer:

```bash
python "{finalizer}" --out "{out}" --template "{template}"
```

The finalizer:
1. Executes each `option_X.py` to produce `option_X.pptx`.
2. Grafts each PPTX onto the client template + applies the theme remap.
3. Renders each themed PPTX to PNG (parallel x4).
4. Writes `<out>/RESULT.md` with per-slide status.

## Prompt file index (absolute paths)

{prompt_index}
"""


def write_dispatch_plan(
    out_dir: Path,
    slides: list[SlideBrief],
    page_types: dict[int, str],
    brief_path: Path,
    template_path: Path,
    deck_meta: dict,
) -> Path:
    rows = []
    prompt_index = []
    for s in slides:
        prompt_path = out_dir / f"slide_{s.n:02d}" / "_prompt.md"
        rows.append(
            f"| {s.n} | {s.title} | `{page_types[s.n]}` | `slide_{s.n:02d}/_prompt.md` |"
        )
        prompt_index.append(f"- Slide {s.n:>2}: `{prompt_path}`")

    finalizer = SKILL_ROOT / "scripts" / "finalize_deck.py"

    content = DISPATCH_TEMPLATE.format(
        ts=datetime.now().isoformat(timespec="seconds"),
        brief=brief_path,
        template=template_path,
        out=out_dir,
        deck_type=deck_meta.get("deck_type", "(not parsed)"),
        narrative_framework=deck_meta.get("narrative_framework", "(not parsed)"),
        governing_thought=deck_meta.get("governing_thought", "(not parsed)"),
        n_slides=len(slides),
        slide_rows="\n".join(rows),
        prompt_index="\n".join(prompt_index),
        finalizer=finalizer,
    )

    target = out_dir / "dispatch_plan.md"
    target.write_text(content, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Slide Lab deck orchestrator — Part A (prep prompts)")
    ap.add_argument("--brief", required=True, type=Path, help="Narrative brief .md")
    ap.add_argument("--template", required=True, type=Path, help="Client PPTX template")
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    ap.add_argument("--slides", type=int, default=None, help="Limit to first N slides")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    if not args.brief.exists():
        print(f"ERROR: brief not found: {args.brief}")
        return 2
    if not args.template.exists():
        print(f"ERROR: template not found: {args.template}")
        return 2

    args.out.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(f"Slide Lab deck orchestrator — Part A")
    print(f"  brief    : {args.brief}")
    print(f"  template : {args.template}")
    print(f"  out      : {args.out}")
    print("=" * 72)

    print("\n[1] Parse brief")
    slides, deck_meta = parse_brief(args.brief)
    print(f"  parsed {len(slides)} slides")
    for s in slides:
        print(f"    slide {s.n:>2}: {s.title[:60]}")

    if args.slides is not None:
        slides = slides[: args.slides]
        print(f"  limited to first {args.slides}")

    print("\n[1.4] Brief-time QC pass")
    qc_narrative = _slidebrief_to_qc_narrative(slides)
    try:
        qc_result = check_brief(qc_narrative)
    except Exception as exc:
        print(f"  WARNING: brief-QC raised {type(exc).__name__}: {exc}")
        qc_result = {"blocking": [], "warnings": [], "summary": f"brief-QC failed: {exc}"}
    qc_blocking = list(qc_result.get("blocking") or [])
    qc_warnings = list(qc_result.get("warnings") or [])
    print(f"  {qc_result.get('summary') or 'no summary'}")
    if qc_blocking:
        print(f"  --- BLOCKING ({len(qc_blocking)}) ---")
        for line in qc_blocking:
            print(f"    [BLOCK] {line}")
    if qc_warnings:
        print(f"  --- WARNINGS ({len(qc_warnings)}) ---")
        for line in qc_warnings[:20]:
            print(f"    [warn]  {line}")
        if len(qc_warnings) > 20:
            print(f"    ... and {len(qc_warnings) - 20} more")
    qc_path = args.out / "brief_qc.json"
    qc_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "brief": str(args.brief),
        "slide_count": len(slides),
        "summary": qc_result.get("summary", ""),
        "blocking": qc_blocking,
        "warnings": qc_warnings,
    }
    qc_path.write_text(json.dumps(qc_payload, indent=2), encoding="utf-8")
    print(f"  wrote {qc_path}")
    if qc_blocking:
        print(f"  NOTE: {len(qc_blocking)} blocking issue(s) found - not halting (brief QC is advisory).")

    print("\n[1.5] Load inlined designer brief")
    if not DESIGNER_BRIEF_PATH.exists():
        print(f"ERROR: designer brief not found at {DESIGNER_BRIEF_PATH}")
        return 2
    designer_brief = DESIGNER_BRIEF_PATH.read_text(encoding="utf-8")
    print(f"  loaded {DESIGNER_BRIEF_PATH.name} ({len(designer_brief):,} chars)")

    print("\n[2] Classify page types + assemble per-slide prompts")
    page_types: dict[int, str] = {}
    for s in slides:
        page_type = classify_page_type(s)
        page_types[s.n] = page_type
        slide_dir = args.out / f"slide_{s.n:02d}"
        slide_dir.mkdir(parents=True, exist_ok=True)
        prompt = render_per_slide_prompt(s, page_type, args.out, designer_brief)
        (slide_dir / "_prompt.md").write_text(prompt, encoding="utf-8")
        print(f"  slide {s.n:>2}: page_type={page_type:30s} -> {slide_dir / '_prompt.md'}")

    print("\n[3] Write dispatch_plan.md")
    plan = write_dispatch_plan(args.out, slides, page_types, args.brief, args.template, deck_meta)
    print(f"  {plan}")

    print("\n[4] Write _meta.json")
    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "brief": str(args.brief),
        "template": str(args.template),
        "out": str(args.out),
        "slide_count": len(slides),
        "deck_meta": deck_meta,
        "brief_qc": {
            "blocking_count": len(qc_blocking),
            "warning_count": len(qc_warnings),
            "summary": qc_result.get("summary", ""),
            "path": str(qc_path),
        },
        "slides": [
            {
                "n": s.n,
                "title": s.title,
                "page_type": page_types[s.n],
                "is_cover": s.is_cover(),
                "is_screenshot_placeholder": s.is_screenshot_placeholder(),
                "chart_type": s.chart_type,
            }
            for s in slides
        ],
    }
    (args.out / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  {args.out / '_meta.json'}")

    print("\n" + "=" * 72)
    print("DONE — Part A complete.")
    print(f"  Next: dispatch {len(slides)} parallel general-purpose Task calls")
    print(f"        using each <slide>/_prompt.md as the prompt body.")
    print(f"  Then: python {SKILL_ROOT / 'scripts' / 'finalize_deck.py'} \\")
    print(f"               --out \"{args.out}\" --template \"{args.template}\"")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
