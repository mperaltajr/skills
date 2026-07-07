#!/usr/bin/env python3
"""
build_deck.py — prep script (slide-builder).

Reads a storyline-helper narrative brief + a client PPTX template, then writes
one self-contained per-slide _prompt.md to <out>/slide_NN/_prompt.md plus a
deck-level dispatch_plan.md summary. The parent session dispatches one worker
agent per slide using those rendered prompts.

Responsibilities:

  1. Read narrative brief + client template.
  2. Prep-time pattern-hint pass: run the layouts.md signals table once per
     slide to forecast each slide's likely pattern. Forecast is injected as
     adjacency CONTEXT into each prompt, not as a constraint — the agent
     overrides at dispatch time if its brief read differs.
  3. Lock content_hash = md5(governing_thought + so_what + evidence_content).
     Compute 4 seeds per slide:
       pattern_pick_seed = md5(content_hash + slide_n)
       variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)
  4. Render prompt.md with all placeholders interpolated.

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
       See validate_theme().
    7  Stage-1 sanity check failed — prerequisite missing.
       The client template is not registered (BrandSidecarMissing — run
       slide-builder/scripts/register_template.py). Halts at prep time
       before agent dispatch costs are sunk.

Cross-platform note: invoke this script with sys.executable from other scripts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

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
SKILL_MD = SKILL_ROOT / "SKILL.md"
THEME_DIR = SKILL_ROOT / "theme"

# HELPERS_MODULE_PATH is the prompt-template substitution token consumed by
# per-slide agent scripts; it points at SKILL_ROOT, where twins/helpers.py lives
# at <SKILL_ROOT>/twins/helpers.py.
HELPERS_MODULE_PATH = SKILL_ROOT

# Make twins.client_theme importable. load_brand_sidecar is the canonical
# source of truth for client brand colors and fonts — it reads <stem>.brand.yml
# (human-authored once via register_template.py) and verifies <stem>.theme.json
# (SHA-stamped audit blob). It does NOT walk template.json slot positions —
# slot-position guessing can surface false positives in which hardcoded
# defaults coincidentally match the client brand.
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
#   `### Slide 1 — Title text`   (title-on-header — preferred)
#   `### Slide 1`                (title-less header — storyline-helper's alternate documented format)
# When title is missing on the header line, parse_brief falls back to the
# `**Slide title:**` body field, then to a synthetic "Slide N" placeholder.
# H2 (##) and H3 (###) both supported. The (\d+) clause gates on the digit.
SLIDE_HEADER_RE = re.compile(r"^#{2,3}\s+Slide\s+(\d+)\s*(?:[—\-:]\s*(.+?)\s*)?$", re.MULTILINE)
# The lookahead must terminate on any H1-H3 boundary, not only H2.
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
    "layout":              ("layout",),  #
    "variant":             ("variant",),  # "dark" triggers dark-background variant
    "governing_thought":   ("governing thought", "governing thought (the claim)"),
    "so_what":             ("so-what", "so what", "so-what (the takeaway)"),
    "editorial_emphasis":  ("editorial emphasis",),
    "evidence_content":    ("evidence", "evidence / content", "evidence/content", "content"),
    "chart_type":          ("chart type",),
    "chart_data":          ("chart data",),
    "not_this_slide":      ("what this slide is not",),
    # Optional per-slide steering fields. The brief author may set these to
    # bias the worker's pattern + composition choices; absent fields fall
    # back to the worker's own judgment. Threaded into _prompt.md so the
    # worker actually honors them (not parse-only).
    "visual_rhythm":       ("visual rhythm",),
    "mandatory_shape":     ("mandatory shape",),
    "forbidden_patterns":  ("forbidden patterns",),
    "accent_placement":    ("accent placement",),
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


# ----------------------------------------------------------------------
# Build-path routing helpers
#
# Default behavior: when --pattern is omitted and settings.json::enable_sketch
# is False (the shipped default), effective_pattern resolves to "legacy" and
# write_meta_json omits all build-path optional fields entirely. _meta.json
# is byte-identical to the pptx-direct-only output. Only when the user opts in
# does any build-path field appear in _meta.json.
# ----------------------------------------------------------------------

_SETTINGS_JSON_PATH = SKILL_ROOT / "settings.json"


def _load_skill_settings() -> dict[str, Any]:
    """Load slide-builder/settings.json if present. Returns {} when missing
    or malformed (skill ships with a sane settings.json; absence is treated
    as 'use hard-coded defaults' rather than fail-loud)."""
    try:
        if not _SETTINGS_JSON_PATH.exists():
            return {}
        raw = json.loads(_SETTINGS_JSON_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {}
        return raw
    except (OSError, json.JSONDecodeError):
        # Don't crash on a malformed settings.json; warn and fall back.
        sys.stderr.write(
            f"  WARN: failed to parse {_SETTINGS_JSON_PATH}; falling back to "
            f"hard-coded defaults (legacy pattern, sketch path disabled).\n"
        )
        return {}


def _resolve_effective_pattern(cli_value: Optional[str]) -> str:
    """Resolve the effective pattern for this build.

    Resolution order:
      1. --pattern CLI flag (if provided)
      2. settings.json::default_pattern
      3. Hard default 'legacy' (preserve current behavior)

    Master switch: settings.json::enable_sketch. When False, any non-legacy
    resolved value is downgraded to 'legacy' with a stderr warning. This is
    the rollback lever — flipping enable_sketch: false in settings.json
    forces every build (including those passing --pattern sketch) back to the
    pptx-direct-only pipeline.

    Returns: "legacy" | "auto" | "sketch" | "direct"
    """
    settings = _load_skill_settings()
    if cli_value is not None:
        resolved = cli_value
    else:
        resolved = settings.get("default_pattern", "legacy")
    if resolved not in ("legacy", "auto", "sketch", "direct"):
        sys.stderr.write(
            f"  WARN: invalid pattern value {resolved!r}; falling back to "
            f"'legacy'. (If this is a stale 'B'/'C' value, re-run with "
            f"--pattern sketch / --pattern direct.)\n"
        )
        resolved = "legacy"
    enable = settings.get("enable_sketch", False)
    if not enable and resolved != "legacy":
        sys.stderr.write(
            f"  WARN: pattern={resolved!r} requested but settings.json has "
            f"enable_sketch: false. Downgrading to 'legacy'. To enable the "
            f"sketch (HTML-first) path, edit {_SETTINGS_JSON_PATH} and set "
            f"enable_sketch: true.\n"
        )
        resolved = "legacy"
    return resolved


def _classify_slide_pattern(brief_slide: dict[str, Any]) -> str:
    """Classify a single slide as 'sketch' (HTML-first) or 'direct' (pptx-direct).

    Moderate routing:
      - Pure-text archetypes (Cover/Title, Section Divider) -> direct
      - Visual archetypes (Analytical, Framework, Synthesis, Roadmap, Risk,
        Financial) -> sketch
      - Any slide referencing a chart / table / iconography -> sketch
      - Default: sketch (when in doubt, route to the higher-quality path)
    """
    archetype = (brief_slide.get("archetype") or "").strip().lower()
    # Normalize whitespace around the "/" so "cover / title" and "cover/title"
    # both match. Also include the standalone "cover" and "title" forms that
    # ARCHETYPE_TO_PAGE_TYPE accepts.
    archetype = archetype.replace(" / ", "/").replace(" /", "/").replace("/ ", "/")
    pure_text = {"cover/title", "cover", "title", "section divider"}
    visual = {
        "analytical", "framework/conceptual", "synthesis/findings",
        "roadmap/implementation", "risk", "financial/business case",
    }
    if archetype in pure_text:
        return "direct"
    if archetype in visual:
        return "sketch"
    # Content signals
    if brief_slide.get("chart_type"):
        return "sketch"
    evidence_lc = (brief_slide.get("evidence", "") or "").lower()
    if "table" in evidence_lc or "icon" in evidence_lc:
        return "sketch"
    # Default: when in doubt, route to the higher-quality path (sketch)
    return "sketch"


def _classify_all_slides(slides: list[dict[str, Any]],
                          effective_pattern: str) -> dict[str, str]:
    """Return {slide_n_str: 'sketch'|'direct'} for every slide given the effective pattern.

    - effective_pattern == 'legacy': returns {} (sketch fields omitted from
      _meta.json; readers route through the legacy path).
    - 'auto': per-slide via _classify_slide_pattern.
    - 'sketch': force all slides to sketch.
    - 'direct': force all slides to direct.
    """
    if effective_pattern == "legacy":
        return {}
    if effective_pattern == "sketch":
        return {str(s["slide_n"]): "sketch" for s in slides}
    if effective_pattern == "direct":
        return {str(s["slide_n"]): "direct" for s in slides}
    # 'auto'
    return {str(s["slide_n"]): _classify_slide_pattern(s) for s in slides}


# ----------------------------------------------------------------------
# Storyline gate enforcement
#
# Slide quality drops drastically when briefs bypass storyline-helper's
# 9-part quality gate (governing thought too vague, slides without a clear
# so-what, missing evidence, mis-sequenced argument). To stop the bypass,
# storyline-helper writes a `storyline_gate_passed: true` marker into the
# brief's YAML front-matter on a successful gate pass, along with a SHA
# of the brief body. build_deck refuses to run without that marker.
#
# Carve-out: `mode: template-fill`, `mode: rebuild-slice`, or `mode: rfp` in
# front-matter explicitly opts out of the gate. All three are legitimate flows
# that don't have a narrative argument to gate:
#   template-fill  — PMO recurring reports
#   rebuild-slice  — single-slide rebuild
#   rfp            — RFP / proposal response from rfp-helper. RFP quality is
#                    enforced by rfp-helper's own pre-brief checks (win-theme
#                    threading, criteria coverage, specificity, explicit
#                    "why us") — the narrative gate doesn't apply to a
#                    prescribed-structure scoring document.
#
# The `storyline_gate_passed: true` marker is the contract — it certifies the
# brief came through storyline-helper's quality gate. Bypass modes opt out for
# legitimate non-narrative flows.
# ----------------------------------------------------------------------

GATE_BYPASS_MODES = {"template-fill", "rebuild-slice", "rfp"}


def _enforce_storyline_gate(front_matter: dict[str, str], body: str,
                            brief_path: Path, bypass: bool = False) -> None:
    # A single-slide rebuild of an already-built deck is itself a rebuild-slice
    # flow, so the narrative gate is bypassed regardless of the reused brief's
    # own marker.
    if bypass:
        return
    mode = (front_matter.get("mode") or "").strip().lower()
    if mode in GATE_BYPASS_MODES:
        return

    passed_raw = (front_matter.get("storyline_gate_passed") or "").strip().lower()
    if passed_raw not in ("true", "yes", "1"):
        sys.stderr.write(
            "ERROR: brief is missing the storyline-helper gate marker.\n\n"
            f"  Brief: {brief_path}\n\n"
            "Slide-builder requires briefs to be produced by storyline-helper\n"
            "and pass its quality gate. To fix, one of:\n\n"
            "  (1) Run storyline-helper on this brief. On a clean gate-pass it\n"
            "      writes the required front-matter field:\n"
            "        storyline_gate_passed: true\n\n"
            "  (2) If this is a legitimate non-narrative flow (PMO recurring\n"
            "      report, single-slide rebuild, or RFP response), add to the\n"
            "      front-matter:\n"
            "        mode: template-fill      # for PMO / template fill mode\n"
            "        mode: rebuild-slice      # for single-slide rebuild\n"
            "        mode: rfp                # for rfp-helper proposal briefs\n"
        )
        sys.exit(10)


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


def extract_deck_section(body: str, *heading_aliases: str) -> str:
    """Extract the body text under a deck-level `## <heading>` section.

    Used for deck-level fields that storyline-helper writes as `##` headings
    rather than YAML front-matter (governing thought, audience). Tries each
    alias in order; returns the first non-empty match, or "".

    Section runs from the matched `## heading` to the next H1-H3 boundary.
    """
    for alias in heading_aliases:
        pat = re.compile(
            r"^##\s+" + re.escape(alias) + r"\s*\n(.*?)(?=^#{1,3}\s|\Z)",
            re.MULTILINE | re.IGNORECASE | re.DOTALL,
        )
        m = pat.search(body)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


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


def parse_brief(brief_path: Path, bypass_gate: bool = False) -> dict[str, Any]:
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
    _enforce_storyline_gate(front_matter, body, brief_path, bypass=bypass_gate)
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
            "layout": extract_field(block, FIELD_LABELS["layout"]),  #
            "variant": (extract_field(block, FIELD_LABELS["variant"]) or "").strip().lower(),
            "governing_thought": extract_field(block, FIELD_LABELS["governing_thought"]),
            "so_what": extract_field(block, FIELD_LABELS["so_what"]),
            "editorial_emphasis": extract_field(block, FIELD_LABELS["editorial_emphasis"]),
            "evidence_content": extract_field(block, FIELD_LABELS["evidence_content"]),
            "chart_type": (extract_field(block, FIELD_LABELS["chart_type"]) or "none").lower(),
            "chart_data": extract_field(block, FIELD_LABELS["chart_data"]),
            "not_this_slide": extract_field(block, FIELD_LABELS["not_this_slide"]),
            "visual_rhythm": extract_field(block, FIELD_LABELS["visual_rhythm"]),
            "mandatory_shape": extract_field(block, FIELD_LABELS["mandatory_shape"]),
            "forbidden_patterns": extract_field(block, FIELD_LABELS["forbidden_patterns"]),
            "accent_placement": extract_field(block, FIELD_LABELS["accent_placement"]),
        }
        slides.append(slide)

    # Deck-level governing thought + audience: storyline-helper writes these
    # as `## Governing thought (the whole deck)` / `## Audience` body
    # headings, not front-matter keys. Capture both here so write_meta_json
    # can populate deck_meta from the body when front-matter is empty.
    deck_governing_thought = extract_deck_section(
        body, "Governing thought (the whole deck)", "Governing thought",
    )
    deck_audience = extract_deck_section(body, "Audience")

    return {
        "front_matter": front_matter,
        "deck_notes": deck_notes,
        "deck_governing_thought": deck_governing_thought,
        "deck_audience": deck_audience,
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
    "fallback":            "FALLBACK (SKELETON_REJECTED)",
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

    These seeds drive deterministic variant rotation: the same brief content
    always produces the same pattern pick and variant choices.
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
# Client slug
# ----------------------------------------------------------------------

def slugify(name: str) -> str:
    """Lowercase, hyphen-separated, filename-safe."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "client"


def detect_client_slug(template_path: Path, override: str | None) -> str:
    """Derive a client slug from an override or the template path.

    `override` is the CLI --client-name when given, otherwise the brief's
    `client_name` front-matter; when both are absent the slug is derived from
    the template's parent directory.

    Examples:
        template = .../Acme/_templates/Template2.pptx    →  "acme"
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


# Per-client Mermaid theme generation was removed; the sketch path (HTML→PNG)
# supersedes it for curved-container diagrams.


# ----------------------------------------------------------------------
# Theme sanity-check — structural belt-and-braces on the brand.yml-derived
# theme. Brand colors are human-confirmed at registration time, so the
# slot-position-guessing class of failures is gone by construction. These
# checks defend against brand.yml authoring errors (typo'd hexes, same
# color in both slots).
#
# Two checks:
#   1. primary and accent both loaded; primary != accent.
#   2. Plausible saturation / luminance for each (not pure black/white,
#      not near-grey).
# ----------------------------------------------------------------------


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

    Brand source is `<template-stem>/brand.yml` (subfolder layout;
    human-authored via slide-builder/scripts/register_template.py, Phase 3
    interactive color confirmation). The slot-position-guessing class of
    bugs is gone by construction; these checks defend against human
    authoring errors in brand.yml (typo'd hexes, same color in both slots,
    etc.).
    """
    errors: list[str] = []
    warnings: list[str] = []
    primary = theme_variables.get("primaryColor", "").strip()
    accent = theme_variables.get("secondaryColor", "").strip()
    brand_yml = str(_p.brand_yml(template_path))

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
                f"If this is a legitimately monochrome brand, override via --allow-neutral-brand."
            )

    return errors, warnings


# ----------------------------------------------------------------------
# Per-slide context bundle (_context.md)
# ----------------------------------------------------------------------
#
# Generated alongside _prompt.md, this file gives the per-slide worker
# agent the full constraint set — canonical reference, design rules,
# brief metadata, and prior-slide context — to reason against as
# context, not as gates.

CONTEXT_TEMPLATE = """# Slide {slide_n} — Worker context bundle

> This is **context to reason against**, not a checklist to mechanically
> enforce. The worker agent should use these constraints to inform its
> pattern picks and variant choices, and is free to bend a soft rule when
> it has a good reason. Hard rules are surfaced in `_prompt.md` and the
> skill's hardline rules — not here.

## 1. Canonical reference (from brand.yml)

{reference_block}

## 2. Design rules — soft constraints

- **Title wrap:** if the title renders to >2 lines at the registered font
  size, the slide drops its subtitle automatically.
  Implication: keep titles to ≤2 visual lines; if a 3-line title is
  intentional, the subtitle/so-what won't render.
- **Subtitle fit:** ~130 chars at 16pt in a ~12.5"×0.39" box. Above ~130
  chars the subtitle will wrap and crowd the body zone.
- **Accent placement:** legends go right-aligned below the sub-headline
  (primary), or top-right of the chart when the right side is occupied
  (fallback). Top/bottom invariant zones hold sources/footnotes/page
  numbers only — NO ACCENTURE/DRAFT/CONFIDENTIAL tags.
- **Title bottom-anchor:** title bottom-y is fixed; 2-line titles grow
  UPWARD into the chrome zone, never displacing the subtitle.
- **No inline run formatting on placeholders.** Title/subtitle inherit
  fonts and colors from the master theme. Workers should not bake in
  hardcoded colors.

## 3. This slide's brief metadata

- Title: {title!r} ({title_len} chars)
- So-what: {so_what!r} ({so_what_len} chars)
- Archetype: {archetype!r}
- Editorial emphasis: {emphasis!r}
- Layout: {layout!r}

## 4. QC anchor

The compiled deck will be QC'd by the `slide-qc` skill, which does
zone-by-zone vision review of every rendered slide. The reference-slide
spec above is the visual anchor — every output slide should match its
chrome (top/bottom bands, footer geometry, title/subtitle position) and
respect the canonical palette ({primary_hex} / {accent_hex}).

## 5. Feedback ledger (prior rejections for this slide)

{prior_feedback}
"""


def _format_reference_block_for_context(brand: dict) -> str:
    ref = brand.get("reference_slide") if isinstance(brand, dict) else None
    if not ref or not isinstance(ref, dict):
        return (
            "_No reference slide was captured at registration. The worker has "
            "no canonical anchor for this template — fall back to the skill's "
            "5 hardline rules + anti-pattern library. Re-register with "
            "`reference_slide_n` in picks.json to enable richer context._"
        )
    lines = [
        f"- **Reference slide:** {ref.get('slide_n', '?')} in the registered "
        f"template",
        f"- **Layout:** `{ref.get('layout_name') or '(unknown)'}`",
    ]
    tb = ref.get("title_box_px")
    if tb:
        lines.append(
            f"- **Title box (px):** x={tb.get('x')} y={tb.get('y')} "
            f"w={tb.get('w')} h={tb.get('h')}"
        )
    sb = ref.get("subtitle_box_px")
    if sb:
        lines.append(
            f"- **Subtitle box (px):** x={sb.get('x')} y={sb.get('y')} "
            f"w={sb.get('w')} h={sb.get('h')}"
        )
    obs = ref.get("observed_colors") or []
    if obs:
        lines.append(
            f"- **Observed colors on the reference slide:** "
            + ", ".join(f"`#{c}`" for c in obs[:8])
        )
    return "\n".join(lines)


def _load_prior_feedback_for_slide(slide_dir: Path) -> str:
    """Hydrate the prior-feedback section from an on-disk file when one exists.

    Convention: any rebuild flow that wants the per-slide worker to see
    prior rejections / coach notes / reference-image pointers writes them
    to `<slide_dir>/_prior_feedback.md`. This function reads that file
    if present and returns its content for inlining into _context.md.
    When the file doesn't exist (fresh build, no prior rejection), return
    a placeholder that ALSO tells the operator how to populate it.
    """
    feedback_path = slide_dir / "_prior_feedback.md"
    if feedback_path.exists():
        try:
            text = feedback_path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                return text
        except Exception:
            pass
    return (
        "_No prior feedback recorded for this slide. To carry "
        "rejection feedback or coaching notes from a previous build "
        "iteration, write them to:_\n\n"
        f"    {feedback_path}\n\n"
        "_Any markdown content in that file is inlined verbatim into "
        "this section on the next `build_deck.py` run, so the worker "
        "agent reasons against the rejection history instead of "
        "repeating the rejected approach._"
    )


def write_slide_context_md(slide: dict, brand: dict, slide_dir: Path,
                            slide_n: int) -> Path:
    """Write `_context.md` next to `_prompt.md` for the per-slide worker
    agent, hydrating any recorded prior feedback for the slide."""
    title = (slide.get("title") or "").strip()
    so_what = (slide.get("so_what") or "").strip()
    archetype = (slide.get("archetype") or "").strip()
    emphasis = (slide.get("editorial_emphasis") or "").strip()
    layout = (slide.get("layout") or "").strip()
    content = CONTEXT_TEMPLATE.format(
        slide_n=slide_n,
        reference_block=_format_reference_block_for_context(brand),
        title=title,
        title_len=len(title),
        so_what=so_what,
        so_what_len=len(so_what),
        archetype=archetype,
        emphasis=emphasis,
        layout=layout,
        primary_hex=brand.get("primary_hex", "(unset)"),
        accent_hex=brand.get("accent_hex", "(unset)"),
        prior_feedback=_load_prior_feedback_for_slide(slide_dir),
    )
    ctx_path = slide_dir / "_context.md"
    ctx_path.write_text(content, encoding="utf-8")
    return ctx_path


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
    slide_pattern: str = "direct",
) -> dict[str, str]:
    """Assemble the {{TOKEN}} → value dictionary for one slide.

    `slide_pattern` is "sketch" (HTML output) or "direct" (python-pptx output,
    default). Defaults to "direct" so callers that don't specify a pattern keep
    working; the worker branches on the rendered PATTERN field.
    """
    return {
        "PATTERN":                 slide_pattern,
        "SLIDE_N":                 str(slide["slide_n"]),
        "SLIDE_TOTAL":             str(slide_total),
        "SLIDE_TITLE":             slide.get("title", "") or "(untitled)",
        "GOVERNING_THOUGHT":       slide.get("governing_thought", "") or "(no governing thought in brief)",
        "SO_WHAT":                 slide.get("so_what", "") or "(no so-what in brief)",
        "EDITORIAL_EMPHASIS":      slide.get("editorial_emphasis", "") or "(none specified)",
        "EVIDENCE_CONTENT":        slide.get("evidence_content", "") or "(no evidence specified)",
        "CHART_TYPE":              slide.get("chart_type", "none"),
        "CHART_DATA":              slide.get("chart_data", "") or "(no chart data provided)",
        "NOT_THIS_SLIDE":          slide.get("not_this_slide", "") or "(none)",
        "VISUAL_RHYTHM":           slide.get("visual_rhythm", "") or "(worker's judgment)",
        "MANDATORY_SHAPE":         slide.get("mandatory_shape", "") or "(none — worker's judgment)",
        "FORBIDDEN_PATTERNS":      slide.get("forbidden_patterns", "") or "(none)",
        "ACCENT_PLACEMENT":        slide.get("accent_placement", "") or "(worker's judgment)",
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
    theme_warnings: list[str],
    brief_path: Path,
    client_template_path: Path,
) -> Path:
    """Write a deck-level dispatch_plan.md so the parent session has a
    one-stop summary of what was prepped.

    Brand validation happens at template registration time, so the plan
    carries no theme-fallback section.
    """
    plan_path = _p.dispatch_plan_md(out_dir)
    lines: list[str] = [
        "# Dispatch plan — slide-builder prep",
        "",
        f"- Brief:           {brief_path}",
        f"- Client template: {client_template_path}",
        f"- Client slug:     {client_slug}",
        f"- Slide total:     {len(slides)}",
        "",
    ]
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
    lines.append(
        "Each slide directory now contains TWO sibling files. Workers read "
        "**`_context.md` first** (Gate C.1, canonical reference + design "
        "rules + brief metadata), then **`_prompt.md`** (build procedure)."
    )
    lines.append("")
    for slide in slides:
        slide_dir = _p.slide_dir(out_dir, slide["slide_n"])
        lines.append(f"- Slide {slide['slide_n']}:")
        lines.append(f"    - context: `{slide_dir / '_context.md'}`")
        lines.append(f"    - prompt:  `{slide_dir / '_prompt.md'}`")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Parent session dispatches one `slide-builder-worker` agent per slide "
        "IN PARALLEL. Each worker reads its `_context.md` first, then "
        "`_prompt.md`, and writes its three options into its own `slide_NN/` "
        "directory — `option_A.py` / `B` / `C` for direct-path slides, or "
        "`option_A.html` / `B` / `C` for sketch-path slides (per the slide's "
        "PATTERN field). Then run `finalize_deck.py` to graft, render, and "
        "produce REVIEW.html."
    )
    plan_path.write_text("\n".join(lines), encoding="utf-8")
    return plan_path


# ----------------------------------------------------------------------
# Deck manifest — _meta.json
#
# Single source of truth for downstream pipeline scripts. Written by
# build_deck.py; consumed by:
#   - finalize_deck.py:main                     (template path, per-slide entries)
#   - compile_picks.py:main                     (template path)
#   - build_review.py:main                      (slides[], brief, deck_meta)
#
# Schema is reader-driven. Adding a new key is safe; renaming or removing
# an existing one requires bumping META_SCHEMA_VERSION + updating readers.
#
# Important: build_review.py uses `slides[].n` (NOT `slide_n`) as the
# slide-number key. Keep this convention here so the readers match.
# ----------------------------------------------------------------------

def _build_slide_meta_entry(slide: dict[str, Any], forecast: str,
                            pattern_per_slide: dict[str, str]) -> dict[str, Any]:
    """Build one slide's `_meta.json` entry. Shared by the full-deck writer and
    the single-slide rebuild updater so the entry shape never drifts."""
    slide_n = slide["slide_n"]
    entry = {
        "n":                  slide_n,
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
        # chrome.yml layout name for this slide. Required;
        # resolve_slide_layouts already gates this is non-empty.
        "layout":             slide.get("layout", "") or "",
        # per-slide variant flag. "dark" triggers full-bleed
        # brand.dark_bg_hex overlay + white title at finalize-time.
        # Empty / "light" / anything else = light variant (default).
        "variant":            (slide.get("variant", "") or "").strip().lower(),
    }
    # Only populate build-path fields when the classifier produced routing for
    # this slide. Empty pattern_per_slide (legacy mode) leaves the shape unchanged.
    if str(slide_n) in pattern_per_slide:
        entry["pattern"] = pattern_per_slide[str(slide_n)]
        entry["artifacts"] = {}  # populated as build progresses
    return entry


def write_meta_json(
    out_dir: Path,
    brief_path: Path,
    brief: dict[str, Any],
    template_path: Path,
    client_slug: str,
    forecasts: list[str],
    brand: dict[str, Any],
    effective_pattern: str = "legacy",
    pattern_per_slide: Optional[dict[str, str]] = None,
) -> Path:
    """Write <out>/_meta.json, the canonical deck manifest.

    When effective_pattern != "legacy", build-path
    optional fields are populated (pattern_default, pattern_per_slide,
    html_render_canvas, translator_dispatched, translation_reports, and
    per-slide pattern/artifacts). When "legacy" (or pattern_per_slide is
    None/empty), the optional fields are omitted entirely so the on-disk
    JSON is byte-identical to the pptx-direct output. This preserves the
    guarantee: a build with no flag is byte-identical to the default.
    """
    pattern_per_slide = pattern_per_slide or {}
    front_matter = brief.get("front_matter", {}) or {}
    slides_meta: list[dict[str, Any]] = [
        _build_slide_meta_entry(slide, forecast, pattern_per_slide)
        for slide, forecast in zip(brief["slides"], forecasts)
    ]

    # `generated_at` lives at TOP LEVEL because build_review.py:1117 reads it
    # there (`(meta or {}).get("generated_at")`). Do NOT also nest it inside
    # deck_meta — single source of truth, no drift.
    meta = {
        "schema_version":  META_SCHEMA_VERSION,
        "template":        str(template_path.resolve()),
        "brief":           str(brief_path.resolve()),
        "out":             str(out_dir.resolve()),
        # The mermaid_theme field is no longer written. _meta_schema.py keeps
        # it as an optional empty-default str so existing readers continue to
        # work without surgery; new writes simply omit it.
        "client_slug":     client_slug,
        "slide_count":     len(slides_meta),
        "generated_at":    datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brand_primary":   (brand.get("primary_hex") or "").strip(),
        "brand_accent":    (brand.get("accent_hex")  or "").strip(),
        "slides":          slides_meta,
        "deck_meta": {
            "deck_type":          front_matter.get("deck_type", "") or "",
            # Front-matter first, then the `## Governing thought` / `## Audience`
            # body headings storyline-helper actually writes. Without the body
            # fallback these ship empty (the front-matter keys are never set).
            "governing_thought":  (front_matter.get("governing_thought", "") or "")
                                   or brief.get("deck_governing_thought", "") or "",
            "audience":           (front_matter.get("audience", "") or "")
                                   or brief.get("deck_audience", "") or "",
        },
    }
    # Build-path optional top-level fields. Only added when effective
    # pattern is non-legacy AND classifier produced routing. Preserves
    # byte-identical output for legacy builds (no flag, default settings).
    if effective_pattern != "legacy" and pattern_per_slide:
        meta["pattern_default"] = effective_pattern
        meta["pattern_per_slide"] = pattern_per_slide
        meta["html_render_canvas"] = "1280x720"  # locked
        meta["translator_dispatched"] = False
        meta["translation_reports"] = {}
    # Validate against the pydantic schema before writing so a malformed
    # write fails loudly here rather than at a downstream reader.
    MetaJson.model_validate(meta)
    meta_path = _p.meta_json(out_dir)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path


def update_meta_for_rebuild(
    out_dir: Path,
    brief: dict[str, Any],
    slide_n: int,
    forecasts: list[str],
    pattern_per_slide: Optional[dict[str, str]] = None,
) -> Optional[Path]:
    """Splice one rebuilt slide's entry into the existing `_meta.json`.

    Loads the on-disk manifest, replaces only slide `slide_n`'s entry (recomputed
    with the same builder the full writer uses), refreshes the per-slide pattern
    map + timestamp, and re-validates against the schema before writing. Every
    other slide's entry — including artifacts populated by later stages — is left
    exactly as it was. Returns the meta path, or None on a recoverable error.
    """
    pattern_per_slide = pattern_per_slide or {}
    meta_path = _p.meta_json(out_dir)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: cannot read {meta_path} for rebuild: {exc}\n")
        return None

    # Locate the brief slide + its forecast (forecasts align with brief slides).
    idx = next(
        (i for i, s in enumerate(brief["slides"]) if s["slide_n"] == slide_n),
        None,
    )
    if idx is None:
        sys.stderr.write(f"ERROR: slide {slide_n} not present in the brief.\n")
        return None
    new_entry = _build_slide_meta_entry(
        brief["slides"][idx], forecasts[idx], pattern_per_slide
    )

    slides_meta = meta.get("slides", [])
    replaced = False
    for i, entry in enumerate(slides_meta):
        if entry.get("n") == slide_n:
            slides_meta[i] = new_entry
            replaced = True
            break
    if not replaced:
        sys.stderr.write(
            f"ERROR: slide {slide_n} not found in existing _meta.json; "
            f"cannot rebuild a slide that wasn't in the original deck.\n"
        )
        return None

    # Keep the per-slide routing map in sync when present.
    if "pattern_per_slide" in meta and str(slide_n) in pattern_per_slide:
        meta["pattern_per_slide"][str(slide_n)] = pattern_per_slide[str(slide_n)]
    meta["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    MetaJson.model_validate(meta)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path


def _shift_build_for_insert(out_dir: Path, insert_n: int, old_count: int) -> None:
    """Make room at position `insert_n` for a new slide by shifting slides
    >= insert_n up by one on disk: rename `slide_NN/` dirs (highest first, so
    each destination is free before the rename) and shift `picks.json` keys.
    `_meta.json` is updated separately by update_meta_for_insert. No-op tail when
    inserting at the end (insert_n == old_count + 1)."""
    for k in range(old_count, insert_n - 1, -1):
        src = _p.slide_dir(out_dir, k)
        dst = _p.slide_dir(out_dir, k + 1)
        if src.exists():
            if dst.exists():
                raise OSError(f"insert shift collision: {dst} already exists")
            src.rename(dst)

    picks_path = out_dir / "picks.json"
    if picks_path.exists():
        try:
            picks = json.loads(picks_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            picks = None
        if isinstance(picks, dict):
            shifted: dict[str, Any] = {}
            for key, val in picks.items():
                m = re.fullmatch(r"slide_(\d+)", key)
                if m and int(m.group(1)) >= insert_n:
                    shifted[_p.slide_key(int(m.group(1)) + 1)] = val
                else:
                    shifted[key] = val
            picks_path.write_text(json.dumps(shifted, indent=2), encoding="utf-8")


def update_meta_for_insert(
    out_dir: Path,
    brief: dict[str, Any],
    insert_n: int,
    forecasts: list[str],
    pattern_per_slide: Optional[dict[str, str]] = None,
    old_count: int = 0,
) -> Optional[Path]:
    """Splice a newly inserted slide's entry into `_meta.json`.

    Assumes `_shift_build_for_insert` already moved the on-disk dirs + picks.
    Shifts existing `_meta` entries (and the pattern map) with n >= insert_n up by
    one, inserts the new slide's entry at insert_n (recomputed with the shared
    builder), bumps slide_count, and re-validates before writing. Other slides'
    entries are preserved verbatim apart from their renumbered `n`."""
    pattern_per_slide = pattern_per_slide or {}
    meta_path = _p.meta_json(out_dir)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: cannot read {meta_path} for insert: {exc}\n")
        return None

    # Shift existing per-slide entries up by one for n >= insert_n.
    for entry in meta.get("slides", []):
        if entry.get("n", 0) >= insert_n:
            entry["n"] = entry["n"] + 1

    # Shift the per-slide routing map's (string) keys the same way.
    existing_pps = meta.get("pattern_per_slide")
    if isinstance(existing_pps, dict):
        shifted_pps: dict[str, str] = {}
        for k, v in existing_pps.items():
            try:
                kn = int(k)
            except (TypeError, ValueError):
                shifted_pps[k] = v
                continue
            shifted_pps[str(kn + 1 if kn >= insert_n else kn)] = v
        meta["pattern_per_slide"] = shifted_pps

    # Build + insert the new slide's entry from the brief.
    idx = next(
        (i for i, s in enumerate(brief["slides"]) if s["slide_n"] == insert_n),
        None,
    )
    if idx is None:
        sys.stderr.write(f"ERROR: slide {insert_n} not present in the brief.\n")
        return None
    new_entry = _build_slide_meta_entry(
        brief["slides"][idx], forecasts[idx], pattern_per_slide
    )
    meta.setdefault("slides", []).append(new_entry)
    meta["slides"].sort(key=lambda e: e.get("n", 0))
    if (
        isinstance(meta.get("pattern_per_slide"), dict)
        and str(insert_n) in pattern_per_slide
    ):
        meta["pattern_per_slide"][str(insert_n)] = pattern_per_slide[str(insert_n)]

    meta["slide_count"] = old_count + 1
    meta["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    MetaJson.model_validate(meta)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path


# ----------------------------------------------------------------------
# Stage-1 sanity check — proactive shared-infra prerequisite verification
#
# Halts at PREP time (before any agent dispatch) when the client template is
# not registered — twins.client_theme.load_brand_sidecar raises
# BrandSidecarMissing.
#
# Proactive sanity check, not reactive fail-at-finalize — agent compute is not
# wasted on dispatches that would be unbuildable downstream.
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# — per-slide layout resolution + fail-loud gate
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
    spec = None
    try:
        spec = load_chrome_yml(_p.chrome_yml(template_path))
        available = sorted(spec.layouts)
    except ChromeSidecarMissingError:
        # chrome.yml missing handled by stage1_sanity_check; the layout
        # resolution still proceeds so the error enumeration can be precise.
        available = []
    except Exception:
        available = []

    # Layout resolution precedence (highest -> lowest):
    #   1. per-slide `Layout:` field in the brief
    #   2. brief front-matter `default_layout:`
    #   3. theme.json `default_content_layout` (set at registration time —
    #      "the layout the user wants their content slides to look like")
    #   4. sole-body-canonical auto-fallback (when chrome.yml has
    #      exactly one body-canonical layout, use it without asking)
    # Ambiguous templates with none of #1-#4 set still hard-fail with
    # exit 9 so the operator must disambiguate.
    template_default = ""
    try:
        theme_path = _p.theme_json(template_path)
        if theme_path.exists():
            theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
            template_default = (theme_data.get("default_content_layout") or "").strip()
    except Exception:
        template_default = ""

    auto_default = ""
    if not deck_default and not template_default and spec is not None:
        body_canonicals = sorted(
            name for name, lc in spec.layouts.items()
            if getattr(lc, "layout_class", None) == "body-canonical"
        )
        if len(body_canonicals) == 1:
            auto_default = body_canonicals[0]

    resolved: list[str] = []
    errors: list[str] = []
    for slide in slides:
        per_slide = (slide.get("layout") or "").strip()
        chosen = per_slide or deck_default or template_default or auto_default
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

    if template_default and not deck_default:
        sys.stderr.write(
            f"[layout] template default: using "
            f"theme.json:default_content_layout = {template_default!r} "
            f"for slides without per-slide Layout: override.\n"
        )
    elif auto_default and not deck_default and not template_default:
        # Sole-body-canonical fallback breadcrumb.
        sys.stderr.write(
            f"[layout] auto-fallback: no `default_layout:` or per-slide "
            f"`Layout:` set, theme.json has no default_content_layout; "
            f"using sole body-canonical layout {auto_default!r}.\n"
        )

    return resolved, available, errors


def emit_layout_resolution_error(
    template_path: Path, errors: list[str], available: list[str],
    front_matter: dict[str, str],
) -> None:
    """Write the exit-9 message to stderr.

    Gives the operator the two-paths-to-fix guidance for a brief missing a
    required layout.
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
    # Use a real registered layout in the example so the operator can copy it
    # verbatim; fall back to a placeholder only when no layouts are available.
    example_layout = available[0] if available else "<name>"
    sys.stderr.write(
        "\nTwo ways to fix:\n\n"
        "   (A) Add `default_layout: <name>` to the brief's YAML front-matter to apply\n"
        "       one layout to every slide that doesn't override:\n\n"
        "       ---\n"
        f"       client_template: {front_matter.get('client_template', '<path>')}\n"
        f"       deck_type: {front_matter.get('deck_type', '<type>')}\n"
        f"       default_layout: {example_layout}    <-- ADD THIS LINE\n"
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
            "Auto-picked primary/accent can invert on some templates; use the chat-driven\n"
            "path so a human can confirm the preview PNG before commit.\n"
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

    # Check (a.2): chrome.yml present. brand.yml is sufficient
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

    # Check (b): slide-qc sibling skill installed at the expected path.
    # finalize_deck.py imports render_slides from slide-qc; without it,
    # Stage 3 cascades into a confusing ImportError hours into the build.
    # Halt at prep so the user re-installs the sibling skill upfront.
    qc_render_path = SKILL_ROOT.parent / "slide-qc" / "scripts" / "render_slides.py"
    if not qc_render_path.exists():
        sys.stderr.write(
            "ERROR: slide-qc sibling skill not found.\n\n"
            f"  Expected at: {qc_render_path}\n\n"
            "Slide Lab calls slide-qc/scripts/render_slides.py at Stage 3 to "
            "render every option PPTX to PNG via LibreOffice. Without it, the "
            "build runs Stages 1-2, dispatches workers, then cascades into an "
            "import error during finalize. Halting at prep saves you the wasted "
            "agent compute.\n\n"
            "Install the slide-qc skill at the expected path:\n"
            f"  {SKILL_ROOT.parent / 'slide-qc'}\n\n"
            "See slide-builder/INSTALL.md Step 5 for the canonical install.\n"
        )
        return 7

    # No mmdc CLI check runs here: the Mermaid fallback was removed, and the
    # sketch path (HTML→PNG via Playwright, verified at install via INSTALL.md
    # Step 1.5) supersedes it.

    print(f"[stage-1 sanity] brand sidecar OK for: {template_path}")
    print(f"[stage-1 sanity] slide-qc sibling OK: {qc_render_path}")
    return 0


# ----------------------------------------------------------------------
# Template confirmation gate — surface the resolved template BEFORE dispatch
# so the operator catches wrong-template runs at the prompt instead of in
# REVIEW.html three minutes later.
# ----------------------------------------------------------------------

def confirm_template_choice(template_path: Path, auto_confirm: bool) -> int:
    """Print a summary of the chosen template (name, brand colors, layout
    count, registration timestamp) and require explicit Y/N confirmation.

    Returns 0 to proceed, non-zero to abort.

    --confirm-template (auto_confirm=True) skips the prompt for scripted runs.
    Non-TTY stdin without --confirm-template also aborts loudly: orchestrators
    that pipe input must opt in to the flag rather than silently bypass.
    """
    # Load brand + chrome sidecars to surface the facts the operator needs.
    # Both already pass sanity check, so they're guaranteed loadable here.
    try:
        brand = load_brand_sidecar(template_path)
    except Exception as exc:
        sys.stderr.write(f"ERROR: cannot load brand sidecar for confirmation: {exc}\n")
        return 8
    try:
        spec = load_chrome_yml(_p.chrome_yml(template_path))
        layout_count = len(spec.layouts)
    except Exception:
        layout_count = 0

    # theme.json carries the registration timestamp (informational).
    registered_at = "(unknown)"
    try:
        theme_json_path = _p.theme_json(template_path)
        if theme_json_path.exists():
            theme_data = json.loads(theme_json_path.read_text(encoding="utf-8"))
            registered_at = str(theme_data.get("registered_at", "(unknown)"))
    except Exception:
        pass

    print()
    print("=" * 72)
    print("TEMPLATE CONFIRMATION")
    print("=" * 72)
    print(f"  Path           : {template_path}")
    print(f"  File           : {template_path.name}")
    print(f"  Brand primary  : {brand.get('primary_hex', '(unknown)')}")
    print(f"  Brand accent   : {brand.get('accent_hex', '(unknown)')}")
    print(f"  Layouts (chrome.yml): {layout_count}")
    print(f"  Registered     : {registered_at}")
    print("=" * 72)

    if auto_confirm:
        print("  [--confirm-template] auto-confirmed, proceeding.")
        print()
        return 0

    if not sys.stdin.isatty():
        sys.stderr.write(
            "ERROR: template confirmation required but stdin is not a TTY.\n"
            "       Re-run with --confirm-template to acknowledge this is the "
            "intended template.\n"
        )
        return 8

    try:
        ans = input("  Proceed with this template? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        sys.stderr.write("\nERROR: confirmation aborted by user.\n")
        return 8
    if ans not in ("y", "yes"):
        sys.stderr.write("Aborted: template not confirmed. Re-run with the correct --template.\n")
        return 8
    print()
    return 0


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prep a narrative brief for parallel-agent fanout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--brief",    required=False, type=Path, default=None,
                        help="Path to narrative brief markdown. Required for a full build; "
                             "optional with --slide (defaults to the brief recorded in the "
                             "existing _meta.json).")
    parser.add_argument("--template", required=True, type=Path, help="Path to client PPTX template")
    parser.add_argument("--out",      required=True, type=Path, help="Output directory for per-slide prompts")
    parser.add_argument("--slide",    required=False, type=int, default=None,
                        help="Rebuild a single slide in an existing build dir: re-prep only "
                             "slide N, merge into the existing _meta.json, and leave every "
                             "other slide untouched. Reuses the recorded brief unless --brief "
                             "is given. After this, dispatch one worker for slide N, run "
                             "finalize_deck.py --slide N, pick, then re-run compile_picks.py.")
    parser.add_argument("--insert",   required=False, type=int, default=None,
                        help="Insert a NEW slide at position N into an existing build: shift "
                             "slides >= N (dirs, _meta entries, picks) up by one, prep only the "
                             "new slide N, and leave the shifted slides' built output intact. The "
                             "brief (recorded or --brief) must already contain the new slide at "
                             "position N with subsequent slides renumbered (one more slide than "
                             "the current build). Then dispatch one worker for slide N, run "
                             "finalize_deck.py --slide N, pick, and re-run compile_picks.py.")
    parser.add_argument(
        "--client-name",
        default=None,
        help="Override client slug detection. By default, derived from the template's parent directory.",
    )
    parser.add_argument(
        "--confirm-template",
        action="store_true",
        help="Skip the interactive 'is this the right template?' prompt. Use for scripted/CI runs. "
             "When omitted, build_deck halts and asks for Y/N confirmation showing the resolved template name, "
             "brand colors, layout count, and registration timestamp.",
    )
    # Build-path routing override. Per-build override of
    # settings.json::default_pattern. Default None = use settings.json (which
    # ships at "auto").
    parser.add_argument(
        "--pattern",
        choices=["auto", "sketch", "direct", "legacy"],
        default=None,
        help=(
            "Build-path routing override. 'auto' routes per-slide via the "
            "classifier (visual structure -> sketch; bullets/dividers -> "
            "direct). 'sketch' forces every slide through the HTML-first path "
            "(HTML-spec -> native translation). 'direct' forces every slide "
            "through the pptx-direct path (native python-pptx, no HTML stage). "
            "'legacy' uses the pptx-direct-only pipeline. When omitted, "
            "defaults from settings.json::default_pattern (shipped at 'auto')."
        ),
    )
    args = parser.parse_args()

    # Resolve effective pattern from CLI flag + settings.json + ship default.
    # Resolution order:
    #   1. --pattern flag wins outright (if provided)
    #   2. settings.json::default_pattern (read if file exists at skill root)
    #   3. Hard default "legacy" (preserve current behavior)
    # If enable_sketch is False in settings.json, any non-legacy value is
    # downgraded to "legacy" with a stderr warning -- the master switch.
    effective_pattern = _resolve_effective_pattern(args.pattern)

    # Single-slide modes: --slide N (rebuild existing slide N) or --insert N
    # (add a new slide at position N). Both reuse the brief recorded in the
    # existing _meta.json unless --brief overrides it. A full build requires --brief.
    rebuild_slide_n = args.slide
    insert_slide_n = args.insert
    if rebuild_slide_n is not None and insert_slide_n is not None:
        sys.stderr.write("ERROR: use --slide OR --insert, not both.\n")
        return 1
    single_slide_mode = rebuild_slide_n is not None or insert_slide_n is not None
    # The current on-disk slide count (needed by --insert to shift slides); read
    # from the existing manifest below.
    existing_slide_count = 0
    if not single_slide_mode and args.brief is None:
        sys.stderr.write(
            "ERROR: --brief is required for a full build (it may be omitted only "
            "with --slide/--insert, which reuse the recorded brief).\n"
        )
        return 1
    if single_slide_mode:
        _mode_flag = "--slide" if rebuild_slide_n is not None else "--insert"
        _mode_n = rebuild_slide_n if rebuild_slide_n is not None else insert_slide_n
        existing_meta_path = args.out / "_meta.json"
        if not existing_meta_path.exists():
            sys.stderr.write(
                f"ERROR: {_mode_flag} {_mode_n} needs an existing build at {args.out} "
                f"(no _meta.json found). Run a full build first.\n"
            )
            return 2
        try:
            _existing_meta = json.loads(existing_meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            sys.stderr.write(f"ERROR: cannot read {existing_meta_path}: {exc}\n")
            return 2
        existing_slide_count = int(_existing_meta.get("slide_count", 0) or 0)
        if args.brief is None:
            _recorded = _existing_meta.get("brief", "")
            if not _recorded:
                sys.stderr.write(
                    "ERROR: existing _meta.json records no brief path; pass --brief explicitly.\n"
                )
                return 2
            args.brief = Path(_recorded)

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

    # 0.5. TEMPLATE CONFIRMATION GATE — surface what template will drive the
    # build BEFORE any agent dispatch. Wrong-template builds are silent + slow
    # to catch otherwise: every page comes out off-brand and only the operator's
    # eye in REVIEW.html spots it. Show the resolved name + colors + registration
    # timestamp and require explicit OK (--confirm-template flag for scripted
    # runs, or Y/N when stdin is a TTY).
    confirm_rc = confirm_template_choice(args.template, args.confirm_template)
    if confirm_rc != 0:
        return confirm_rc

    # Output dir — only created after sanity check passes
    try:
        args.out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"ERROR: cannot create output directory {args.out}: {exc}\n")
        return 5

    # 1. Read brief
    brief = parse_brief(args.brief, bypass_gate=single_slide_mode)
    slides = brief["slides"]
    slide_total = brief["slide_total"]
    deck_notes = brief["deck_notes"]

    # Validate the rebuild target exists in this brief before any work.
    if rebuild_slide_n is not None:
        valid_ns = [s["slide_n"] for s in slides]
        if rebuild_slide_n not in valid_ns:
            sys.stderr.write(
                f"ERROR: --slide {rebuild_slide_n} is not in the brief "
                f"(slides present: {valid_ns}).\n"
            )
            return 2

    # Validate the insert target + that the brief carries exactly one new slide.
    if insert_slide_n is not None:
        if insert_slide_n < 1 or insert_slide_n > existing_slide_count + 1:
            sys.stderr.write(
                f"ERROR: --insert {insert_slide_n} out of range; the existing build has "
                f"{existing_slide_count} slides, so a new slide can go at positions "
                f"1..{existing_slide_count + 1}.\n"
            )
            return 2
        if slide_total != existing_slide_count + 1:
            sys.stderr.write(
                f"ERROR: --insert expects the brief to contain exactly one more slide than the "
                f"current build ({existing_slide_count + 1}), with the new slide at position "
                f"{insert_slide_n} and later slides renumbered. The brief has {slide_total} "
                f"slides. Add the new slide to the brief and renumber, then re-run.\n"
            )
            return 2

    # 1.5 Resolve every slide's layout name; fail-loud with exit 9
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

    # 4. Load brand sidecar (needed for write_meta_json + per-slide context).
    # Per-client Mermaid theme generation no longer runs here — the sketch
    # path (HTML) supersedes it. Brand-color validation happens at template
    # registration time (Phase 3 interactive color confirmation +
    # register_template.py's WCAG warning).
    # Client slug precedence: CLI --client-name, then the brief's `client_name`
    # front-matter, then derivation from the template's parent directory.
    _fm = brief.get("front_matter", {}) or {}
    _brief_client = (_fm.get("client_name") or _fm.get("client") or "").strip() or None
    client_slug = detect_client_slug(args.template, args.client_name or _brief_client)
    brand = load_brand_sidecar(args.template)

    # No inline theme sanity-check runs here. Validation lives at template
    # registration time (register_template.py Phase 3 + WCAG warning), so
    # theme_warnings stays empty and the dispatch plan carries no theme
    # warnings.
    theme_warnings: list = []

    # Classify per-slide pattern BEFORE rendering prompts (empty dict
    # in legacy mode). The result threads into per-slide _prompt.md via the
    # PATTERN placeholder so the worker knows whether to emit .py (direct path)
    # or .html (sketch path) outputs.
    pattern_per_slide = _classify_all_slides(brief["slides"], effective_pattern)
    if effective_pattern != "legacy":
        sys.stderr.write(
            f"  Build-path routing: effective_pattern={effective_pattern!r}; "
            f"per-slide map = {pattern_per_slide}\n"
        )

    # Insert mode: make room at position N by shifting slides >= N (dirs + picks)
    # up by one BEFORE rendering, so the new slide N renders into the freed slot
    # and the shifted slides keep their built output. Must run before the render.
    if insert_slide_n is not None:
        try:
            _shift_build_for_insert(args.out, insert_slide_n, existing_slide_count)
        except OSError as exc:
            sys.stderr.write(f"ERROR: could not shift build for insert: {exc}\n")
            return 5

    # 5. Render per-slide prompts. In single-slide modes, render only the target
    # slide and leave every other slide's prompt/context/meta untouched.
    target_slide_n = rebuild_slide_n if rebuild_slide_n is not None else insert_slide_n
    template_text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    render_targets = [
        (slide, seeds) for slide, seeds in zip(slides, seeds_by_slide)
        if target_slide_n is None or slide["slide_n"] == target_slide_n
    ]
    for slide, seeds in render_targets:
        slide_n = slide["slide_n"]
        slide_dir = _p.slide_dir(args.out, slide_n)
        slide_dir.mkdir(parents=True, exist_ok=True)
        likely_prior = format_prior_patterns(slide_n, forecasts)
        # Build-path routing for this slide: sketch = HTML output,
        # direct = python-pptx. Unrouted slides default to direct.
        slide_pattern = pattern_per_slide.get(str(slide_n), "direct")
        placeholders = build_placeholders(
            slide=slide,
            slide_total=slide_total,
            deck_notes=deck_notes,
            client_template_path=args.template.resolve(),
            output_dir=slide_dir.resolve(),
            seeds=seeds,
            likely_prior_patterns=likely_prior,
            slide_pattern=slide_pattern,
        )
        rendered = render_prompt(template_text, placeholders)
        _p.prompt_md(args.out, slide_n).write_text(rendered, encoding="utf-8")
        # Write a `_context.md` sibling that bundles the canonical reference,
        # design rules, brief metadata, and feedback ledger for the
        # per-slide worker agent to reason against.
        try:
            write_slide_context_md(slide, brand, slide_dir, slide_n)
        except Exception as _exc:
            sys.stderr.write(
                f"  WARN: could not write slide {slide_n} _context.md: "
                f"{type(_exc).__name__}: {_exc}\n"
            )

    # Rebuild mode: merge only the target slide's entry into the existing
    # _meta.json and stop. Every other slide's prompt, context, themed PPTX,
    # and meta entry (including artifacts) are preserved. The operator then
    # dispatches one worker for slide N, runs finalize_deck.py --slide N, picks,
    # and re-runs compile_picks.py to graft the rebuilt slide into final_deck.pptx.
    if rebuild_slide_n is not None:
        meta_path = update_meta_for_rebuild(
            out_dir=args.out,
            brief=brief,
            slide_n=rebuild_slide_n,
            forecasts=forecasts,
            pattern_per_slide=pattern_per_slide,
        )
        if meta_path is None:
            return 2
        rb_dir = _p.slide_dir(args.out, rebuild_slide_n)
        print(f"Re-prepped slide {rebuild_slide_n} at:")
        print(f"  {rb_dir.resolve()}")
        print()
        print(f"Updated deck manifest:")
        print(f"  {meta_path.resolve()}")
        print()
        print(f"Next, to rebuild slide {rebuild_slide_n} end to end:")
        print(f"  1. Dispatch ONE slide-builder-worker for slide {rebuild_slide_n} "
              f"(reads {rb_dir / '_context.md'} then {rb_dir / '_prompt.md'}).")
        print(f"  2. py -3 finalize_deck.py --out <out> --template <template> --slide {rebuild_slide_n}")
        print(f"  3. Take the user's pick for slide {rebuild_slide_n}; update picks.json.")
        print(f"  4. py -3 compile_picks.py --out <out>   # grafts the new slide into final_deck.pptx")
        return 0

    # Insert mode: dirs + picks were already shifted; splice the new slide's entry
    # into _meta.json (shifting existing entries >= N) and bump slide_count. Every
    # shifted slide's prompt/context/themed PPTX is preserved under its new number.
    if insert_slide_n is not None:
        meta_path = update_meta_for_insert(
            out_dir=args.out,
            brief=brief,
            insert_n=insert_slide_n,
            forecasts=forecasts,
            pattern_per_slide=pattern_per_slide,
            old_count=existing_slide_count,
        )
        if meta_path is None:
            return 2
        ins_dir = _p.slide_dir(args.out, insert_slide_n)
        print(f"Inserted new slide {insert_slide_n} (build now has {existing_slide_count + 1} slides):")
        print(f"  {ins_dir.resolve()}")
        print()
        print(f"Updated deck manifest:")
        print(f"  {meta_path.resolve()}")
        print()
        print(f"Next, to build the inserted slide {insert_slide_n} end to end:")
        print(f"  1. Dispatch ONE slide-builder-worker for slide {insert_slide_n} "
              f"(reads {ins_dir / '_context.md'} then {ins_dir / '_prompt.md'}).")
        print(f"  2. py -3 finalize_deck.py --out <out> --template <template> --slide {insert_slide_n}")
        print(f"  3. Take the user's pick for slide {insert_slide_n}; add it to picks.json.")
        print(f"  4. py -3 compile_picks.py --out <out>   # grafts the full renumbered deck")
        return 0

    # Deck manifest (_meta.json) — single source of truth for downstream
    # pipeline scripts. Writes AFTER slide prompts are rendered so that any
    # exception in render_prompt aborts before the manifest claims success.
    meta_path = write_meta_json(
        out_dir=args.out,
        brief_path=args.brief,
        brief=brief,
        template_path=args.template,
        client_slug=client_slug,
        forecasts=forecasts,
        brand=brand,
        effective_pattern=effective_pattern,
        pattern_per_slide=pattern_per_slide,
    )

    # Dispatch plan
    plan_path = write_dispatch_plan(
        out_dir=args.out,
        slides=slides,
        forecasts=forecasts,
        client_slug=client_slug,
        theme_warnings=theme_warnings,
        brief_path=args.brief.resolve(),
        client_template_path=args.template.resolve(),
    )

    # Console summary (paths as plain text)
    print(f"Prepped {slide_total} slides at:")
    print(f"  {args.out.resolve()}")
    print()
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
    print("Next: dispatch one slide-builder-worker agent per slide in parallel.")
    print("Each worker reads _context.md first, then _prompt.md in its slide_NN/")
    print("directory. Then run finalize_deck.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
