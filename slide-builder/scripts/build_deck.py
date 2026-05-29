#!/usr/bin/env python3
"""
build_deck.py — v2 prep script (slide-builder).

Reads a storyline-helper narrative brief + a client PPTX template, then writes
one self-contained per-slide _prompt.md to <out>/slide_NN/_prompt.md plus a
deck-level dispatch_plan.md summary. The parent session dispatches one worker
agent per slide using those rendered prompts.

Five responsibilities (locked in DECISIONS.md § "What's new for v2"):

  1. Read narrative brief + client template.
  2. Prep-time pattern-hint pass: run the layouts.md signals table once per
     slide to forecast each slide's likely pattern. Forecast is injected as
     adjacency CONTEXT into each prompt, not as a constraint — the agent
     overrides at dispatch time if its brief read differs.
  3. Lock content_hash = md5(governing_thought + so_what + evidence_content).
     Compute 4 seeds per slide:
       pattern_pick_seed = md5(content_hash + slide_n)
       variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)
  4. Per-client Mermaid theme generation: read the client template.json,
     apply the mapping in reference/fallback.md, write
     theme/mermaid-<client_slug>.json. Log which slots used hardcoded fallbacks.
  5. Render prompt.md with all placeholders interpolated.

Usage:
    py -3 build_deck.py \\
        --brief <narrative_brief.md> \\
        --template <client_template.pptx> \\
        --out <output_directory> \\
        [--client-name <override>]

Exit codes:
    0  Success.
    1  Brief file missing, unreadable, or empty.
    2  Brief has no parseable slides.
    3  Client template missing.
    4  prompt.md template missing or malformed.
    5  Output directory cannot be created.
    6  Client theme validation failed — refusing to build slides with wrong colors.
       See validate_theme() and the v1 client_theme loader-bug note in fallback.md.
    7  Stage-1 sanity check failed — prerequisite missing.
       Either the client template is not registered (BrandSidecarMissing — run
       slide-builder/scripts/register_template.py) OR mmdc is not installed
       (npm install -g @mermaid-js/mermaid-cli@11.4.0). Halts at prep time
       before agent dispatch costs are sunk.

Cross-platform note: invoke this script with sys.executable from other scripts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# _meta.json schema version. Canonical source is _meta_schema.py; this
# assignment lands AFTER the import of META_SCHEMA_VERSION_CURRENT (further
# below), so see that block for the lockstep.


# ----------------------------------------------------------------------
# Skill paths — derived from this file's location
# ----------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
PROMPT_TEMPLATE = SKILL_ROOT / "prompt.md"
LAYOUTS_MD = SKILL_ROOT / "reference" / "layouts.md"
ANTI_PATTERNS_MD = SKILL_ROOT / "reference" / "anti-patterns.md"
FALLBACK_MD = SKILL_ROOT / "reference" / "fallback.md"
FALLBACK_EXAMPLES_DIR = SKILL_ROOT / "reference" / "fallback-examples"
SKILL_MD = SKILL_ROOT / "SKILL.md"
THEME_DIR = SKILL_ROOT / "theme"

# twins/ lives inside this skill (re-homed in Phase 2 cleanup 2026-05-26).
# HELPERS_MODULE_PATH retained as the historical name for the prompt-template
# substitution token consumed by per-slide agent scripts, but the path now
# points at SKILL_ROOT — twins/helpers.py is at <SKILL_ROOT>/twins/helpers.py.
HELPERS_MODULE_PATH = SKILL_ROOT

# Make twins.client_theme importable. load_brand_sidecar is the canonical
# source of truth for client brand colors and fonts — it reads <stem>.brand.yml
# (human-authored once via register_template.py) and verifies <stem>.theme.json
# (SHA-stamped audit blob). v2 does NOT walk template.json slot positions any
# more — that path was retired after the prior FedEx smoke surfaced a
# false-positive in which hardcoded defaults coincidentally matched FedEx.
# See _decisions/smoke-test-finding-2026-05-25.md § "Critical correction to
# prior FedEx smoke reporting".
sys.path.insert(0, str(HELPERS_MODULE_PATH))
try:
    from twins.client_theme import load_brand_sidecar, BrandSidecarMissing, BrandSidecarStale  # noqa: E402
except ImportError as _imp_exc:
    sys.stderr.write(
        "ERROR: cannot import twins.client_theme — twins/ should be at "
        f"{SKILL_ROOT / 'twins'}.\n"
        f"  Import error: {_imp_exc}\n"
    )
    raise

import shutil  # noqa: E402
import subprocess  # noqa: E402

import _paths as _p  # noqa: E402
from _meta_schema import MetaJson, META_SCHEMA_VERSION_CURRENT  # noqa: E402
from _chrome_schema import (  # noqa: E402
    ChromeSidecarMissingError, load_chrome_yml,
)

# Re-export under the historical name for clarity at the writer site (line
# ~970 in write_meta_json). The single canonical source is _meta_schema.py.
META_SCHEMA_VERSION = META_SCHEMA_VERSION_CURRENT


# ----------------------------------------------------------------------
# Brief parsing
# ----------------------------------------------------------------------

YAML_FENCE_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# Slide header regex. Accepts BOTH:
#   `### Slide 1 — Title text`   (title-on-header — preferred, used by post-2026-05-26 briefs)
#   `### Slide 1`                (title-less header — storyline-helper's older documented format)
# When title is missing on the header line, parse_brief falls back to the
# `**Slide title:**` body field, then to a synthetic "Slide N" placeholder.
# H2 (##) and H3 (###) both supported. The (\d+) clause gates on the digit.
SLIDE_HEADER_RE = re.compile(r"^#{2,3}\s+Slide\s+(\d+)\s*(?:[—\-:]\s*(.+?)\s*)?$", re.MULTILINE)
# Critical fix #2: lookahead must terminate on any H1-H3 boundary, not only H2.
# Briefs with `### Appendix A — ...` after deck notes were silently swallowing
# the appendix into the deck-notes capture. `^#{1,3}\s` covers H1/H2/H3.
DECK_NOTES_RE = re.compile(
    r"^##\s+Deck[\s\-]?level\s+design\s+notes\s*\n(.*?)(?=^#{1,3}\s|\Z)",
    re.MULTILINE | re.IGNORECASE | re.DOTALL,
)

# Bold-labeled field lines: **Label:** value (one-line)  OR  **Label:**\nblock
FIELD_LABELS = {
    "title":               ("slide title",),
    "archetype":           ("archetype",),
    "layout":              ("layout",),  # v0.2 P1.4
    "variant":             ("variant",),  # v0.3: "dark" triggers dark-background variant
    "governing_thought":   ("governing thought", "governing thought (the claim)"),
    "so_what":             ("so-what", "so what", "so-what (the takeaway)"),
    "editorial_emphasis":  ("editorial emphasis",),
    "evidence_content":    ("evidence", "evidence / content", "evidence/content", "content"),
    "chart_type":          ("chart type",),
    "not_this_slide":      ("what this slide is not",),
}


# Archetype → page_type normalization. storyline-helper produces brief slides
# with **Archetype:** values from a documented enum; downstream readers (QC,
# build_review) reason about a coarser `page_type` token. This map closes the
# gap so the brief author doesn't have to think about both.
ARCHETYPE_TO_PAGE_TYPE: dict[str, str] = {
    "cover / title":             "cover",
    "cover":                     "cover",
    "title":                     "cover",
    "executive summary":         "executive-summary",
    "context / situation":       "context",
    "approach / methodology":    "approach",
    "analytical":                "analysis",
    "framework / conceptual":    "framework",
    "synthesis / findings":      "headline-finding",
    "recommendation":            "recommendation",
    "roadmap / implementation":  "roadmap",
    "risk":                      "risk",
    "financial / business case": "financial",
    "decision / ask":            "decision",
    "appendix":                  "appendix",
}


def _normalize_archetype_to_page_type(archetype: str) -> str:
    """Map a brief Archetype label to the coarser page_type token."""
    if not archetype:
        return ""
    return ARCHETYPE_TO_PAGE_TYPE.get(archetype.strip().lower(), "")


def parse_yaml_simple(yaml_text: str) -> dict[str, str]:
    """Tiny YAML reader — handles flat 'key: value' pairs only. The brief's
    front-matter is shallow by convention (client_template, deck_type, etc.)
    so we avoid the PyYAML dependency."""
    out: dict[str, str] = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip("'\"")
    return out


def extract_front_matter(brief_text: str) -> tuple[dict[str, str], str]:
    """Return (front_matter_dict, body_without_front_matter)."""
    match = YAML_FENCE_RE.match(brief_text)
    if not match:
        return {}, brief_text
    return parse_yaml_simple(match.group(1)), brief_text[match.end():]


def extract_deck_notes(body: str) -> str:
    """Extract the '## Deck-level design notes' section if present."""
    match = DECK_NOTES_RE.search(body)
    if not match:
        return ""
    return match.group(1).strip()


def split_slide_blocks(body: str) -> list[tuple[int, str, str]]:
    """Split body into (slide_n, title, block_text) tuples.

    A slide block runs from one '## Slide N — title' header to the next
    (or to end-of-file). The block_text includes the body content beneath
    the header.
    """
    matches = list(SLIDE_HEADER_RE.finditer(body))
    blocks: list[tuple[int, str, str]] = []
    for i, m in enumerate(matches):
        slide_n = int(m.group(1))
        # m.group(2) is None when the header is title-less ("### Slide 1"
        # without an em-dash + title). parse_brief falls back to the
        # **Slide title:** body field in that case.
        title = (m.group(2) or "").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[start:end].strip()
        blocks.append((slide_n, title, block))
    return blocks


def extract_field(block: str, labels: tuple[str, ...]) -> str:
    """Extract a bold-labeled field from a slide block.

    Matches either:
        **Label:** inline value\n
        **Label:**\n
        value paragraph (may span multiple lines until the next **Label:** or blank-then-bold)

    Case-insensitive on the label. Returns empty string if not found.
    """
    for label in labels:
        pattern = re.compile(
            rf"\*\*{re.escape(label)}\s*:?\s*\*\*\s*(.*?)(?=\n\s*\*\*[A-Za-z]|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(block)
        if match:
            return match.group(1).strip()
    return ""


def parse_brief(brief_path: Path) -> dict[str, Any]:
    """Parse the storyline-helper narrative brief.

    Returns:
        {
            "front_matter": {...},
            "deck_notes":   "...",
            "slides":       [{slide_n, title, governing_thought, so_what,
                              editorial_emphasis, evidence_content, chart_type,
                              not_this_slide}, ...],
            "slide_total":  N,
        }
    """
    if not brief_path.exists():
        sys.stderr.write(f"ERROR: brief file does not exist: {brief_path}\n")
        sys.exit(1)
    text = brief_path.read_text(encoding="utf-8")
    if not text.strip():
        sys.stderr.write(f"ERROR: brief file is empty: {brief_path}\n")
        sys.exit(1)

    front_matter, body = extract_front_matter(text)
    deck_notes = extract_deck_notes(body)
    blocks = split_slide_blocks(body)
    if not blocks:
        sys.stderr.write(
            f"ERROR: no parseable slides found in brief. Expected '## Slide N — title' "
            f"headers. Brief: {brief_path}\n"
        )
        sys.exit(2)

    slides: list[dict[str, Any]] = []
    for slide_n, title, block in blocks:
        slide = {
            "slide_n": slide_n,
            # Title resolution order: (1) header line `### Slide N — Title`;
            # (2) **Slide title:** body field; (3) synthetic `Slide N` so
            # downstream readers (REVIEW.html topbar, dispatch_plan rows)
            # always have a non-empty label. The first two paths are
            # author-controlled; the third is a safety net so a title-less
            # storyline-helper brief still builds.
            "title": (title or extract_field(block, FIELD_LABELS["title"])
                      or f"Slide {slide_n}"),
            "archetype": extract_field(block, FIELD_LABELS["archetype"]),
            "layout": extract_field(block, FIELD_LABELS["layout"]),  # v0.2 P1.4
            "variant": (extract_field(block, FIELD_LABELS["variant"]) or "").strip().lower(),  # v0.3
            "governing_thought": extract_field(block, FIELD_LABELS["governing_thought"]),
            "so_what": extract_field(block, FIELD_LABELS["so_what"]),
            "editorial_emphasis": extract_field(block, FIELD_LABELS["editorial_emphasis"]),
            "evidence_content": extract_field(block, FIELD_LABELS["evidence_content"]),
            "chart_type": (extract_field(block, FIELD_LABELS["chart_type"]) or "none").lower(),
            "not_this_slide": extract_field(block, FIELD_LABELS["not_this_slide"]),
        }
        slides.append(slide)

    return {
        "front_matter": front_matter,
        "deck_notes": deck_notes,
        "slides": slides,
        "slide_total": len(slides),
    }


# ----------------------------------------------------------------------
# Pattern-hint pass — keyword-based forecaster
#
# Returns the most likely pattern from layouts.md given the brief signals.
# This is a FORECAST, not a binding pick. The agent overrides at dispatch
# time. The agent's prompt receives this only as adjacency context for
# slides N-1 and N-2 (so the agent can break 3-in-a-row runs).
# ----------------------------------------------------------------------

# Pattern names — must match the canonical names in layouts.md exactly
PATTERNS = {
    "full_canvas":         "Full canvas",
    "fifty_fifty":         "50/50 vertical",
    "asymmetric":          "Asymmetric vertical (75/25)",
    "top_band":            "Top band + body",
    "n_column":            "N-column row (3-9)",
    "vertical_stack":      "Vertical N-row stack",
    "dense_grid":          "Dense grid (2..5 × 2..5)",
    "left_rail":           "Left rail + body",
    "horizontal_bands":    "Horizontal bands",
    "org_chart":           "Org chart (hierarchical)",
    "swimlane":            "Swimlane (cross-functional process)",
    "decision_tree":       "Decision tree (branching)",
    "chart":               "Chart (with quadrant mode)",
    "table":               "Table",
    "fallback":            "FALLBACK (Mermaid or SKELETON_REJECTED)",
}

_COUNT_RE = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|\d+)\b", re.IGNORECASE)
_WORD_TO_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
}


def _extract_item_count(text: str) -> int:
    """Best-effort item-count extraction. Looks for 'N <noun>' patterns like
    '3 pillars', 'two paths', '6 findings'. Returns 0 if none found."""
    item_nouns = (
        "path", "paths", "pillar", "pillars", "phase", "phases",
        "finding", "findings", "option", "options", "step", "steps",
        "principle", "principles", "row", "rows", "column", "columns",
        "tile", "tiles", "card", "cards", "force", "forces",
    )
    pattern = re.compile(
        rf"\b(one|two|three|four|five|six|seven|eight|nine|\d+)\s+"
        rf"({'|'.join(item_nouns)})\b",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return 0
    token = match.group(1).lower()
    if token in _WORD_TO_INT:
        return _WORD_TO_INT[token]
    try:
        return int(token)
    except ValueError:
        return 0


def forecast_pattern(slide: dict[str, Any]) -> str:
    """Heuristic pattern forecaster — keyword-based, no LLM.

    Returns the canonical pattern name from PATTERNS. Used only for
    adjacency context (LIKELY_PRIOR_PATTERNS in the next two slides'
    prompts). The agent has final say at dispatch.
    """
    text = " ".join([
        slide.get("title", ""),
        slide.get("governing_thought", ""),
        slide.get("so_what", ""),
        slide.get("editorial_emphasis", ""),
        slide.get("evidence_content", ""),
    ]).lower()
    chart_type = slide.get("chart_type", "none")

    # Chart object — any non-"none" chart_type wins
    if chart_type and chart_type != "none":
        return PATTERNS["chart"]

    # Diagram primitives
    if any(kw in text for kw in ("org chart", "hierarchy", "reporting line", "capability tree")):
        return PATTERNS["org_chart"]
    if any(kw in text for kw in ("swimlane", "cross-functional", "hand-off", "handoff")):
        return PATTERNS["swimlane"]
    if any(kw in text for kw in ("decision tree", "branching", "if/then", "routing rule")):
        return PATTERNS["decision_tree"]

    # Fallback triggers — agent will refine to FALLBACK_MERMAID vs SKELETON_REJECTED
    fallback_kws = (
        "hub and spoke", "hub-spoke", "hub-and-spoke",
        "porter's five forces", "five forces",
        "fishbone", "ishikawa",
        "ecosystem map", "ecosystem",
        "free-form network", "network diagram",
        "concentric rings", "concentric ring",
    )
    if any(kw in text for kw in fallback_kws):
        return PATTERNS["fallback"]

    # Table
    if "comparison table" in text or "decision matrix" in text or "option scoring" in text:
        return PATTERNS["table"]

    # Visual-weight / comparison signals
    if any(kw in text for kw in ("today vs", "vs.", "before/after", "before and after", "current state", "future state")):
        return PATTERNS["fifty_fifty"]
    if any(kw in text for kw in ("evidence/so-what", "evidence and so-what")):
        return PATTERNS["horizontal_bands"]
    if any(kw in text for kw in ("headline finding", "top band", "headline + cards")):
        return PATTERNS["top_band"]
    if any(kw in text for kw in ("hero metric", "anchor metric", "anchor panel")):
        return PATTERNS["asymmetric"]
    if any(kw in text for kw in ("left rail", "section marker", "navigation chrome")):
        return PATTERNS["left_rail"]

    # Count-based fallbacks
    count = _extract_item_count(text)
    if count >= 7:
        return PATTERNS["dense_grid"]
    if 3 <= count <= 6:
        # Vertical vs horizontal — heuristic on prose vs grid signals
        if any(kw in text for kw in ("list", "principles", "capabilities", "commitments")):
            return PATTERNS["vertical_stack"]
        return PATTERNS["n_column"]
    if count == 2:
        return PATTERNS["fifty_fifty"]

    # Hero / single-statement signals
    if any(kw in text for kw in ("hero claim", "single statement", "dominant statement", "quote", "divider", "cover")):
        return PATTERNS["full_canvas"]

    # Default — full canvas is the safest for under-determined briefs
    return PATTERNS["full_canvas"]


# ----------------------------------------------------------------------
# content_hash + seeds
# ----------------------------------------------------------------------

def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def compute_seeds(slide: dict[str, Any]) -> dict[str, str]:
    """Lock content_hash and compute 4 per-slide seeds.

    Mirrors the canonical formulas in DECISIONS.md § "Variant rotation
    discipline (simplified for v2)".
    """
    content_str = (
        slide.get("governing_thought", "")
        + slide.get("so_what", "")
        + slide.get("evidence_content", "")
    )
    content_hash = _md5(content_str)
    slide_n_str = str(slide["slide_n"])
    return {
        "content_hash":      content_hash,
        "pattern_pick_seed": _md5(content_hash + slide_n_str),
        "variant_seed_a":    _md5(content_hash + slide_n_str + "A"),
        "variant_seed_b":    _md5(content_hash + slide_n_str + "B"),
        "variant_seed_c":    _md5(content_hash + slide_n_str + "C"),
    }


# ----------------------------------------------------------------------
# Client slug + Mermaid theme generation
# ----------------------------------------------------------------------

def slugify(name: str) -> str:
    """Lowercase, hyphen-separated, filename-safe."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "client"


def detect_client_slug(template_path: Path, override: str | None) -> str:
    """Derive a client slug from CLI override or the template filename.

    Examples:
        template = .../FedEx/_templates/Template2.pptx  →  "fedex"
        template = .../ACME Project/template.pptx        →  "acme-project"
    """
    if override:
        return slugify(override)
    # Walk up to find a meaningful directory name (skip generic _templates, etc.)
    for parent in template_path.resolve().parents:
        name = parent.name
        if name and not name.startswith("_") and name.lower() not in ("templates", "claude projects", "documents"):
            return slugify(name)
    # Fall back to template filename stem
    return slugify(template_path.stem)


def _compute_theme_variables(brand: dict) -> dict[str, str]:
    """Map v1's brand-sidecar fields to Mermaid themeVariables.

    `brand` is the dict returned by `twins.client_theme.load_brand_sidecar()`.
    Hexes in the dict are 6-char UPPERCASE WITHOUT '#' prefix; we prepend.

    Brand-driven fields (sourced from brand.yml):
      primary_hex   -> primaryColor, primaryBorderColor, lineColor,
                       nodeBorder, defaultLinkColor              (5 vars)
      accent_hex    -> secondaryColor, secondaryBorderColor      (2 vars)
      font_heading  -> fontFamily (composed with font_body + fallback stack)
      font_body     -> fontFamily

    Universal neutrals (NOT brand-specific; same hex across all clients):
      primaryTextColor, secondaryTextColor    (white-on-dark text)
      tertiaryTextColor, titleColor, textColor (dark-on-light text)
      tertiaryColor, tertiaryBorderColor       (neutral grays)
      background, mainBkg, secondBkg, clusterBkg, clusterBorder
      edgeLabelBackground, fontSize

    NO slot-position guessing. NO walking template.json["extracted"]["all_colors"].
    Brand source is brand.yml only; that's the v1-canonical contract.
    """
    def _hex(field: str) -> str:
        # Production-grade bar: NO silent fallback. Prior FedEx smoke's
        # "purple/orange correct" was a false-positive — hardcoded FedEx-shaped
        # defaults coincidentally matched. Fail loudly so the operator
        # re-registers the template instead of shipping wrong colors.
        raw = brand.get(field, "")
        v = (raw or "").strip().upper()
        if not v:
            raise ValueError(
                f"brand.{field} missing or empty. "
                f"Re-register the template (scripts/register_template.py propose → commit)."
            )
        if not re.fullmatch(r"[0-9A-F]{6}", v):
            raise ValueError(
                f"brand.{field} malformed: {raw!r}. "
                f"Expected 6-char hex (no leading '#'). "
                f"Re-register the template (scripts/register_template.py propose → commit)."
            )
        return f"#{v}"

    primary = _hex("primary_hex")
    accent  = _hex("accent_hex")

    font_heading = (brand.get("font_heading", "") or "").strip()
    font_body    = (brand.get("font_body", "") or "").strip()
    family_parts: list[str] = []
    if font_body:
        family_parts.append(f'"{font_body}"')
    if font_heading and font_heading != font_body:
        family_parts.append(f'"{font_heading}"')
    family_parts.extend(["Helvetica", "Arial", "sans-serif"])
    font_family = ", ".join(family_parts)

    return {
        # Brand-driven primary (5 vars from brand.primary_hex)
        "primaryColor":         primary,
        "primaryBorderColor":   primary,
        "lineColor":             primary,
        "nodeBorder":            primary,
        "defaultLinkColor":      primary,
        # Brand-driven accent (2 vars from brand.accent_hex)
        "secondaryColor":        accent,
        "secondaryBorderColor":  accent,
        # Universal text-on-fill (white on dark brand, dark on light)
        "primaryTextColor":      "#FFFFFF",
        "secondaryTextColor":    "#FFFFFF",
        "tertiaryTextColor":     "#1A1A1A",
        "titleColor":            "#1A1A1A",
        "textColor":             "#1A1A1A",
        # Universal neutrals (no slot-position guessing)
        "tertiaryColor":         "#F2F2F2",
        "tertiaryBorderColor":   "#E3E3E3",
        "background":            "#FFFFFF",
        "mainBkg":               "#FAFAFA",
        "secondBkg":             "#F2F2F2",
        "clusterBkg":            "#FAFAFA",
        "clusterBorder":         "#E3E3E3",
        "edgeLabelBackground":   "#FFFFFF",
        # Brand-driven font + fixed size
        "fontFamily":            font_family,
        "fontSize":              "16px",
    }


def generate_mermaid_theme(client_slug: str, brand: dict) -> tuple[Path, list[str]]:
    """Write theme/mermaid-<slug>.json from v1's brand-sidecar dict.

    `brand` is the dict from `twins.client_theme.load_brand_sidecar()`.

    Returns (theme_file_path, slots_using_fallback). slots_using_fallback
    lists any brand fields that fell back to default values (e.g., missing
    fonts → Helvetica stack). It does NOT cover universal-neutral fields,
    which are hardcoded by design (no slot-position guessing).
    """
    THEME_DIR.mkdir(parents=True, exist_ok=True)
    out_path = THEME_DIR / f"mermaid-{client_slug}.json"

    theme_variables = _compute_theme_variables(brand)
    slots_using_fallback: list[str] = []
    if not (brand.get("primary_hex") or "").strip():
        slots_using_fallback.append("primary_hex missing in brand.yml → primaryColor fell back")
    if not (brand.get("accent_hex") or "").strip():
        slots_using_fallback.append("accent_hex missing in brand.yml → secondaryColor fell back")
    if not (brand.get("font_body") or "").strip() and not (brand.get("font_heading") or "").strip():
        slots_using_fallback.append("font_body + font_heading both missing → fontFamily fell back to Helvetica stack")

    config = {
        "_comment_generated_by":   "scripts/build_deck.py",
        "_comment_client_slug":    client_slug,
        "_comment_brand_source":   "brand.yml via twins.client_theme.load_brand_sidecar (v1 canonical)",
        "_comment_fallbacks_used": slots_using_fallback,
        "theme": "base",
        "themeVariables": theme_variables,
        "flowchart": {
            "curve": "basis",
            "padding": 20,
            "nodeSpacing": 50,
            "rankSpacing": 60,
            "useMaxWidth": False,
        },
    }
    out_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return out_path, slots_using_fallback


# ----------------------------------------------------------------------
# Theme sanity-check — structural belt-and-braces on the brand.yml-derived
# theme. Brand source is human-authored via slide-builder/scripts/register_template.py
# (Phase 3 interactive color confirmation), so the slot-position-guessing
# class of failures is gone by construction. These checks defend against
# brand.yml authoring errors (typo'd hexes, same color in both slots).
#
# Three checks:
#   1. primary and accent both loaded.
#   1b. primary != accent.
#   2. Plausible saturation / luminance for each (not pure black/white,
#      not near-grey).
#   3. Template path → expected color family for known clients (optional;
#      warning-only when client unknown).
# ----------------------------------------------------------------------

# Hue ranges (degrees, 0-360) for known clients' brand primaries.
# Extend as new clients are validated against real templates.
# Hue conventions: red ~0, yellow ~60, green ~120, cyan ~180, blue ~240,
#                  magenta ~300, red again ~360.
KNOWN_CLIENT_HUE_RANGES: dict[str, tuple[float, float, str]] = {
    "fedex": (260.0, 310.0, "purple"),
    # Add others as we validate them against real templates.
    # Note: don't add Accenture here — Accenture is also purple and would
    # alias with FedEx, defeating the cross-client guard.
}


def _hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    """`#RRGGBB` -> `(r, g, b)` in [0, 1]. Raises ValueError on bad input."""
    s = hex_str.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"expected #RRGGBB, got {hex_str!r}")
    return (
        int(s[0:2], 16) / 255.0,
        int(s[2:4], 16) / 255.0,
        int(s[4:6], 16) / 255.0,
    )


def _rgb_to_hsl(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """`(r, g, b)` in [0, 1] -> `(hue_deg, saturation, lightness)`.
    Saturation and lightness are in [0, 1]."""
    r, g, b = rgb
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin
    lightness = (cmax + cmin) / 2
    if delta == 0:
        return 0.0, 0.0, lightness
    if lightness < 0.5:
        saturation = delta / (cmax + cmin)
    else:
        saturation = delta / (2 - cmax - cmin)
    if cmax == r:
        hue = ((g - b) / delta) % 6
    elif cmax == g:
        hue = (b - r) / delta + 2
    else:
        hue = (r - g) / delta + 4
    return hue * 60, saturation, lightness


def validate_theme(
    theme_variables: dict[str, str],
    template_path: Path,
) -> tuple[list[str], list[str]]:
    """Structural belt-and-braces sanity check on the resolved theme.

    Returns (errors, warnings).
        errors:   hard-halt conditions. Build refuses to proceed.
        warnings: soft conditions surfaced in dispatch_plan.md.

    Brand source is `<template-stem>.brand.yml` (human-authored via
    slide-builder/scripts/register_template.py, Phase 3 interactive color
    confirmation). The slot-position-guessing class of bugs is gone by
    construction; these checks defend against human authoring errors in
    brand.yml (typo'd hexes, same color in both slots, etc.).
    """
    errors: list[str] = []
    warnings: list[str] = []
    primary = theme_variables.get("primaryColor", "").strip()
    accent = theme_variables.get("secondaryColor", "").strip()
    brand_yml = template_path.with_suffix("").as_posix() + ".brand.yml"

    # Check 1: both colors loaded
    if not primary or not accent:
        errors.append(
            f"Missing primary or accent color in resolved theme. "
            f"primaryColor={primary!r}, secondaryColor={accent!r}. "
            f"Source: {brand_yml} — primary_hex / accent_hex fields. "
            f"Re-register the template if hexes are missing or malformed."
        )
        return errors, warnings  # Further checks need both colors

    # Check 1b: primary != accent
    if primary.upper() == accent.upper():
        errors.append(
            f"primary == accent (both {primary}). "
            f"Source: {brand_yml} has the same hex in primary_hex and accent_hex. "
            f"Re-register interactively (do NOT use --auto-accept-phase1) to re-pick distinct colors."
        )

    # Check 2: plausible saturation / luminance for each
    for label, hex_value in [("primary", primary), ("accent", accent)]:
        try:
            rgb = _hex_to_rgb(hex_value)
        except ValueError as exc:
            errors.append(
                f"{label} color is invalid hex: {hex_value!r} ({exc}). "
                f"Source: {brand_yml} {label}_hex field. Expected /^[0-9A-F]{{6}}$/ after normalization."
            )
            continue
        hue, sat, light = _rgb_to_hsl(rgb)
        if light < 0.05:
            errors.append(
                f"{label} = {hex_value} is near-black (lightness {light:.2f}). "
                f"Source: {brand_yml} — primary/accent shouldn't be near-black."
            )
        elif light > 0.95:
            errors.append(
                f"{label} = {hex_value} is near-white (lightness {light:.2f}). "
                f"Source: {brand_yml} — primary/accent shouldn't be near-white."
            )
        elif sat < 0.10:
            errors.append(
                f"{label} = {hex_value} is near-grey (saturation {sat:.2f}). "
                f"Source: {brand_yml} — brand colors should be chromatic. "
                f"If this is a legitimately monochrome brand, override via --allow-neutral-brand (v0.1)."
            )

    # Check 3: template path -> expected color family
    path_lower = str(template_path).lower()
    matched_client: str | None = None
    for client_name, (hue_low, hue_high, family_label) in KNOWN_CLIENT_HUE_RANGES.items():
        if client_name not in path_lower:
            continue
        matched_client = client_name
        try:
            primary_rgb = _hex_to_rgb(primary)
        except ValueError:
            break  # already reported in Check 2
        hue, _, _ = _rgb_to_hsl(primary_rgb)
        if not (hue_low <= hue <= hue_high):
            errors.append(
                f"Template path contains {client_name!r} (expected {family_label} "
                f"primary, hue {hue_low:.0f}-{hue_high:.0f} deg), but primary={primary} "
                f"has hue {hue:.0f} deg. "
                f"Source: {brand_yml} — primary_hex doesn't match the expected color family "
                f"for this client. Either brand.yml has a typo'd hex, or the template path "
                f"matches the wrong KNOWN_CLIENT_HUE_RANGES entry (e.g., 'fedex' substring "
                f"in path that's actually a different client). Re-register or pass --client-name."
            )
        break  # only run for the first matching client

    # When no known client name appears in the template path, the hue-range check
    # can't run — surface as a warning so the operator knows the validator is
    # operating on structural checks only (primary != accent, saturation, luminance).
    # With brand.yml as source-of-truth, the historical concern (loader-bug ships
    # wrong-color slides for non-FedEx clients) is gone by construction — brand.yml
    # was human-confirmed at registration time. This warning is mostly informational.
    if matched_client is None:
        known_clients = sorted(KNOWN_CLIENT_HUE_RANGES.keys()) or ["(none registered)"]
        warnings.append(
            f"client '{template_path.name}' (path: {template_path}) not in "
            f"KNOWN_CLIENT_HUE_RANGES (currently: {known_clients}). "
            f"Check 3 (brand-specific hue range) skipped — structural validation "
            f"(primary != accent, plausible saturation/luminance) applied only. "
            f"Brand source is {brand_yml} (human-confirmed at registration). "
            f"To add this client to the hue-range guard, append an entry to "
            f"KNOWN_CLIENT_HUE_RANGES in scripts/build_deck.py."
        )

    return errors, warnings


# ----------------------------------------------------------------------
# Prompt rendering
# ----------------------------------------------------------------------

PROMPT_BODY_MARKER = "# Slide {{SLIDE_N}} build prompt"


def render_prompt(template_text: str, placeholders: dict[str, str]) -> str:
    """Strip the prompt.md metadata table, then substitute {{TOKEN}}s.

    The template has a Placeholders table at the top that documents the
    tokens — those literal mentions must NOT be substituted. We split on
    the first occurrence of '# Slide {{SLIDE_N}} build prompt' and render
    only the body.
    """
    idx = template_text.find(PROMPT_BODY_MARKER)
    if idx == -1:
        sys.stderr.write(
            f"ERROR: prompt.md template missing the expected body marker "
            f"'{PROMPT_BODY_MARKER}'. Template: {PROMPT_TEMPLATE}\n"
        )
        sys.exit(4)
    body = template_text[idx:]
    for token, value in placeholders.items():
        body = body.replace("{{" + token + "}}", str(value))
    return body


def build_placeholders(
    slide: dict[str, Any],
    slide_total: int,
    deck_notes: str,
    client_template_path: Path,
    output_dir: Path,
    seeds: dict[str, str],
    likely_prior_patterns: str,
) -> dict[str, str]:
    """Assemble the {{TOKEN}} → value dictionary for one slide."""
    return {
        "SLIDE_N":                 str(slide["slide_n"]),
        "SLIDE_TOTAL":             str(slide_total),
        "SLIDE_TITLE":             slide.get("title", "") or "(untitled)",
        "GOVERNING_THOUGHT":       slide.get("governing_thought", "") or "(no governing thought in brief)",
        "SO_WHAT":                 slide.get("so_what", "") or "(no so-what in brief)",
        "EDITORIAL_EMPHASIS":      slide.get("editorial_emphasis", "") or "(none specified)",
        "EVIDENCE_CONTENT":        slide.get("evidence_content", "") or "(no evidence specified)",
        "CHART_TYPE":              slide.get("chart_type", "none"),
        "NOT_THIS_SLIDE":          slide.get("not_this_slide", "") or "(none)",
        "DECK_LEVEL_DESIGN_NOTES": deck_notes or "(no deck-level design notes)",
        "CLIENT_TEMPLATE_PATH":    str(client_template_path),
        "OUTPUT_DIR":              str(output_dir),
        "CONTENT_HASH":            seeds["content_hash"],
        "PATTERN_PICK_SEED":       seeds["pattern_pick_seed"],
        "VARIANT_SEED_A":          seeds["variant_seed_a"],
        "VARIANT_SEED_B":          seeds["variant_seed_b"],
        "VARIANT_SEED_C":          seeds["variant_seed_c"],
        "LIKELY_PRIOR_PATTERNS":   likely_prior_patterns,
        "LAYOUTS_MD_PATH":         str(LAYOUTS_MD),
        "ANTI_PATTERNS_MD_PATH":   str(ANTI_PATTERNS_MD),
        "FALLBACK_MD_PATH":        str(FALLBACK_MD),
        "FALLBACK_EXAMPLES_DIR":   str(FALLBACK_EXAMPLES_DIR),
        "SKILL_MD_PATH":           str(SKILL_MD),
        "HELPERS_MODULE_PATH":     str(HELPERS_MODULE_PATH),
    }


def format_prior_patterns(slide_n: int, forecasts: list[str]) -> str:
    """Build the LIKELY_PRIOR_PATTERNS injection text for slide_n.

    `forecasts` is the full list of forecasted patterns indexed by slide
    number (1-based). For slide N, we show the forecasts for N-2 and N-1.
    """
    if slide_n == 1:
        return "(this is the first slide — no prior context)"
    if slide_n == 2:
        return f"slide 1 forecast: {forecasts[0]}"
    return (
        f"slide {slide_n - 2} forecast: {forecasts[slide_n - 3]}\n"
        f"slide {slide_n - 1} forecast: {forecasts[slide_n - 2]}"
    )


# ----------------------------------------------------------------------
# Dispatch plan
# ----------------------------------------------------------------------

def write_dispatch_plan(
    out_dir: Path,
    slides: list[dict[str, Any]],
    forecasts: list[str],
    client_slug: str,
    theme_path: Path,
    fallbacks_used: list[str],
    theme_warnings: list[str],
    brief_path: Path,
    client_template_path: Path,
) -> Path:
    """Write a deck-level dispatch_plan.md so the parent session has a
    one-stop summary of what was prepped."""
    plan_path = _p.dispatch_plan_md(out_dir)
    lines: list[str] = [
        "# Dispatch plan — slide-builder prep",
        "",
        f"- Brief:           {brief_path}",
        f"- Client template: {client_template_path}",
        f"- Client slug:     {client_slug}",
        f"- Mermaid theme:   {theme_path}",
        f"- Slide total:     {len(slides)}",
        "",
    ]
    if fallbacks_used:
        lines.append("## Theme fallbacks (slots that used hardcoded defaults)")
        lines.append("")
        for entry in fallbacks_used:
            lines.append(f"- {entry}")
        lines.append("")
    if theme_warnings:
        lines.append("## Theme validation warnings — REVIEW BEFORE APPROVING BUILD")
        lines.append("")
        lines.append(
            "These are soft conditions that did not halt the build but indicate "
            "validation was partial. The operator must read them before approving "
            "the first A/B output for this template."
        )
        lines.append("")
        for entry in theme_warnings:
            lines.append(f"- {entry}")
        lines.append("")
    lines.append("## Per-slide forecast (adjacency context — NOT a constraint)")
    lines.append("")
    lines.append("| Slide | Title | Forecasted pattern |")
    lines.append("|---|---|---|")
    for slide, forecast in zip(slides, forecasts):
        title = slide.get("title", "(untitled)")
        lines.append(f"| {slide['slide_n']} | {title} | {forecast} |")
    lines.append("")
    lines.append("## Per-slide artifact locations")
    lines.append("")
    for slide in slides:
        slide_dir = _p.slide_dir(out_dir, slide["slide_n"])
        lines.append(f"- Slide {slide['slide_n']}: `{slide_dir / '_prompt.md'}`")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Parent session dispatches one `slide-builder-worker` agent per slide "
        "IN PARALLEL using the rendered `_prompt.md` files above. Each agent writes "
        "`option_A.py`, `option_B.py`, `option_C.py` (plus `option_X.mmd` for "
        "Mermaid-fallback slides) into its own `slide_NN/` directory. Then run "
        "`finalize_deck.py` to graft, render, and produce REVIEW.html."
    )
    plan_path.write_text("\n".join(lines), encoding="utf-8")
    return plan_path


# ----------------------------------------------------------------------
# Deck manifest — _meta.json
#
# Single source of truth for downstream pipeline scripts. Written by
# build_deck.py after theme generation; consumed by:
#   - finalize_deck.py::_resolve_mermaid_theme  (mermaid_theme path)
#   - compile_picks.py:main                     (template path)
#   - build_review.py:main                      (slides[], brief, deck_meta)
#
# Schema is reader-driven. Adding a new key is safe; renaming or removing
# an existing one requires bumping META_SCHEMA_VERSION + updating readers.
# Reader audit done 2026-05-25 (see _decisions/handoff-fix-review-{A,B,C}.md).
#
# Important: build_review.py uses `slides[].n` (NOT `slide_n`) as the
# slide-number key. Keep this convention here so the readers match.
# ----------------------------------------------------------------------

def write_meta_json(
    out_dir: Path,
    brief_path: Path,
    brief: dict[str, Any],
    template_path: Path,
    theme_path: Path,
    client_slug: str,
    forecasts: list[str],
    brand: dict[str, Any],
) -> Path:
    """Write <out>/_meta.json, the canonical deck manifest."""
    front_matter = brief.get("front_matter", {}) or {}
    slides_meta: list[dict[str, Any]] = []
    for slide, forecast in zip(brief["slides"], forecasts):
        slides_meta.append({
            "n":                  slide["slide_n"],
            "title":              slide.get("title", "") or "",
            "forecasted_pattern": forecast,
            # page_type is explicit if the brief sets it, else derived from
            # **Archetype:** via ARCHETYPE_TO_PAGE_TYPE. Empty if neither
            # source resolves — downstream QC checks treat empty as "no
            # archetype-specific exemptions apply."
            "page_type":          (slide.get("page_type", "") or "").strip()
                                   or _normalize_archetype_to_page_type(
                                       slide.get("archetype", "") or ""
                                   ),
            # v0.2 P1.4: chrome.yml layout name for this slide. Required at
            # v3; resolve_slide_layouts already gates this is non-empty.
            "layout":             slide.get("layout", "") or "",
            # v0.3: per-slide variant flag. "dark" triggers full-bleed
            # brand.dark_bg_hex overlay + white title at finalize-time.
            # Empty / "light" / anything else = light variant (default).
            "variant":            (slide.get("variant", "") or "").strip().lower(),
        })

    # `generated_at` lives at TOP LEVEL because build_review.py:1117 reads it
    # there (`(meta or {}).get("generated_at")`). Schema validation in v0.1
    # will lock this. Do NOT also nest it inside deck_meta — single source of
    # truth, no drift.
    meta = {
        "schema_version":  META_SCHEMA_VERSION,
        "template":        str(template_path.resolve()),
        "brief":           str(brief_path.resolve()),
        "out":             str(out_dir.resolve()),
        "mermaid_theme":   str(theme_path.resolve()),
        "client_slug":     client_slug,
        "slide_count":     len(slides_meta),
        "generated_at":    datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brand_primary":   (brand.get("primary_hex") or "").strip(),
        "brand_accent":    (brand.get("accent_hex")  or "").strip(),
        "slides":          slides_meta,
        "deck_meta": {
            "deck_type":          front_matter.get("deck_type", "") or "",
            "governing_thought":  front_matter.get("governing_thought", "") or "",
            "audience":           front_matter.get("audience", "") or "",
        },
    }
    # Validate against the pydantic schema before writing so a malformed
    # write fails loudly here rather than at a downstream reader.
    MetaJson.model_validate(meta)
    meta_path = _p.meta_json(out_dir)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path


# ----------------------------------------------------------------------
# Stage-1 sanity check — proactive shared-infra prerequisite verification
#
# Halts at PREP time (before any agent dispatch) if:
#   (a) Client template not registered — twins.client_theme.load_brand_sidecar
#       raises BrandSidecarMissing
#   (b) mmdc (Mermaid CLI) not installed — render_mermaid.py would fail at
#       Stage 3 finalize for any FALLBACK_MERMAID option
#
# Reviewer A's "proactive sanity check, not reactive fail-at-finalize" pattern.
# Production-grade bar requires it — agent compute is not wasted on dispatches
# that would be unbuildable downstream.
# ----------------------------------------------------------------------

def _check_mmdc_installed() -> tuple[bool, str]:
    """Verify mmdc is on PATH and runnable. Returns (ok, version_or_reason)."""
    mmdc = shutil.which("mmdc")
    if not mmdc and os.name == "nt":
        # Windows npm-global fallback locations
        for candidate in (
            Path(os.environ.get("APPDATA", "")) / "npm" / "mmdc.cmd",
            Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Roaming" / "npm" / "mmdc.cmd",
        ):
            if candidate.exists():
                mmdc = str(candidate)
                break
    if not mmdc:
        return False, "mmdc not found on PATH"
    try:
        result = subprocess.run(
            [mmdc, "--version"], capture_output=True, text=True, timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, f"mmdc invocation failed: {type(exc).__name__}: {exc}"
    if result.returncode != 0:
        return False, f"mmdc --version returned exit {result.returncode}: {(result.stderr or '').strip()[:200]}"
    version = (result.stdout or "").strip()
    if not version:
        return False, "mmdc --version returned empty stdout"
    return True, version


# ----------------------------------------------------------------------
# v0.2 P1.4 — per-slide layout resolution + fail-loud gate
# ----------------------------------------------------------------------

def resolve_slide_layouts(
    brief: dict[str, Any], template_path: Path
) -> tuple[list[str], list[str], list[str]]:
    """Resolve each slide's layout name from per-slide field -> deck default
    -> fail-loud.

    Returns (per_slide_layouts, available_layouts, errors).
    per_slide_layouts: list aligned to brief['slides'], each entry is the
      resolved layout name (non-empty) — OR empty when resolution failed,
      with the offending slide enumerated in `errors`.
    available_layouts: list of layout names from chrome.yml (or [] if
      chrome.yml unreadable).
    errors: list of per-slide error strings (offending slide titles).
    """
    front_matter = brief.get("front_matter", {}) or {}
    deck_default = (front_matter.get("default_layout") or "").strip()
    slides = brief.get("slides", []) or []

    available: list[str] = []
    try:
        spec = load_chrome_yml(_p.chrome_yml(template_path))
        available = sorted(spec.layouts)
    except ChromeSidecarMissingError:
        # chrome.yml missing handled by stage1_sanity_check; the layout
        # resolution still proceeds so the error enumeration can be precise.
        available = []
    except Exception:
        available = []

    resolved: list[str] = []
    errors: list[str] = []
    for slide in slides:
        per_slide = (slide.get("layout") or "").strip()
        chosen = per_slide or deck_default
        if not chosen:
            errors.append(
                f"Slide {slide['slide_n']} — \"{slide.get('title', '(untitled)')}\""
            )
            resolved.append("")
            continue
        if available and chosen not in available:
            errors.append(
                f"Slide {slide['slide_n']} — \"{slide.get('title', '(untitled)')}\""
                f" requests layout {chosen!r} which is not in chrome.yml"
            )
            resolved.append("")
            continue
        resolved.append(chosen)
    return resolved, available, errors


def emit_layout_resolution_error(
    template_path: Path, errors: list[str], available: list[str],
    front_matter: dict[str, str],
) -> None:
    """Write the design-locked exit-9 message to stderr.

    Format matches § 5.1 of v0.2-layout-inheritance-design-lock.md so the
    operator gets exactly the two-paths-to-fix guidance the spec promised.
    """
    sys.stderr.write(
        "ERROR: brief is missing required `Layout:` field on these slides, and no\n"
        "       `default_layout:` is set in the front-matter:\n\n"
    )
    for entry in errors:
        sys.stderr.write(f"   {entry}\n")
    sys.stderr.write("\n")
    chrome_yml_path = _p.chrome_yml(template_path)
    if available:
        sys.stderr.write(
            f"Available layouts registered for {template_path.name} "
            f"(from {chrome_yml_path.name}):\n"
        )
        for name in available:
            sys.stderr.write(f"   {name}\n")
    else:
        sys.stderr.write(
            f"No layouts found in {chrome_yml_path} (file missing or empty). "
            f"Re-register the template via register_template.py propose -> commit.\n"
        )
    sys.stderr.write(
        "\nTwo ways to fix:\n\n"
        "   (A) Add `default_layout: <name>` to the brief's YAML front-matter to apply\n"
        "       one layout to every slide that doesn't override:\n\n"
        "       ---\n"
        f"       client_template: {front_matter.get('client_template', '<path>')}\n"
        f"       deck_type: {front_matter.get('deck_type', '<type>')}\n"
        "       default_layout: body_canonical_light    <-- ADD THIS LINE\n"
        "       ---\n\n"
        "   (B) Add `**Layout:** <name>` to each slide block listed above.\n\n"
        "Exit code: 9 (brief-missing-required-layout)\n"
    )


def stage1_sanity_check(template_path: Path) -> int:
    """Verify shared-infra prerequisites BEFORE agent dispatch.

    Returns 0 on success; non-zero exit code on failure (caller should
    propagate). Halts at prep time, before agent compute is sunk.
    """
    # Check (a): brand sidecar present + valid
    try:
        load_brand_sidecar(template_path)
    except BrandSidecarMissing as exc:
        sys.stderr.write(
            "ERROR: Client template not registered.\n\n"
            f"{exc}\n\n"
            "Register via the chat-driven flow:\n\n"
            f"  py -3 scripts/register_template.py propose \"{template_path}\"\n"
            "  # parent chat shows the preview PNG, takes picks, writes picks.json\n"
            f"  py -3 scripts/register_template.py commit \"{template_path}\" --picks <picks.json>\n\n"
            "Auto-picked primary/accent has inverted on every FedEx template historically;\n"
            "use the chat-driven path so a human can confirm the preview PNG before commit.\n"
        )
        return 7
    except BrandSidecarStale as exc:
        sys.stderr.write(
            "ERROR: Template SHA mismatch — brand sidecar is stale.\n\n"
            f"{exc}\n\n"
            "The template file changed since registration. Re-register to re-validate:\n"
            f"  py -3 scripts/register_template.py propose \"{template_path}\"\n"
            f"  py -3 scripts/register_template.py commit  \"{template_path}\" --picks <picks.json>\n"
        )
        return 7
    except (ValueError, OSError) as exc:
        sys.stderr.write(
            f"ERROR: load_brand_sidecar failed: {type(exc).__name__}: {exc}\n"
            "       (Malformed brand.yml, parse error, or filesystem error.)\n"
            "       Re-register the template:\n"
            f"  py -3 scripts/register_template.py propose \"{template_path}\"\n"
            f"  py -3 scripts/register_template.py commit  \"{template_path}\" --picks <picks.json>\n"
        )
        return 7

    # Check (a.2): chrome.yml present (v0.2 P1.4). brand.yml is sufficient
    # for theme remap but finalize_deck refuses to graft without chrome.yml.
    # Halt at prep so the operator re-registers before agent dispatch.
    chrome_yml_path = _p.chrome_yml(template_path)
    if not chrome_yml_path.exists():
        sys.stderr.write(
            f"ERROR: chrome.yml missing for template.\n"
            f"  Expected at: {chrome_yml_path}\n\n"
            "v0.2 finalize_deck requires the per-layout chrome sidecar. "
            "Re-register to produce it:\n"
            f"  py -3 scripts/register_template.py propose \"{template_path}\"\n"
            f"  py -3 scripts/register_template.py commit  \"{template_path}\" --picks <picks.json>\n"
        )
        return 7
    try:
        load_chrome_yml(chrome_yml_path)
    except Exception as exc:
        sys.stderr.write(
            f"ERROR: chrome.yml at {chrome_yml_path} failed to load: "
            f"{type(exc).__name__}: {exc}\n"
            "Re-register the template (register_template.py propose -> commit).\n"
        )
        return 7

    # Check (b): mmdc installed at runnable version
    ok, info = _check_mmdc_installed()
    if not ok:
        sys.stderr.write(
            "ERROR: Mermaid CLI (mmdc) not installed or not runnable.\n\n"
            f"  Detail: {info}\n\n"
            "Install the pinned version:\n"
            "  npm install -g @mermaid-js/mermaid-cli@11.4.0\n\n"
            "Verify:\n"
            "  mmdc --version   # expected: 11.4.0\n"
        )
        return 7

    # Both checks passed — propagate version info to console for audit
    print(f"[stage-1 sanity] brand sidecar OK for: {template_path}")
    print(f"[stage-1 sanity] mmdc version: {info}")
    return 0


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prep a narrative brief for v2 parallel-agent fanout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--brief",    required=True, type=Path, help="Path to narrative brief markdown")
    parser.add_argument("--template", required=True, type=Path, help="Path to client PPTX template")
    parser.add_argument("--out",      required=True, type=Path, help="Output directory for per-slide prompts")
    parser.add_argument(
        "--client-name",
        default=None,
        help="Override client slug detection. By default, derived from the template's parent directory.",
    )
    args = parser.parse_args()

    from _log import attach as _log_attach  # noqa: E402
    _log_attach(args.out, "build_deck.py")

    # Validate inputs
    if not args.template.exists():
        sys.stderr.write(f"ERROR: client template does not exist: {args.template}\n")
        return 3
    if not PROMPT_TEMPLATE.exists():
        sys.stderr.write(f"ERROR: prompt.md template missing at {PROMPT_TEMPLATE}\n")
        return 4

    # 0. STAGE-1 SANITY CHECK — proactive prerequisite verification, BEFORE
    # output dir creation. Reviewer-B catch: if sanity check fails, we should
    # NOT leave breadcrumb output dirs on disk from a failed prep.
    sanity_rc = stage1_sanity_check(args.template)
    if sanity_rc != 0:
        return sanity_rc

    # Output dir — only created after sanity check passes
    try:
        args.out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"ERROR: cannot create output directory {args.out}: {exc}\n")
        return 5

    # 1. Read brief
    brief = parse_brief(args.brief)
    slides = brief["slides"]
    slide_total = brief["slide_total"]
    deck_notes = brief["deck_notes"]

    # 1.5 v0.2 P1.4: resolve every slide's layout name; fail-loud with exit 9
    # if any slide lacks one (per-slide field OR deck default OR missing).
    slide_layouts, available_layouts, layout_errors = resolve_slide_layouts(
        brief, args.template
    )
    if layout_errors:
        emit_layout_resolution_error(
            args.template, layout_errors, available_layouts,
            brief.get("front_matter", {}) or {},
        )
        return 9
    # Splice resolved layouts back into brief['slides'] so downstream
    # consumers (meta writer, dispatch plan) see the canonical value.
    for slide, layout_name in zip(slides, slide_layouts):
        slide["layout"] = layout_name

    # 2. Pattern-hint pass — forecast each slide
    forecasts: list[str] = [forecast_pattern(s) for s in slides]

    # 3. Seeds — content_hash + 4 per slide
    seeds_by_slide: list[dict[str, str]] = [compute_seeds(s) for s in slides]

    # 4. Per-client Mermaid theme generation.
    # Reads from v1's brand sidecar (canonical). The sanity check above already
    # verified the sidecar exists + SHA-matches, so this load is safe.
    client_slug = detect_client_slug(args.template, args.client_name)
    brand = load_brand_sidecar(args.template)
    try:
        theme_path, fallbacks_used = generate_mermaid_theme(client_slug, brand)
    except ValueError as exc:
        sys.stderr.write(
            "ERROR: brand.yml has missing or malformed hex values.\n\n"
            f"  Detail: {exc}\n\n"
            f"Brand source: {args.template.with_suffix('').as_posix()}.brand.yml\n\n"
            "Re-register the template (chat-driven flow with a human in the loop):\n\n"
            f"  py -3 scripts/register_template.py propose \"{args.template}\"\n"
            f"  py -3 scripts/register_template.py commit  \"{args.template}\" --picks <picks.json>\n\n"
            "Production-grade bar: refusing to generate a Mermaid theme with silent\n"
            "fallback defaults — the historical FedEx smoke's 'colors correct' was a\n"
            "false-positive (hardcoded fallback shape coincidentally matched). See\n"
            "_decisions/smoke-test-finding-2026-05-25.md § 'Critical correction'.\n"
        )
        return 6

    # 4.5 Theme sanity-check — structural belt-and-braces.
    # The brand.yml is human-authored via register_template.py (Phase 3 manual
    # color confirmation), so the slot-position guessing-bug class of failures
    # is gone by construction. validate_theme still runs as a structural guard:
    # primary != accent, plausible saturation/luminance, optional client-hue-range
    # confirmation if KNOWN_CLIENT_HUE_RANGES has an entry.
    try:
        theme_doc = json.loads(theme_path.read_text(encoding="utf-8"))
        theme_variables = theme_doc.get("themeVariables", {})
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"ERROR: failed to re-read generated theme {theme_path}: {exc}\n")
        return 6
    theme_errors, theme_warnings = validate_theme(theme_variables, args.template)
    if theme_errors:
        sys.stderr.write(
            "ERROR: client theme validation failed.\n"
            "       Refusing to build slides with wrong colors.\n\n"
        )
        for err in theme_errors:
            sys.stderr.write(f"  - {err}\n\n")
        sys.stderr.write(
            f"Resolved theme: {theme_path}\n"
            f"Template path:  {args.template}\n"
            f"Brand source:   {args.template.with_suffix('').with_suffix('.brand.yml').name}\n\n"
            "Likely causes:\n"
            "  1. Human error in brand.yml — primary_hex and accent_hex are the same,\n"
            "     or one of them is near-black / near-white / near-grey. Re-register the\n"
            "     template via the chat-driven propose → commit flow so a human can\n"
            "     confirm the preview PNG before the picks land.\n"
            "  2. brand.yml has a hex format the validator can't parse — verify hex codes\n"
            "     match /^[0-9A-F]{6}$/ (uppercase, no '#') after _normalize_hex.\n"
            "  3. Template path doesn't match a known client convention — if the brand colors\n"
            "     are actually correct, extend KNOWN_CLIENT_HUE_RANGES.\n\n"
            f"To re-register:\n"
            f"  py -3 scripts/register_template.py propose \"{args.template}\"\n"
            f"  py -3 scripts/register_template.py commit  \"{args.template}\" --picks <picks.json>\n"
        )
        return 6

    # 5. Render per-slide prompts
    template_text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    for slide, seeds in zip(slides, seeds_by_slide):
        slide_n = slide["slide_n"]
        slide_dir = _p.slide_dir(args.out, slide_n)
        slide_dir.mkdir(parents=True, exist_ok=True)
        likely_prior = format_prior_patterns(slide_n, forecasts)
        placeholders = build_placeholders(
            slide=slide,
            slide_total=slide_total,
            deck_notes=deck_notes,
            client_template_path=args.template.resolve(),
            output_dir=slide_dir.resolve(),
            seeds=seeds,
            likely_prior_patterns=likely_prior,
        )
        rendered = render_prompt(template_text, placeholders)
        _p.prompt_md(args.out, slide_n).write_text(rendered, encoding="utf-8")

    # Deck manifest (_meta.json) — single source of truth for downstream
    # pipeline scripts. Writes AFTER slide prompts are rendered so that any
    # exception in render_prompt aborts before the manifest claims success.
    meta_path = write_meta_json(
        out_dir=args.out,
        brief_path=args.brief,
        brief=brief,
        template_path=args.template,
        theme_path=theme_path,
        client_slug=client_slug,
        forecasts=forecasts,
        brand=brand,
    )

    # Dispatch plan
    plan_path = write_dispatch_plan(
        out_dir=args.out,
        slides=slides,
        forecasts=forecasts,
        client_slug=client_slug,
        theme_path=theme_path,
        fallbacks_used=fallbacks_used,
        theme_warnings=theme_warnings,
        brief_path=args.brief.resolve(),
        client_template_path=args.template.resolve(),
    )

    # Console summary (paths as plain text)
    print(f"Prepped {slide_total} slides at:")
    print(f"  {args.out.resolve()}")
    print()
    print(f"Mermaid theme (per-client):")
    print(f"  {theme_path}")
    if fallbacks_used:
        print(f"  Theme slots using hardcoded fallback: {len(fallbacks_used)} (see dispatch_plan.md)")
    if theme_warnings:
        print()
        print(f"Theme validation warnings: {len(theme_warnings)} (see dispatch_plan.md § 'Theme validation warnings')")
        for w in theme_warnings:
            # Print a one-line truncated preview to stderr-like console output
            head = w.split(".", 1)[0]
            print(f"  WARNING: {head}.")
    print()
    print(f"Deck manifest:")
    print(f"  {meta_path}")
    print()
    print(f"Dispatch plan:")
    print(f"  {plan_path}")
    print()
    print("Next: dispatch one slide-builder-worker agent per slide in parallel,")
    print("reading the rendered _prompt.md in each slide_NN/ directory. Then run finalize_deck.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
