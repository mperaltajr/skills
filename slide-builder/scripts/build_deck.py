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

Remove a slide (the reverse of --insert; take it out of the brief and
renumber the later slides first):
    py -3 build_deck.py --delete N --out <output_directory> [--brief <brief.md>]
  The folder and its records go to _session/removed_slides/ (never deleted),
  every slide-numbered record is renumbered, the slide id is retired, the
  user's rulings on it are listed for them to move or retire, the final check
  is cleared and the next QC reads every page. Exit 3: a sealed brief could
  not be sealed again; exit 5: a folder in use (nothing was changed).

Exit codes:
    0  Success.
    1  Brief file missing, unreadable, or empty.
    2  Brief has no parseable slides (or an invalid --slide/--insert/--delete request).
    3  Client template missing.
    4  prompt.md template missing or malformed.
    5  Output directory cannot be created.
    7  Stage-1 sanity check failed — prerequisite missing.
       The client template is not registered (BrandSidecarMissing — run
       slide-builder/scripts/register_template.py). Halts at prep time
       before agent dispatch costs are sunk.
    8  (retired) Was the interactive template prompt, which nobody could
       answer from inside Claude Code; it always aborted.
    9  Layout resolution failed — a slide's layout could not be resolved
       against the template's registered layouts (emit_layout_resolution_error).
   10  Storyline gate failed — the narrative brief did not pass the quality
       gate (bypassed by mode: template-fill / rebuild-slice / rfp).
   12  The template has not been confirmed by a human (register_template.py
       confirm). Override, logged in _state.json: --allow-unconfirmed.

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


import _paths as _p
import _visuals  # noqa: E402
import icon_names  # noqa: E402  (the one icon lookup; topics offered per slide)
import _state  # noqa: E402  (build state manifest: prep record + review invalidation)
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
    # storyline-helper writes "## Deck-level design notes (optional)"; the old
    # pattern needed the line to end at "notes", so every deck lost its notes.
    r"^##\s+Deck[\s\-]?level\s+design\s+notes\b[^\n]*\n(.*?)(?=^#{1,3}\s|\Z)",
    re.MULTILINE | re.IGNORECASE | re.DOTALL,
)
# Any `## ` section and its body (to the next H1-H3 heading).
H2_SECTION_RE = re.compile(r"^##\s+([^\n]+?)\s*\n(.*?)(?=^#{1,3}\s|\Z)",
                           re.MULTILINE | re.DOTALL)
# Other headings that also mean "rules for every page". A brief once named its
# section "Section content rules (binding on every page)"; prep read only the
# exact "Deck-level design notes" heading, so a dozen binding rules reached no
# designer (2026-10-08). Matched against _heading_key(heading).
DECK_NOTES_HEADING_RES = (
    re.compile(r"\bdesign\s+notes\b"),
    re.compile(r"^(?:deck[\s\-]*(?:level|wide)\s+)?(?:section\s+)?"
               r"(?:design|content|style|writing|build|page|slide)\s+"
               r"(?:notes|rules|conventions|constraints|guidelines)$"),
    re.compile(r"^deck[\s\-]*(?:level|wide)?\s*(?:notes|rules|conventions|constraints|guidelines)$"),
    re.compile(r"^(?:rules|notes|conventions)\s+for\s+every\s+(?:page|slide)$"),
)
# Deck-level sections prep knows (read, or deliberately not needed by the
# designers). Any other `##` section gets a warning at prep.
KNOWN_DECK_SECTIONS = (
    "sequence", "deck type", "narrative framework", "strategic framework",
    "governing thought", "audience", "flags", "open gaps",
)

# Bold-labeled field lines: **Label:** value (one-line)  OR  **Label:**\nblock
FIELD_LABELS = {
    "title":               ("slide title",),
    # "slide type" is the user-facing label; "archetype" still parses (older briefs).
    "archetype":           ("slide type", "archetype"),
    "layout":              ("layout",),  #
    "variant":             ("variant",),  # "dark" triggers dark-background variant
    "governing_thought":   ("governing thought", "governing thought (the claim)"),
    # "the takeaway" is the user-facing label; "so-what" variants still parse.
    "so_what":             ("the takeaway", "so-what", "so what", "so-what (the takeaway)"),
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
    # A page the user handed over to be KEPT (a one-pager, a mockup). Recorded
    # in _meta.json so it cannot be quietly replaced by a summary of it, which
    # is how a supplied one-pager once became an exec summary nobody asked for.
    "pinned_source_page":  ("pinned source page", "supplied page"),
    # The page's source line (for the template's Source slot / footer) and the
    # small section tag above the title. Briefs wrote both as fields of their
    # own; prep did not read them, so designers never saw them and pages went
    # out with no source (2026-10-08).
    "source":              ("source", "sources", "source line"),
    "section_tag":         ("section tag", "section label"),
    # The slide's fixed id (slide_ids.py writes it when the storyline is
    # approved; owner's decision 2026-10-14). Numbers move when a slide is
    # inserted; the id never does, so rulings stay on the right page.
    "slide_id":            ("slide id",),
    # A section divider's one line (clone_pages.py, 2026-10-14). Optional: the
    # takeaway or the first bullet stands in when it is absent.
    "section_description": ("section description",),
    # The slide's visual, chosen on the Storyline tab of the Slide Lab page
    # (record_storyline.py; owner's decision 2026-10-16): "<name> | suggestion"
    # or "<name> | must use", the user's note on it, the chat's one line on
    # what it shows, and where the slide starts from when pages were supplied.
    "visual":              ("visual",),
    "visual_note":         ("visual note",),
    "visual_shows":        ("visual shows",),
    "reuse":               ("reuse",),
}

# Bold labels a slide block may carry that prep knows but does not pass on as
# a field of its own: cover and closing-page items written inside the content.
# Any other label is warned about at prep instead of being dropped silently.
KNOWN_EXTRA_LABELS = (
    "title", "tagline", "subtitle", "presenter", "date", "audience / client",
    "audience", "client", "eyebrow", "eyebrow (optional)", "primary ask", "sub-asks",
    "page type",
)


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
        # This computer's settings.local.json wins (_paths.settings()).
        return {**raw, **_p.settings()}
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
    # These messages deliberately do NOT print a command that gets past the gate.
    # They used to print the seal command and the mode: lines, and an orchestrator
    # in a hurry followed them, which turned the gate into a different command to
    # type. The way past is the user: they run the gate, or they say to build
    # without it, which is --assume-gated and is shown at delivery.
    _ask = ("  What to do: run storyline-helper's quality gate on the brief; it seals\n"
            "  the brief when the gate passes. If the user wrote this brief in this\n"
            "  session and tells you to build it without the gate, use --assume-gated:\n"
            "  it is recorded and shown to the user when the deck is delivered.\n"
            "  Do not seal the brief yourself without running the gate.\n")
    if passed_raw in ("true", "yes", "1"):
        # Owner's decision (2026-09-30): the marker must be proven, not typed.
        # seal_brief.py writes a fingerprint of the brief (front matter and text)
        # when the gate passes; a typed marker has none, and any edit breaks it.
        from seal_brief import brief_fingerprint
        sealed = (front_matter.get("storyline_gate_sha") or "").strip()
        if not sealed:
            sys.stderr.write(
                "ERROR: the brief says it passed the storyline gate, but it was never "
                "sealed, so nothing shows the gate actually ran.\n\n"
                f"  Brief: {brief_path}\n\n" + _ask)
            sys.exit(10)
        # Either fingerprint: today's (slide id and pinned-page lines not
        # counted) or the one seals used before 2026-10-14.
        if sealed not in (brief_fingerprint(front_matter, body),
                          brief_fingerprint(front_matter, body, legacy=True)):
            sys.stderr.write(
                "ERROR: the brief changed after it passed the storyline gate.\n\n"
                f"  Brief: {brief_path}\n\n" + _ask)
            sys.exit(10)
        return
    sys.stderr.write(
        "ERROR: the brief has not been through storyline-helper's quality gate.\n\n"
        f"  Brief: {brief_path}\n\n" + _ask)
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


def _heading_key(heading: str) -> str:
    """A `##` heading reduced for matching: no "(...)" note, nothing after a
    dash or colon ("Flags — live issues" is "flags"), lower case."""
    h = re.sub(r"\([^)]*\)", " ", heading)
    h = re.split(r"\s[—–]\s|:|\s-\s", h)[0]
    h = re.sub(r"[^\w\s/\-]", " ", h)
    return " ".join(h.lower().split())


def is_deck_notes_heading(heading: str) -> bool:
    """True when a `##` heading names the deck-wide design or content rules."""
    if re.search(r"binding\s+on\s+every\s+(?:page|slide)", heading, re.I):
        return True
    key = _heading_key(heading)
    return any(r.search(key) for r in DECK_NOTES_HEADING_RES)


def extract_deck_notes(body: str) -> str:
    """The deck-wide design notes: every `##` section whose heading names them
    ("Deck-level design notes", "Section content rules (binding on every
    page)", "Deck rules", ...), joined in brief order."""
    parts = []
    for m in H2_SECTION_RE.finditer(body):
        heading, text = m.group(1).strip(), m.group(2).strip()
        if re.match(r"^Slide\s+\d+", heading, re.I) or not text:
            continue
        if is_deck_notes_heading(heading):
            parts.append(text if not parts else f"({heading})\n{text}")
    return "\n\n".join(parts)


def brief_warnings(body: str, blocks: list) -> list[str]:
    """Sections and slide fields prep does not read. Prep used to drop them
    without a word, so the designers never saw them and nobody knew."""
    out = []
    for m in H2_SECTION_RE.finditer(body):
        heading = m.group(1).strip()
        if re.match(r"^Slide\s+\d+", heading, re.I) or is_deck_notes_heading(heading):
            continue
        key = _heading_key(heading)
        if any(key == k or key.startswith(k + " ") for k in KNOWN_DECK_SECTIONS):
            continue
        out.append(f'section "## {heading}" is not one prep reads, so no designer will '
                   f'see it. If it holds rules for every page, name it "## Deck-level '
                   f'design notes"; otherwise move what matters into the slides\' fields.')
    known = {lab for labs in FIELD_LABELS.values() for lab in labs} | set(KNOWN_EXTRA_LABELS)
    label_re = re.compile(r"^[ \t]*\*\*([^*\n]{1,60}?)\s*(?::\s*\*\*|\*\*\s*:)", re.M)
    seen: dict[str, list[int]] = {}
    for slide_n, _title, block in blocks:
        # The last slide's block runs to the end of the brief; stop at the
        # next deck-level heading (the Flags section has fields of its own).
        block = re.split(r"(?m)^#{1,2}\s", block)[0]
        for lm in label_re.finditer(block):
            lab = lm.group(1).strip()
            if " ".join(lab.lower().split()) not in known:
                ns = seen.setdefault(lab, [])
                if slide_n not in ns:
                    ns.append(slide_n)
    for lab, ns in seen.items():
        out.append(f'field "**{lab}:**" (slide {", ".join(str(n) for n in ns)}) is not one '
                   f"prep reads, so the designer will not see it. Put it under **Evidence / "
                   f"content:** or **Editorial emphasis:**, or use a field from "
                   f"storyline-helper's brief format.")
    return out


def extract_deck_section(body: str, *heading_aliases: str) -> str:
    """Extract the body text under a deck-level `## <heading>` section.

    Used for deck-level fields that storyline-helper writes as `##` headings
    rather than YAML front-matter (governing thought, audience). Tries each
    alias in order; returns the first non-empty match, or "".

    Section runs from the matched `## heading` to the next H1-H3 boundary.
    """
    for alias in heading_aliases:
        pat = re.compile(
            r"^##\s+" + re.escape(alias) + r"(?:\s*\([^\n]*\))?\s*\n(.*?)(?=^#{1,3}\s|\Z)",
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

    A value also ends at a `---` divider line or a markdown heading. Without
    that, the LAST field of a slide (usually **Chart type:** none) swallowed
    the divider, and on the last slide the brief's Flags section too, so
    "none" never matched and every slide was forecast as a chart.
    """
    for label in labels:
        pattern = re.compile(
            rf"\*\*{re.escape(label)}\s*:?\s*\*\*\s*(.*?)"
            rf"(?=\n\s*\*\*[A-Za-z]|\n[ \t]*-{{3,}}[ \t]*(?:\n|\Z)|\n#{{1,6}}\s|\Z)",
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
            "pinned_source_page": extract_field(block, FIELD_LABELS["pinned_source_page"]),
            "source": " ".join(extract_field(block, FIELD_LABELS["source"]).split()),
            "section_tag": " ".join(extract_field(block, FIELD_LABELS["section_tag"]).split()),
            "slide_id": extract_field(block, FIELD_LABELS["slide_id"]).strip("` ").lower(),
            "section_description": " ".join(
                extract_field(block, FIELD_LABELS["section_description"]).split()),
            "visual": " ".join(extract_field(block, FIELD_LABELS["visual"]).split()),
            "visual_note": " ".join(extract_field(block, FIELD_LABELS["visual_note"]).split()),
            "visual_shows": " ".join(extract_field(block, FIELD_LABELS["visual_shows"]).split()),
            "reuse": " ".join(extract_field(block, FIELD_LABELS["reuse"]).split()),
        }
        slides.append(slide)
    _dupes = sorted({s["slide_id"] for s in slides if s["slide_id"]
                     and sum(1 for t in slides if t["slide_id"] == s["slide_id"]) > 1})
    if _dupes:
        sys.stderr.write(
            "ERROR: two slides of the brief have the same slide id: "
            + ", ".join(_dupes) + ". Ids must be unique; run "
            f"py -3 scripts/slide_ids.py --brief \"{brief_path}\" --check to list them, "
            "fix the brief, and run this again.\n")
        sys.exit(2)

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
        "warnings": brief_warnings(body, blocks),
        "deck_governing_thought": deck_governing_thought,
        "deck_audience": deck_audience,
        "slides": slides,
        "slide_total": len(slides),
        "brief_path": str(brief_path),
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

## 0. The deck this slide belongs to

- **Main message of the deck:** {deck_message}
- **Audience:** {deck_audience}
- **Every slide in the deck** (yours is marked):
{deck_titles}

Make this slide's own point; do not repeat another slide's point. Keep tables,
charts, numbering and labels in the same style as the rest of the deck would
expect (one way of writing each kind of number across all slides).

## 1. Canonical reference (from brand.yml)

{reference_block}

## 2. Design rules — soft constraints

- **Title wrap (HARD LIMIT):** the title must fit inside its title box. If it
  wraps to more lines than the box holds, the build **hard-fails at finalize**
  (a longer title would overlap the heading band / body — measured with the
  brand font, so it reflects PowerPoint, not the preview). At >2 lines the slide
  also drops its subtitle automatically. Keep titles to ≤2 visual lines and
  shorten an over-long title rather than counting on it to fit.
- **Takeaway fit:** keep the takeaway to one line; § 3 gives this layout's
  takeaway size and about how many characters a line holds.
- **Accent placement:** every chart's legend is one row at the top right of
  the chart, on the chart's header line, right-aligned to the chart's right
  edge (owner's rule, 2026-10-09); never below the chart, never stacked at
  the side. A chart with one series has no legend. Top/bottom invariant
  zones hold sources/footnotes/page numbers only: NO
  ACCENTURE/DRAFT/CONFIDENTIAL tags.
- **Chart header line (owner's rule, 2026-10-09):** every chart has a header
  line at its top left, starting at the chart's left edge: "Chart title,
  Unit", e.g. "Who owns the GPUs that retire, M GPUs": the title bold, the
  comma and the unit regular weight, the unit written plainly after the
  comma (no square brackets, no parentheses; corrected 2026-10-13), an
  optional footnote mark right after the title as a superscript digit (the
  characters ¹ ² ³). Name it `chart-title` (`chart-title-2` for a
  second chart), the legend pieces `chart-legend-<series>` and
  `chart-legend-swatch-<series>`, axis titles `chart-axis-title-x` /
  `chart-axis-title-y`, and every other chart piece `chart-...`. QC flags a
  missing header line, a missing unit, a unit in brackets and a misplaced
  legend as Major.
- **Title bottom-anchor:** title bottom-y is fixed; 2-line titles grow
  UPWARD into the chrome zone, never displacing the subtitle.
- **No inline run formatting on placeholders.** Title/subtitle inherit
  fonts and colors from the master theme. Workers should not bake in
  hardcoded colors. On a sketch the title, takeaway and section tag are
  styled by the pipeline (§ 3): mark them, don't style them.
- **Charts tell the truth (QC flags these as Major):** bars and areas start at
  zero; every value axis has a title with its unit; a number called out in the
  title or a callout appears on the chart itself; one unit per kind of figure
  across the deck ($1.2B on every slide, never $1,200M on the next one).
- **Facts, not adjectives:** write only words and numbers from the brief.
  Labels, eyebrows and callouts reuse the brief's wording; no new claims, no
  buzzwords (see `reference/banned-words.md`).
- **No final periods (owner's rule, 2026-10-09):** no text item ends with a
  period (titles, takeaways, labels, bullets, panel text, callouts, table
  cells, chart labels, footnotes, sources). Keep periods between sentences,
  never at the end. Finalize removes any final period left and lists each
  one in the report; QC flags one that remains as Major.

## 3. This slide's brief metadata

- Title: {title!r} ({title_len} chars)
- So-what: {so_what!r} ({so_what_len} chars)
- Archetype: {archetype!r}
- Editorial emphasis: {emphasis!r}
- Layout: {layout!r}
- Source line: {source!r} (goes in the `data-template-field="footer"` element on a
  sketch, `add_footer(source=...)` on the direct path; never invent one)
- Section tag: {section_tag!r} (Slide Lab draws it; do not draw it. Finalize puts it
  just above the title in the template's fixed style)
{body_geometry}

**Title, takeaway and section tag on this layout (styled by Slide Lab, 2026-10-13):**

{chrome_block}

On a sketch, mark the title `data-template-field="title"` and the takeaway
`data-template-field="subtitle"`, and do not style them (no font, size,
color or position rules for them, and no section tag at all). Slide Lab adds
`_chrome.css` (next to this file) last when it draws the picture, so every
sketch shows the template's real title, takeaway and section tag, exactly as
finalize puts them on the slide. Design the body for that: it starts at
`--body-top`.

## 4. QC anchor

The compiled deck will be QC'd by the `slide-qc` skill, which does
zone-by-zone vision review of every rendered slide. Every output slide should
match the template's chrome (top/bottom bands, footer geometry, title/subtitle
position) and respect the canonical palette ({primary_hex} / {accent_hex}).

## 5. Feedback ledger (prior rejections for this slide)

{prior_feedback}
"""


def _format_reference_block_for_context(brand: dict) -> str:
    ref = brand.get("reference_slide") if isinstance(brand, dict) else None
    if not ref or not isinstance(ref, dict):
        return (
            "_No reference slide was captured at registration. Follow the "
            "template's own layout (geometry below) and the skill's hardline "
            "rules and anti-pattern library._"
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


def _style_refs_block(template_path) -> str:
    """Pictures of real pages from the client's own deck, when the template has
    them (<template stem>/style_refs/*.png, added with add_style_refs.py).

    Without them, designers had only colors and box positions to go on and fell
    back to generic cards and tables; the client's response to one round was
    "definitely look Claude generated" and "generic cards"."""
    try:
        refs = sorted(_p.style_refs_dir(Path(template_path)).glob("*.png")) if template_path else []
    except Exception:
        refs = []
    if not refs:
        return ("\n\n_No client style references for this template. If the template "
                "came from a real client deck, add 3-4 of its best pages with "
                "`scripts/add_style_refs.py` so designs match the client's look._")
    lines = ["", "", "**Client style references (look at these images first):**", ""]
    lines += [f"- `{r}`" for r in refs[:6]]
    lines += ["",
              "These are real pages from the client's own deck. Open each image before "
              "designing and match their visual language: how they number steps, use "
              "icons, draw charts and diagrams, label things, how dense a page is, and "
              "where color goes. Do NOT copy their text, numbers or layout one-to-one; "
              "the content comes only from the brief. A design that could belong to any "
              "company is the failure to avoid."]
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


# How many agents the parent session can have running at once. Dispatches past
# this are rejected, and the rejection is quiet: on one 29-slide deck about 20
# of them vanished and finalize exited 11 with slides 23-29 missing.
MAX_CONCURRENT_AGENTS = 20

_CHROME_SPEC_CACHE: dict = {}


def _body_geometry_block(template_path, layout_name: str) -> str:
    """The authoritative body zone for this slide's layout, as a :root block.

    reference/sketch-html-spec.md has long asserted that prep inlines this into
    _context.md. It did not. Workers were told to "use the body zone" with no
    numbers anywhere in _context.md or _prompt.md, so they guessed: on one real
    deck 123 options read chrome.yml themselves and got it right, and 9 copied
    the `149px` out of the spec's ILLUSTRATIVE example, a number belonging to a
    different template. Emit the real numbers, from the same resolver finalize
    uses, so the graft zone is reserved before anything is authored.
    """
    if not template_path or not layout_name:
        return ""
    try:
        from twins.helpers import body_zone_for_chrome  # noqa: E402
        key = str(template_path)
        if key not in _CHROME_SPEC_CACHE:
            _CHROME_SPEC_CACHE[key] = load_chrome_yml(_p.chrome_yml(Path(template_path)))
        lc = _CHROME_SPEC_CACHE[key].layouts.get(layout_name)
        if lc is None:
            return ""
        top, bot = body_zone_for_chrome(lc)
    except Exception:
        return ""   # never break prep over a context nicety
    # The layout's own background and side margins: chrome.yml's record, else
    # read from the template now (no re-registration needed). Designs used to
    # be drawn on a fixed white canvas with no side margins given, so a pale
    # panel vanished on a gray-blue master and panels ran past the template's
    # right margin (2026-10-06).
    facts = {}
    try:
        import _template_bg as _tbg
        facts = _tbg.facts_for(template_path, layout_name, lc)
    except Exception:
        facts = {}
    bg = facts.get("bg_hex") if facts.get("bg_kind") != "picture" else None
    css = [f"  --body-top: {top}px;      /* first body shape starts at or below this */",
           f"  --body-bottom: {bot}px;   /* last body shape ends at or above this */",
           f"  --body-height: {bot - top}px;"]
    if facts.get("left") is not None and facts.get("right") is not None:
        css += [f"  --body-left: {facts['left']}px;    /* the template's left margin */",
                f"  --body-right: {facts['right']}px;  /* the template's right margin */"]
    if bg:
        css.append(f"  --slide-canvas-bg: #{bg};  /* this layout's own background */")
    notes = ["The grafted title and takeaway line own everything above `--body-top`. "
             "Anything you place above it will be collided with after the graft, which "
             "no pre-graft preview can show you."]
    if facts.get("left") is not None and facts.get("right") is not None:
        notes.append("Keep body content between `--body-left` and `--body-right`: those "
                     "are the template's own side margins (its title and text area).")
    if bg:
        approx = (" It is the first color of the layout's "
                  f"{facts.get('bg_kind')} background, so treat it as approximate."
                  if facts.get("bg_kind") in ("gradient", "pattern", "theme-style") else "")
        notes.append(f"Paint `.slide-canvas` with `var(--slide-canvas-bg)` (#{bg}): it is "
                     "the template's own background on this layout, so the sketch shows "
                     "what the slide will look like, and the converter leaves it to the "
                     "template instead of covering the master's artwork. Copy this value "
                     "over the one in brand.css. A panel within a few shades of it will "
                     "barely show: give panels a clearly different fill or an outline."
                     + approx)
    elif facts.get("bg_kind") == "picture":
        notes.append("This layout's background is a picture. Keep `.slide-canvas` "
                     "unpainted (white) and keep body panels opaque so they read on it.")
    return (
        "\n**Body zone for this layout (authoritative, use these numbers, do not guess):**\n\n"
        "```css\n:root {\n" + "\n".join(css) + "\n}\n```\n\n"
        + "\n\n".join(notes) + "\n"
    )


_CHROME_PRS_CACHE: dict = {}


def _slide_chrome_style(template_path, slide: dict, brand: dict):
    """The template's title, takeaway and section tag for this slide's
    layout, as finalize will style them (twins/chrome_rules.chrome_style);
    None for a cover, divider or other art-directed layout, or when the
    template's sidecars cannot be read."""
    layout_name = (slide.get("layout") or "").strip()
    if not template_path or not layout_name:
        return None
    from pptx import Presentation
    from twins.chrome_rules import chrome_style, template_takeaway_pt
    from twins.client_theme import resolve_build_template
    key = str(template_path)
    if key not in _CHROME_SPEC_CACHE:
        _CHROME_SPEC_CACHE[key] = load_chrome_yml(_p.chrome_yml(Path(template_path)))
    spec = _CHROME_SPEC_CACHE[key]
    lc = spec.layouts.get(layout_name)
    if lc is None:
        return None
    if key not in _CHROME_PRS_CACHE:
        prs = Presentation(str(resolve_build_template(Path(template_path))))
        _CHROME_PRS_CACHE[key] = (prs, template_takeaway_pt(prs, spec))
    prs, deck_takeaway_pt = _CHROME_PRS_CACHE[key]
    page_type = ((slide.get("page_type") or "").strip()
                 or _normalize_archetype_to_page_type(slide.get("archetype") or ""))
    on_dark = True if (slide.get("variant") or "").strip().lower() == "dark" else None
    return chrome_style(lc, prs, brand.get("accent_hex") or "", on_dark=on_dark,
                        page_type=page_type, takeaway_pt=deck_takeaway_pt,
                        section_tag=(slide.get("section_tag") or "").strip())


def _write_chrome_css(slide: dict, brand: dict, slide_dir: Path, template_path,
                      slide_n=None) -> str:
    """Write slide_NN/_chrome.css (render_html.py adds it last when it draws
    the sketch) and return the plain-words block for _context.md. A layout
    with no fixed chrome gets no sheet (an old one is removed)."""
    css_path = slide_dir / "_chrome.css"
    try:
        style = _slide_chrome_style(template_path, slide, brand)
    except Exception as exc:  # noqa: BLE001 -- never break prep over the preview styling
        sys.stderr.write(f"  WARN: could not read the template's title and takeaway style for "
                         f"slide {slide_n}: {type(exc).__name__}: {exc}. The sketch "
                         f"pictures will show the designer's own styling; finalize still styles "
                         f"the slide. Re-register the template if this repeats.\n")
        style = None
    if style is None:
        if css_path.exists():
            css_path.unlink()
        return ("This layout keeps its own art-directed title and lines (a cover, "
                "divider or similar): design them as the layout shows them.")
    from twins.chrome_rules import chrome_css, chrome_plain_words
    css_path.write_text(chrome_css(style), encoding="utf-8")
    return chrome_plain_words(style)


def _deck_titles_block(deck: dict | None, slide_n: int) -> str:
    rows = []
    for s in (deck or {}).get("slides") or []:
        n = s.get("slide_n")
        mark = "  <- this slide" if n == slide_n else ""
        rows.append(f"  {n}. {(s.get('title') or '').strip()}{mark}")
    return "\n".join(rows) or "  (not available)"


def _add_context_pack(content: str, slide: dict, slide_dir: Path,
                      deck: dict | None) -> str:
    """Put the slide's context pack (sources, number trail, the user's rulings
    in their exact words) into _context.md, on every dispatch (owner's
    decision, 2026-10-14). Never stops prep: without it the designer still has
    the brief."""
    try:
        import _context_pack
        content, dropped = _context_pack.drop_chat_direction(content)
        if dropped:
            print(f"  WARNING: slide {slide.get('slide_n')}: {slide_dir / '_prior_feedback.md'} "
                  f"has {dropped} hand-written \"Direction from the user\" block(s). They were "
                  "left out of _context.md: the user's direction reaches designers only in "
                  "their exact words. Record each point with py -3 scripts/add_ruling.py --out "
                  f"\"{slide_dir.parent}\" --id <slide id> --topic <topic> --quote \"<their "
                  "words>\" --reading \"<what you understood>\", delete the block, and prep "
                  "this slide again.")
        return _context_pack.put_pack(content, _context_pack.pack_block(
            slide_dir.parent, slide, brief=(deck or {}).get("brief_path")))
    except Exception as exc:
        print(f"  WARN: slide {slide.get('slide_n')}: could not add the rulings pack to "
              f"_context.md ({type(exc).__name__}: {exc})")
        return content


def write_slide_context_md(slide: dict, brand: dict, slide_dir: Path,
                            slide_n: int, template_path=None,
                            deck: dict | None = None) -> Path:
    """Write `_context.md` next to `_prompt.md` for the per-slide worker
    agent, hydrating any recorded prior feedback for the slide. `deck` is the
    parsed brief: designers used to see only their own slide, with no main
    message, audience or neighbours."""
    title = (slide.get("title") or "").strip()
    so_what = (slide.get("so_what") or "").strip()
    archetype = (slide.get("archetype") or "").strip()
    emphasis = (slide.get("editorial_emphasis") or "").strip()
    layout = (slide.get("layout") or "").strip()
    fm = (deck or {}).get("front_matter") or {}
    content = CONTEXT_TEMPLATE.format(
        slide_n=slide_n,
        deck_message=(((deck or {}).get("deck_governing_thought") or fm.get("governing_thought")
                       or "(not given)").strip().strip('"')),
        deck_audience=(" ".join(((deck or {}).get("deck_audience") or fm.get("audience")
                                 or "(not given)").replace("**", "").split())[:400]),
        deck_titles=_deck_titles_block(deck, slide_n),
        reference_block=(_format_reference_block_for_context(brand)
                         + _style_refs_block(template_path)),
        title=title,
        title_len=len(title),
        so_what=so_what,
        so_what_len=len(so_what),
        archetype=archetype,
        emphasis=emphasis,
        layout=layout,
        source=(slide.get("source") or "").strip() or "(none in the brief)",
        section_tag=(slide.get("section_tag") or "").strip() or "(none)",
        body_geometry=_body_geometry_block(template_path, layout),
        chrome_block=_write_chrome_css(slide, brand, slide_dir, template_path, slide_n),
        primary_hex=brand.get("primary_hex", "(unset)"),
        accent_hex=brand.get("accent_hex", "(unset)"),
        prior_feedback=_load_prior_feedback_for_slide(slide_dir),
    )
    content = _add_context_pack(content, slide, slide_dir, deck)
    if (slide.get("visual") or slide.get("reuse") or "").strip():
        # The user's visual choice from the Storyline tab (2026-10-16).
        content += ("\n\n## The visual the user chose (Storyline tab)\n\n"
                    + visual_directive(slide) + "\n")
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
    # Keep only the instructions for this slide's build path. Each designer
    # used to read both paths' rules (about 29 KB), half of them irrelevant.
    path = str(placeholders.get("PATTERN") or "").strip().lower()
    if path in ("direct", "sketch"):
        other = "sketch" if path == "direct" else "direct"
        body = re.sub(r"<!-- only:%s -->.*?<!-- /only -->\n?" % other, "", body, flags=re.S)
        body = re.sub(r"<!-- /?only(?::%s)? -->\n?" % path, "", body)
    for token, value in placeholders.items():
        body = body.replace("{{" + token + "}}", str(value))
    return body


def density_directive(front_matter: dict[str, Any]) -> str:
    """The per-deck content-density instruction threaded to the worker.

    Default (ALL decks): fill the page — a content slide must be useful on its
    own. Slides rendered near-empty (a few words on a full canvas) were the
    recurring complaint. An explicit `density: executive` (or sparse/minimal)
    front-matter opts a genuinely minimal deck back into headline-led sparseness.
    This never overrides brief fidelity — the worker renders what the brief
    supplies richly and still never fabricates beyond it.
    """
    density = (front_matter.get("density") or "").strip().lower()
    if density in ("executive", "sparse", "minimal"):
        return ("Executive / sparse deck (density: {d}). Lead with the headline; "
                "keep the body minimal — proof only. Generous whitespace is "
                "intentional here.".format(d=density))
    return (
        "Fill the page. Every CONTENT slide must be useful on its own: render all "
        "of the brief's evidence as substantive, self-explanatory body content — "
        "each point a full, readable statement, not a stub or a 2-3 word label. A "
        "near-empty content page (a handful of words on a full canvas) is a DEFECT; "
        "use the body zone. This does NOT override brief fidelity: render what the "
        "brief supplies richly, never fabricate beyond it. Cover / section-divider / "
        "single-hero-stat slides are exempt — those stay deliberately spare."
    )


def visual_mandatory(slide: dict[str, Any]) -> str:
    """A Must use visual is a required shape, like **Mandatory shape:**."""
    v = _visuals.parse_visual(slide.get("visual") or "")
    if v and v["lock"] == "must use" and v["name"] != _visuals.ANY:
        return f"{v['name']} (the user chose it on the Storyline tab: Must use)"
    return ""


def visual_directive(slide: dict[str, Any]) -> str:
    """The prompt's **Visual:** line (owner's decision 2026-10-16)."""
    v = _visuals.parse_visual(slide.get("visual") or "")
    reuse = (slide.get("reuse") or "").strip()
    start = ""
    if reuse and not reuse.lower().startswith("new design"):
        start = (f" Start from: {reuse}."
                 + (" Keep its structure and wording and redraw it cleanly on the template."
                    if "clean" in reuse.lower() else ""))
    if not v or v["name"] == _visuals.ANY:
        return ("Designer's choice: pick the visual that proves the point best, and tag what "
                "you drew (see \"Tag the main visual\" below)." + start)
    note = (slide.get("visual_note") or "").strip()
    shows = (slide.get("visual_shows") or "").strip()
    extra = (f" What it shows: {shows}." if shows else "") + (f" The user's note: {note}." if note else "")
    if v["lock"] == "must use":
        return (f"{v['name']} (MUST USE: the user chose it on the Storyline tab). Every option "
                "is this kind of visual; a design that comes back as another kind is sent back "
                "before the user sees it." + extra + start)
    return (f"{v['name']} (suggestion). Use it unless you have a better reason; if you draw "
            "something else, tag what you drew and give the reason in one line (see \"Tag the "
            "main visual\" below). With three options, use at least two different kinds of "
            "visual." + extra + start)


def build_placeholders(
    slide: dict[str, Any],
    slide_total: int,
    deck_notes: str,
    client_template_path: Path,
    output_dir: Path,
    seeds: dict[str, str],
    likely_prior_patterns: str,
    slide_pattern: str = "direct",
    density_note: str = "",
) -> dict[str, str]:
    """Assemble the {{TOKEN}} → value dictionary for one slide.

    `slide_pattern` is "sketch" (HTML output) or "direct" (python-pptx output,
    default). Defaults to "direct" so callers that don't specify a pattern keep
    working; the worker branches on the rendered PATTERN field.
    """
    # Option count is settings-driven (default 1). Build the count-aware tokens
    # the worker prompt uses so it authors exactly N options.
    letters = _p.option_letters()
    _seed_by_letter = {"A": seeds["variant_seed_a"],
                       "B": seeds["variant_seed_b"],
                       "C": seeds["variant_seed_c"]}
    variant_seeds = "\n".join(
        f"  - Option {L} variant seed: `{_seed_by_letter[L]}`" for L in letters
    )
    files_direct = "\n".join(str(output_dir / _p.option_py_name(L)) for L in letters)
    files_sketch = "\n".join(str(output_dir / f"option_{L}.html") for L in letters)
    return {
        "OPTIONS_COUNT":           str(len(letters)),
        "OPTION_LETTERS":          ", ".join(letters),
        "VARIANT_SEEDS":           variant_seeds,
        "OPTION_FILES_DIRECT":     files_direct,
        "OPTION_FILES_SKETCH":     files_sketch,
        "PATTERN":                 slide_pattern,
        "SLIDE_N":                 str(slide["slide_n"]),
        "SLIDE_TOTAL":             str(slide_total),
        "SLIDE_TITLE":             slide.get("title", "") or "(untitled)",
        "GOVERNING_THOUGHT":       slide.get("governing_thought", "") or "(no governing thought in brief)",
        "SO_WHAT":                 slide.get("so_what", "") or "(no so-what in brief)",
        "EDITORIAL_EMPHASIS":      slide.get("editorial_emphasis", "") or "(none specified)",
        # evidence_type: lines are storyline bookkeeping, not slide content;
        # designers were copying them. Source lines stay (they feed the footer).
        "EVIDENCE_CONTENT":        (re.sub(r"(?m)^[ \t]*evidence_type:.*\n?", "",
                                           slide.get("evidence_content", "") or "")
                                    or "(no evidence specified)"),
        "CHART_TYPE":              slide.get("chart_type", "none"),
        "CHART_DATA":              slide.get("chart_data", "") or "(no chart data provided)",
        "NOT_THIS_SLIDE":          slide.get("not_this_slide", "") or "(none)",
        "VISUAL_RHYTHM":           slide.get("visual_rhythm", "") or "(worker's judgment)",
        "MANDATORY_SHAPE":         (slide.get("mandatory_shape", "") or visual_mandatory(slide)
                                    or "(none — worker's judgment)"),
        "VISUAL":                  visual_directive(slide),
        # 2 to 4 icon topics picked from the slide's own words, plus the
        # status group (owner's decision 2026-10-21).
        "ICON_TOPICS":             icon_names.topic_block(" ".join(
                                       str(slide.get(k) or "") for k in
                                       ("title", "governing_thought", "so_what",
                                        "editorial_emphasis", "evidence_content"))),
        "PINNED_SOURCE_PAGE":      slide.get("pinned_source_page", "") or "(none)",
        "SOURCE_LINE":             slide.get("source", "") or "(none in the brief)",
        "SECTION_TAG":             slide.get("section_tag", "") or "(none)",
        "FORBIDDEN_PATTERNS":      slide.get("forbidden_patterns", "") or "(none)",
        "ACCENT_PLACEMENT":        slide.get("accent_placement", "") or "(worker's judgment)",
        "DECK_LEVEL_DESIGN_NOTES": deck_notes or "(no deck-level design notes)",
        "DENSITY_DIRECTIVE":       density_note or density_directive({}),
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
    _letters = _p.option_letters()
    _files = " / ".join(f"`option_{L}`" for L in _letters)
    _n = len(_letters)
    _opt_word = "option" if _n == 1 else f"{_n} options"
    lines.append(
        "Parent session dispatches one `slide-builder-worker` agent per slide "
        "IN PARALLEL. Each worker reads its `_context.md` first, then "
        f"`_prompt.md`, and writes its {_opt_word} into its own `slide_NN/` "
        f"directory — {_files} as `.py` for direct-path slides, or as `.html` "
        "for sketch-path slides (per the slide's PATTERN field). After the "
        "workers, follow the steps prep printed (finalize, REVIEW.html, "
        "record_picks.py, translate picked sketches, finalize, FINAL-CHECK.html, "
        "compile); SKILL.md steps 6-10 describe the same order."
    )

    lines.extend(dispatch_how_lines(out_dir, [s["slide_n"] for s in slides]))
    plan_path.write_text("\n".join(lines), encoding="utf-8")
    return plan_path


def dispatch_how_lines(out_dir: Path, nums: list) -> list[str]:
    """How to send the workers (owner's decision 2026-10-14, Q1).

    Up to 20: one message of foreground agent calls (a trial; recommended),
    so the main session waits once instead of waking for every finished
    agent. More than 20: a rolling pool. Twenty agents run at once and a
    21st dispatch is dropped without a word (a 29-slide deck lost slides
    23-29 and finalize exited 11), so start 20 and start the next each time
    one finishes; never wait for a whole group. Either way,
    `build_deck.py --pending` after the last dispatch names any slide whose
    worker never ran.
    """
    o = f'"{out_dir}"'
    pending = f"py -3 scripts/build_deck.py --pending --out {o}"
    lines = ["", "### How to send the workers", ""]
    if len(nums) <= MAX_CONCURRENT_AGENTS:
        lines.append(
            f"Send all {len(nums)} worker(s) in ONE message, each agent call with "
            "run_in_background false (recommended; a trial since 2026-10-14). The "
            "main session then waits once and reads every result in one turn, "
            "instead of waking about once per finished agent (22 extra turns and "
            "10-20M tokens per 20-worker wave measured on 10-08 and 10-12). The "
            "user cannot type to this session while the wave runs (about 12-18 "
            "minutes); when they want to, send the workers in the background "
            "instead.")
    else:
        lines.append(
            f"Rolling pool: at most {MAX_CONCURRENT_AGENTS} agents run at once, "
            "and a dispatch past that is dropped without any message. Start the "
            f"first {MAX_CONCURRENT_AGENTS} on the list below (in the background); "
            "each time one finishes, start the next on the list. Do not wait for "
            "a whole group to finish before starting more.")
        lines.append("")
        lines.append("Order: slides " + ", ".join(str(n) for n in nums))
    lines.append("")
    lines.append(
        f"After the last dispatch, before finalize, run `{pending}`. It lists "
        "every slide with no worker output (a dispatch that was dropped or never "
        "sent) in seconds; dispatch a worker for each one it lists, then run it "
        "again until it prints none.")
    lines.append("")
    lines.append(
        "The `slide-builder-translator` fan-out at Stage 3.5 (one agent per "
        f"picked option, so it can be longer than this list) works the same way: "
        f"up to {MAX_CONCURRENT_AGENTS} in one message of foreground calls, "
        f"else a rolling pool of {MAX_CONCURRENT_AGENTS}.")
    return lines


# ---------------------------------------------------------------- --pending
def pending_slides(out_dir: Path) -> tuple[list, list]:
    """(slides with no worker output, [(slide, missing letters)] with some).

    A slide counts when prep wrote its `_prompt.md` (so a worker was due) and
    none of its option files (option_X.html or option_X.py, for the letters
    the build froze in _meta.json) is there. A rejected design
    (SKELETON_REJECTED) counts as output: the worker ran."""
    import json as _json
    try:
        meta = _json.loads(_p.meta_json(out_dir).read_text(encoding="utf-8"))
    except Exception:
        meta = {}
    entries = {int(e.get("n") or 0): e for e in meta.get("slides", []) if e.get("n")}
    nums = set(entries)
    for d in out_dir.glob("slide_[0-9][0-9]*"):
        if d.is_dir() and d.name[6:].isdigit():
            nums.add(int(d.name[6:]))
    none, partial = [], []
    for n in sorted(nums):
        sd = _p.slide_dir(out_dir, n)
        if not (sd / "_prompt.md").exists():
            continue
        letters = (entries.get(n) or {}).get("options") or list(_p.option_letters())
        have = [L for L in letters
                if (sd / f"option_{L}.html").exists() or (sd / f"option_{L}.py").exists()]
        if not have:
            none.append(n)
        elif len(have) < len(letters):
            partial.append((n, [L for L in letters if L not in have]))
    return none, partial


def pending_main(argv: list) -> int:
    """build_deck.py --pending --out <out>: exit 0 when every slide has its
    worker output, 1 when some do not (listed with the next step), 2 on a
    bad folder."""
    ap = argparse.ArgumentParser(
        prog="build_deck.py --pending",
        description="List the slides whose worker output is missing.")
    ap.add_argument("--pending", action="store_true", required=True)
    ap.add_argument("--out", required=True, type=Path, help="The build's output folder.")
    args = ap.parse_args(argv)
    out = args.out
    if not out.is_dir():
        print(f"ERROR: build folder not found: {out}. Give the --out folder prep wrote.")
        return 2
    none, partial = pending_slides(out)
    if not none and not partial:
        print(f"No slides pending: every slide in {out} has its worker output. "
              "Next: finalize (the step prep printed).")
        return 0
    if none:
        print(f"PENDING: {len(none)} slide(s) have no worker output: "
              + ", ".join(str(n) for n in none) + ".")
        print("  Their worker was dropped or never sent. Next: dispatch one "
              "slide-builder-worker for each, on its prompt:")
        for n in none:
            print(f"    {_p.slide_dir(out, n) / '_prompt.md'}")
    if partial:
        print(f"INCOMPLETE: {len(partial)} slide(s) have only some of their options: "
              + "; ".join(f"slide {n} is missing option {', '.join(m)}" for n, m in partial)
              + ".")
        print("  If its worker has finished, dispatch it again for that slide; if it "
              "is still running, wait for it.")
    print(f"  Then run this again: py -3 scripts/build_deck.py --pending --out \"{out}\"")
    return 1


def regenerate_dispatch_plan_from_meta(out_dir: Path) -> Optional[Path]:
    """Rebuild dispatch_plan.md from the current _meta.json so its per-slide
    numbering stays in sync after an insert (or rebuild).

    dispatch_plan.md is a human-readable summary; the build itself keys off
    _meta.json / picks.json, so a stale plan never breaks a build — it just
    misleads the reader. Best-effort: only refreshes a plan that already
    exists (never invents one for a legacy build that lacked it), and a
    missing/unreadable _meta.json is a no-op that returns None rather than
    failing the caller."""
    plan_path = _p.dispatch_plan_md(out_dir)
    if not plan_path.exists():
        return None
    meta_path = _p.meta_json(out_dir)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    slides_meta = sorted(meta.get("slides", []), key=lambda e: e.get("n", 0))
    slides = [
        {"slide_n": e.get("n"), "title": e.get("title", "") or ""}
        for e in slides_meta
    ]
    forecasts = [e.get("forecasted_pattern", "") or "" for e in slides_meta]
    return write_dispatch_plan(
        out_dir=out_dir,
        slides=slides,
        forecasts=forecasts,
        client_slug=meta.get("client_slug", "") or "",
        theme_warnings=[],
        brief_path=Path(meta.get("brief", "") or ""),
        client_template_path=Path(meta.get("template", "") or ""),
    )


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
        # Freeze the option letters this slide is built with, so finalize's
        # expected-pairs gate doesn't re-read options_per_slide live (which
        # would break if settings changed between build and finalize).
        "options":            list(_p.option_letters()),
    }
    _pin = (slide.get("pinned_source_page") or "").strip()
    if _pin:
        entry["pinned_source_page"] = _pin
    # Kept for the finishing step: the template's Source slot / footer can be
    # filled from here when the design left it out; the tag is text only for
    # now (no drawn slot yet).
    for _k in ("source", "section_tag", "slide_id"):
        _v = (slide.get(_k) or "").strip()
        if _v:
            entry[_k] = _v
    # The visual chosen on the Storyline tab (record_storyline.py): the
    # review card says whether the design follows it, and a Must use slide
    # that comes back another way is redone (check_visual_type.py).
    _vis = _visuals.parse_visual(slide.get("visual") or "")
    if _vis:
        entry["visual"] = {"name": _vis["name"], "lock": _vis["lock"]}
        if (slide.get("visual_note") or "").strip():
            entry["visual"]["note"] = slide["visual_note"].strip()
    if (slide.get("reuse") or "").strip():
        entry["reuse"] = slide["reuse"].strip()
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


def record_prep_with_notice(out_dir, deck_hash: str, step: str) -> None:
    """Record this prep step in the build state, and say so plainly when the
    agent files Claude Code runs are not the ones the build's previous step
    used. Before 2026-10-13 a --slide or --insert after an install silently
    re-stamped the record, so slides from two agent versions passed as one;
    now every step is kept and compile judges them all (owner's decision)."""
    changed = _state.record_prep(out_dir, deck_hash, out_dir, step=step)
    if not changed:
        return
    import _install
    ok, why, note = _install.versions_compatible(_state.read_state(out_dir))
    print()
    print(f"NOTE: the agent files Claude Code runs changed since this build's last step "
          f"({', '.join(changed)}). This {step} is recorded with the new files; the "
          "earlier slides were built with the old ones.")
    if ok:
        print(f"  Every version used is on main, so the build carries on: {note}.")
        print("  Compile writes this into COMPILED.md. Start a new Claude session before "
              "the next round so every worker runs the new files.")
    else:
        print("  Compile will refuse this build: " + why)
    print("  Do not copy or restore agent files from this session.")


def _one_page_after_prep(out_dir: Path):
    """After a prep: the one Slide Lab page shows the storyline (read only)
    and "the designers are working" on tab 2. Never fails the prep."""
    try:
        import slidelab_page
        slidelab_page.forget_parts(out_dir)
        return slidelab_page.write(out_dir, "designs")
    except Exception as exc:  # pragma: no cover
        print(f"  (the Slide Lab page was not written: {type(exc).__name__}: {exc})")
        return None


def pinned_pages_note(slides) -> list[str]:
    """The prep note for slides that copy a supplied page (owner's decision,
    2026-10-13). No stop: their figures are checked after the picks, on the
    finished slides, and shown on FINAL-CHECK.html for the user to answer."""
    pinned = [s for s in slides if (s.get("pinned_source_page") or "").strip()]
    if not pinned:
        return []
    return ["",
            f"{len(pinned)} slide(s) copy a supplied page: slide "
            + ", ".join(str(s.get("slide_n")) for s in pinned) + ".",
            "  Their figures are checked after the user picks: finalize lists every "
            "number that came from the copied page onto the picked design (numbers "
            "that match the brief are only counted), and FINAL-CHECK.html shows them "
            "in one table for the user to keep or replace. Compile waits for that "
            "answer. The pins stay; never remove one to get past the check."]


# ----------------------------------------------------------------------
# Pages designed once and copied by script (clone_pages.py; owner's decision
# 2026-10-14, speed verdict Q3). Only the first section divider gets a
# designer, the others are copies of it; the cover, contents and executive
# summary are filled from the design kept for the template when there is one;
# a page pinned to a slide of a .pptx is copied as is and a worker in EDIT MODE
# changes only its text. Content pages are never built by script.
# ----------------------------------------------------------------------

def plan_page_copies(args, slides, pattern_per_slide, rebuild_slide_n, insert_slide_n):
    """(plan, exit code). Forces every page in the plan onto the direct path
    (a copy is made from a script). Refuses a rebuild of a divider copy."""
    import clone_pages
    keep: set = set()
    if rebuild_slide_n is not None or insert_slide_n is not None:
        try:
            _old = json.loads(_p.meta_json(args.out).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _old = {}
        for _e in _old.get("slides") or []:
            if (_e.get("page_copy") or {}).get("role") == "master" and isinstance(_e.get("n"), int):
                _n = _e["n"]
                if insert_slide_n is not None and _n >= insert_slide_n:
                    _n += 1
                keep.add(_n)
    fresh = {rebuild_slide_n} if rebuild_slide_n is not None else set()
    bases = [Path(args.brief).resolve().parent, Path(args.out).resolve()]
    plan, warns = clone_pages.plan(slides, template=args.template, bases=bases,
                                   design_fresh=fresh, keep_masters=keep)
    if rebuild_slide_n is not None and clone_pages.is_deck_copy(plan.get(rebuild_slide_n)):
        _m = plan[rebuild_slide_n]["master"]
        sys.stderr.write(
            f"ERROR: slide {rebuild_slide_n} is a copy of slide {_m}'s design (a section "
            f"divider), so it has no design of its own to rebuild. To change how the "
            f"dividers look, rebuild slide {_m}: py -3 scripts/build_deck.py --slide {_m} "
            f"--out \"{args.out}\" --template \"{args.template}\"; every copy is made again "
            "from it at finalize. To change this divider's words, edit the brief and prep "
            "again.\n")
        return plan, 2
    for _w in warns:
        print(f"WARNING (brief): {_w}")
    # "Make slide N look like slide M" (--like-slide) keeps M's build path, so
    # the rebuilt page is designed as asked and is not a design kept for copies.
    if (rebuild_slide_n is not None and getattr(args, "like_slide", None) is not None
            and (plan.get(rebuild_slide_n) or {}).get("role") == "master"
            and not plan[rebuild_slide_n].get("copies")):
        plan.pop(rebuild_slide_n)
    if pattern_per_slide:
        moved = [n for n in sorted(plan) if pattern_per_slide.get(str(n)) != "direct"]
        for n in plan:
            pattern_per_slide[str(n)] = "direct"
        if moved:
            sys.stderr.write(
                f"  slide(s) {', '.join(map(str, moved))}: set to the direct path, because "
                "they are copied by script (clone_pages.py) or are the design the copies "
                "come from.\n")
    return plan, 0


def page_copy_prompt(slide_dir: Path, slide: dict, rendered: str, plan: dict) -> str:
    """The slide's _prompt.md with the page-copy section or banner; for a
    copied supplied page, also writes its option_A.py and _edit_request.md."""
    import clone_pages
    n = slide["slide_n"]
    pc = (plan or {}).get(n)
    if not pc:
        return rendered
    if pc["role"] == "master":
        sec = clone_pages.master_prompt_section(n, pc, plan)
        anchor = "## 1. Brief content (only this slide)"
        i = rendered.find(anchor)
        return rendered[:i] + sec + rendered[i:] if i >= 0 else sec + rendered
    if pc["role"] == "copy":
        return clone_pages.copy_prompt_banner(n, pc) + rendered
    if pc["role"] == "pinned":
        clone_pages.write_pinned_copy(slide_dir, n, pc)
        return clone_pages.pinned_prompt_banner(n, pc) + rendered
    return rendered


def record_page_copies(meta_path: Path, plan: dict) -> None:
    import clone_pages
    clone_pages.apply_to_meta(Path(meta_path), plan or {})


def page_copy_lines(plan: dict, out_dir: Path, template, plan_path=None) -> list[str]:
    """What prep says about copied pages; also added to dispatch_plan.md."""
    import clone_pages
    lines = clone_pages.prep_lines(plan or {}, Path(out_dir).resolve(), template)
    if lines and plan_path is not None:
        try:
            with open(plan_path, "a", encoding="utf-8") as fh:
                fh.write("\n\n## Pages made by script\n" + "\n".join(lines[1:]) + "\n")
        except OSError:
            pass
    return lines


def page_copy_target_lines(plan: dict, slide_n, out_dir: Path) -> list[str]:
    """After a single-slide prep: what the copied pages need now."""
    import clone_pages
    pc = (plan or {}).get(slide_n) or {}
    if pc.get("role") == "master" and pc.get("copies"):
        return [f"Slide {slide_n} is the design slides {', '.join(map(str, pc['copies']))} are "
                "copied from: finalize_deck.py makes the copies again from the new design "
                "(clone_pages.py). Do not send workers for them."]
    if pc.get("role") == "pinned":
        return [f"Slide {slide_n} copies {Path(pc['source']).name} slide {pc['source_slide']} "
                "as is: send its worker in EDIT MODE on "
                f"{_p.slide_dir(out_dir, slide_n) / clone_pages.EDIT_REQUEST}, not a designer."]
    return []


def review_sequence_lines(out_dir, template, slide_n=None) -> list[str]:
    """The steps after the workers, in order. ONE copy, printed by every exit of
    prep and pointed at by the docs. Rebuild, insert, full build and 6b each used
    to print their own version, and most of them skipped a step: no translator,
    picks before the review, a compile with no review at all.

    The order is the owner's decision (2026-09-30).
    """
    o, t = f'"{out_dir}"', f'"{template}"'
    scope = f" --slide {slide_n}" if slide_n is not None else ""
    return [
        "  a. Dispatch the slide-builder-worker(s) as dispatch_plan.md says (up to 20:",
        "     one message of foreground calls; more: a rolling pool of 20). Sketch",
        "     designs render to option_X.sketch.png. Then run, until it lists none:",
        f"     py -3 scripts/build_deck.py --pending --out {o}",
        f"  b. py -3 scripts/finalize_deck.py --out {o} --template {t}{scope}",
        "     (puts direct-path options on the template; sketches wait for a pick)",
        f"  c. py -3 scripts/build_review.py --out {o}",
        "     SHOW the user REVIEW.html and WAIT. They pick every slide (or Replace",
        "     these). Their Build command runs record_picks.py; run it as pasted.",
        "  d. Dispatch slide-builder-translator on each PICKED sketch that",
        "     record_picks.py lists. Unpicked sketches are never converted.",
        # Same scope as step b. A full finalize here broke the 6b flow: an
        # adopted deck's other slides have no options, so it exited 11 and
        # advised redesigning slides the user never asked to touch.
        f"  e. py -3 scripts/finalize_deck.py --out {o} --template {t}{scope}",
        f"  f. py -3 scripts/build_review.py --out {o} --final",
        "     SHOW the user FINAL-CHECK.html and WAIT for its Build command",
        "     (compile_picks.py ... --final-token <t>). Run it as pasted.",
        "  g. slide-qc on the deck, record_vision_qc.py, then check_done.py.",
    ]


def _retire_previous_options(slide_dir: Path) -> int:
    """Move a slide's existing option files into slide_NN/_prev/<timestamp>/.

    A rebuild used to leave them in place. finalize prefers an existing
    option_X_native.py, so after a worker wrote new HTML, finalize quietly rebuilt
    the OLD design; and a new sketch could sit beside an old finished file, so
    the user approved one picture and compile shipped another. Moving them aside
    (not deleting) keeps them for comparison. Returns how many files moved.
    """
    olds = [p for p in slide_dir.glob("option_*") if p.is_file()]
    if not olds:
        return 0
    dest = slide_dir / "_prev" / datetime.now().strftime("%Y%m%dT%H%M%S")
    dest.mkdir(parents=True, exist_ok=True)
    for p in olds:
        try:
            p.replace(dest / p.name)
        except OSError as exc:
            sys.stderr.write(f"  WARN: could not move {p.name} aside: {exc}\n")
    print(f"  moved {len(olds)} previous option file(s) to {dest}")
    return len(olds)


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

    try:
        MetaJson.model_validate(meta)
    except Exception as exc:
        # A malformed on-disk _meta.json (e.g. an incomplete hand-built or
        # adopted manifest) should fail with a clear message, not a raw
        # traceback out of a rebuild/insert. Caller treats None as exit 2.
        print(f"[error] _meta.json failed schema validation: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return None
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path


def record_storyline(out_dir: Path, brief_path: Optional[Path],
                     override: Optional[Path] = None) -> Optional[str]:
    """Record the approved storyline in _meta.json["storyline"]: its path,
    size, last-changed time and fingerprint (owner's decision 2026-10-13).
    The path comes from --storyline, else the brief's front matter
    `approved_storyline:`; nothing is ever searched for by name. REVIEW.html
    shows that file, and warns when it changed after this prep. Returns a
    line to print, or None when there is no pointer."""
    path_txt = str(override) if override else ""
    if not path_txt and brief_path and Path(brief_path).exists():
        try:
            fm, _ = extract_front_matter(read_text_safe(Path(brief_path)))
        except Exception:
            fm = {}
        path_txt = (fm.get("approved_storyline") or "").strip()
    mp = _p.meta_json(out_dir)
    try:
        meta = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not path_txt:
        if meta.pop("storyline", None) is not None:
            mp.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return None
    sp = Path(path_txt)
    if not sp.is_absolute() and brief_path:
        sp = (Path(brief_path).parent / sp)
    rec: dict[str, Any] = {"path": str(sp.resolve()), "recorded_at": datetime.now().isoformat(
        timespec="seconds")}
    if sp.exists():
        data = sp.read_bytes()
        rec.update({"size": len(data), "mtime": sp.stat().st_mtime,
                    "sha256": hashlib.sha256(data).hexdigest()})
        line = f"Approved storyline recorded: {sp.resolve()}"
    else:
        rec["missing"] = True
        line = (f"WARNING: the approved storyline {sp} does not exist; the review page "
                "will say so. Fix approved_storyline in the brief's front matter.")
    meta["storyline"] = rec
    mp.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return line


def read_text_safe(p: Path) -> str:
    return p.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n").lstrip("﻿")


def _shift_build_for_insert(out_dir: Path, insert_n: int, old_count: int) -> None:
    """Make room at position `insert_n` for a new slide by shifting slides
    >= insert_n up by one on disk: rename `slide_NN/` dirs (highest first, so
    each destination is free before the rename), then renumber every
    slide-numbered record (_state.shift_slide_records: picks.json, _meta.json,
    _state.json, source_ledger.json). update_meta_for_insert then adds the new
    slide's entry. No-op tail when inserting at the end (insert_n == old_count + 1).

    Self-reversing: if any rename fails partway, the renames already done are
    undone before re-raising, so the build is never left half-shifted.

    A folder Windows will not rename (WinError 32: a program or a File Explorer
    window is sitting in it) is tried 3 more times, then FolderLocked is raised
    naming that folder (2026-10-13: an agent shell left in slide_20 stopped
    three inserts)."""
    renamed: list[tuple[Path, Path]] = []  # (current, original) to undo on failure
    try:
        for k in range(old_count, insert_n - 1, -1):
            src = _p.slide_dir(out_dir, k)
            dst = _p.slide_dir(out_dir, k + 1)
            if src.exists():
                if dst.exists():
                    raise OSError(f"insert shift collision: {dst} already exists")
                _rename_with_retry(src, dst)
                renamed.append((dst, src))

        # Per-slide reports in the build folder move with their slides.
        for k in range(old_count, insert_n - 1, -1):
            src = out_dir / f"RESULT-slide-{k:02d}.md"
            dst = out_dir / f"RESULT-slide-{k + 1:02d}.md"
            if src.exists() and not dst.exists():
                _rename_with_retry(src, dst)
                renamed.append((dst, src))
        # Every record keyed by a slide number moves with the folders (one
        # helper for insert and delete, 2026-10-27). Left unshifted, a slide
        # inherited its neighbor's record: a slide blocked for placeholder
        # text moved up one and picked up a clean record, and a verifier
        # shipped it as DELIVERABLE.
        _state.shift_slide_records(out_dir, insert_n, +1,
                                   note=f"slide {insert_n} inserted")
        _mark_fix_snapshots(out_dir, f"slide {insert_n} inserted")
    except OSError:
        # Undo the dir renames we managed so the build isn't half-shifted. A
        # failed undo used to pass silently; say which folder is out of place.
        for current, original in reversed(renamed):
            try:
                _rename_with_retry(current, original)
            except OSError as undo_exc:
                sys.stderr.write(
                    f"  ERROR: could not move {current.name} back to {original.name} "
                    f"({undo_exc}). Rename {current} to {original} by hand once the "
                    "folder is free, before any other step.\n")
        raise


class FolderLocked(OSError):
    """A slide folder Windows would not rename because something is using it."""

    def __init__(self, folder: Path, exc: OSError):
        super().__init__(f"{folder} is in use: {exc}")
        self.folder = folder


def _is_lock_error(exc: OSError) -> bool:
    return getattr(exc, "winerror", None) in (5, 32, 33) or isinstance(exc, PermissionError)


def _rename_with_retry(src: Path, dst: Path, tries: int = 4) -> None:
    """Rename, trying 3 more times (about 3 s in all) while the folder is in use."""
    import time as _time
    for i in range(tries):
        try:
            src.rename(dst)
            return
        except OSError as exc:
            if not _is_lock_error(exc):
                raise
            if i == tries - 1:
                raise FolderLocked(src, exc) from exc
            _time.sleep(0.5 * (i + 1))


def locked_folder_message(out_dir: Path, folder: Path, argv: list[str],
                          op: str = "insert") -> list[str]:
    """The plain stop message for a folder in use: what holds it (read-only)
    and what to do. Nothing is ended here (owner's decision 2026-10-13).
    `op` is "insert" or "delete"."""
    here = Path(__file__).resolve().parent
    lines = [
        f"ERROR: the {op} stopped because Windows would not rename the folder",
        f"  {folder}",
        "  A program or File Explorer window is sitting in this folder (for example an",
        "  agent's shell that ran cd into it, a render, or an Explorer window open on it).",
        "  Nothing was changed: every folder is back where it was.",
    ]
    rows = []
    try:
        if str(here) not in sys.path:
            sys.path.insert(0, str(here))
        import _procs
        rows = _procs.mentioning(str(Path(out_dir).resolve()))
        listing = _procs.describe(rows)
    except Exception:
        listing = []
    if rows:
        lines.append("  Processes whose command line mentions this build folder (listed only; "
                     "nothing was ended):")
        lines += listing
    else:
        lines.append("  No process names this build folder in its command line, so it is most "
                     "likely a File Explorer window or a program with the folder open.")
    lines.append("Next:")
    if rows:
        pids = " ".join(str(r["pid"]) for r in rows)
        lines += [
            "  1. Ask the user to close any File Explorer window or program open in that",
            "     folder, or to say yes to ending exactly the PIDs listed above. Only after",
            "     their yes, end ONLY those PIDs (never anything by its name):",
            f'     py -3 "{here / "_procs.py"}" --mentioning "{Path(out_dir).resolve()}" --end {pids}',
        ]
    else:
        lines.append("  1. Ask the user to close any File Explorer window or program open in "
                     "that folder.")
    lines.append(f"  2. Then run the same {op} again:")
    lines.append("     py -3 " + " ".join(f'"{a}"' if " " in a else a for a in argv))
    return lines


def _mark_fix_snapshots(out_dir: Path, note: str) -> None:
    """The whole-deck copies apply_qc_fix.py keeps (_autofix_prev/deck_before_*)
    have the old page count after an insert or a delete. Say so beside them;
    apply_qc_fix.py refuses to undo a fix made before the renumbering."""
    d = Path(out_dir) / "_autofix_prev"
    if not d.is_dir():
        return
    olds = sorted(p.name for p in d.glob("deck_before_*"))
    if not olds:
        return
    try:
        with open(d / "BEFORE_RENUMBER.txt", "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat(timespec='seconds')}: {note}. These decks "
                     "have the old page numbers; never restore a page from them:\n")
            fh.writelines(f"  {n}\n" for n in olds)
    except OSError:
        pass


# ----------------------------------------------------------------------
# build_deck.py --delete N (2026-10-27): the reverse of --insert. Before it,
# a slide was removed with a hand-written script that moved the folders and
# a few records and left the rest pointing at the wrong pages.
# ----------------------------------------------------------------------

_MENTION_RE = re.compile(r"\b(slides?|pages?)\s+(\d+)\b", re.I)


def _number_mentions(text: str, at: int) -> list[tuple[int, str]]:
    """Lines naming 'slide N' or 'page N' with N >= at: after the delete they
    point at another page (or at the removed one)."""
    hits = []
    for i, line in enumerate((text or "").replace("\r\n", "\n").split("\n"), 1):
        if any(int(m.group(2)) >= at for m in _MENTION_RE.finditer(line)):
            hits.append((i, line.strip()[:160]))
    return hits


def _move_with_retry(src: Path, dst: Path) -> None:
    """Rename (retrying while the folder is in use); a move to another drive
    falls back to a copy-and-remove move."""
    try:
        _rename_with_retry(src, dst)
    except FolderLocked:
        raise
    except OSError as exc:
        if getattr(exc, "winerror", None) == 17 or getattr(exc, "errno", None) == 18:
            import shutil as _sh
            _sh.move(str(src), str(dst))
        else:
            raise


def _shift_build_for_delete(out_dir: Path, n: int, count: int, archive: Path) -> None:
    """Move slide_NN/ and RESULT-slide-NN.md into `archive`, then rename the
    later folders and reports down one, lowest first. Self-reversing: a folder
    Windows will not rename stops it with every move undone."""
    done: list[tuple[Path, Path]] = []      # (now at, was at)
    archive_made = not archive.exists()
    archive.mkdir(parents=True, exist_ok=True)
    try:
        src = _p.slide_dir(out_dir, n)
        if src.exists():
            _move_with_retry(src, archive / src.name)
            done.append((archive / src.name, src))
        for k in range(n + 1, count + 1):
            s, d = _p.slide_dir(out_dir, k), _p.slide_dir(out_dir, k - 1)
            if s.exists():
                if d.exists():
                    raise OSError(f"delete shift collision: {d} already exists")
                _rename_with_retry(s, d)
                done.append((d, s))
        rs = out_dir / f"RESULT-slide-{n:02d}.md"
        if rs.exists():
            _move_with_retry(rs, archive / rs.name)
            done.append((archive / rs.name, rs))
        for k in range(n + 1, count + 1):
            s, d = out_dir / f"RESULT-slide-{k:02d}.md", out_dir / f"RESULT-slide-{k - 1:02d}.md"
            if s.exists() and not d.exists():
                _rename_with_retry(s, d)
                done.append((d, s))
    except OSError:
        for now_at, was_at in reversed(done):
            try:
                _move_with_retry(now_at, was_at)
            except OSError as undo_exc:
                sys.stderr.write(
                    f"  ERROR: could not move {now_at} back to {was_at} ({undo_exc}). Move it "
                    "back by hand once the folder is free, before any other step.\n")
        if archive_made:
            try:
                archive.rmdir()
                if not any(archive.parent.iterdir()):
                    archive.parent.rmdir()
            except OSError:
                pass
        raise


def _retire_slide_id(brief: Path, slide_id: str, n: int) -> Optional[Path]:
    """Mark the id retired in _session/slide_ids.json. It is never handed out
    again (slide_ids.py skips every id in the file), so a re-insert of the
    page gets a new id unless the user gives it this one back by hand."""
    if not slide_id:
        return None
    try:
        import slide_ids
        reg = slide_ids.load_registry(brief)
        ent = reg.setdefault("ids", {}).setdefault(slide_id, {"first_title": "", "at": ""})
        ent["retired"] = {"at": datetime.now().isoformat(timespec="seconds"),
                          "why": f"slide {n} removed from the deck"}
        p = slide_ids.registry_path(brief)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
        return p
    except Exception as exc:
        sys.stderr.write(f"  WARN: could not mark the id {slide_id!r} retired: {exc}\n")
        return None


def _reseal_if_sealed(brief_path: Path) -> int:
    """A sealed brief with the slide taken out no longer matches its seal:
    seal it again (keeping the user's earlier accepted reasons). 0 when sealed
    or never sealed; seal_brief.py's exit code when it refused."""
    text = read_text_safe(brief_path)
    fm, _body = extract_front_matter(text)
    sha = str((fm or {}).get("storyline_gate_sha") or "").strip()
    if not sha:
        return 0
    import seal_brief
    try:
        if seal_brief._fingerprint_as_prep_reads(text) == sha:
            return 0
    except Exception:
        pass
    acc = str((fm or {}).get("storyline_gate_accepted") or "").strip().strip('"')
    acc = re.sub(r"^\d+ issue\(s\) kept:\s*", "", acc)
    argv = ["--brief", str(brief_path)] + (["--accepted", acc] if acc else [])
    print("The brief was sealed; sealing it again with the slide taken out:")
    return seal_brief.main(argv)


def delete_main(argv: list) -> int:
    """build_deck.py --delete N --out <out> [--brief <brief>] [--template <tpl>]."""
    ap = argparse.ArgumentParser(
        prog="build_deck.py --delete",
        description="Remove slide N from an existing build: the reverse of --insert.")
    ap.add_argument("--delete", required=True, type=int)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--brief", type=Path, default=None,
                    help="The brief with slide N already taken out and the later slides "
                         "renumbered (default: the brief recorded in _meta.json).")
    ap.add_argument("--template", type=Path, default=None,
                    help="Accepted for symmetry with --insert; read from _meta.json.")
    ap.add_argument("--confirm-template", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    out, n = args.out, args.delete
    meta_path = _p.meta_json(out)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: --delete {n} needs an existing build at {out} "
                         f"(no readable _meta.json: {exc}).\n")
        return 2
    count = int(meta.get("slide_count", 0) or 0)
    if count < 2 or not 1 <= n <= count:
        sys.stderr.write(f"ERROR: --delete {n} out of range; the build has {count} slide(s), "
                         "so a slide 1.." + str(count) + " can be removed (never the last one "
                         "left).\n")
        return 2
    brief_path = args.brief or Path(meta.get("brief") or "")
    if not brief_path or not Path(brief_path).is_file():
        sys.stderr.write(f"ERROR: no brief at {brief_path}; pass --brief.\n")
        return 2
    try:
        import _rulings
        _rulings.announce(out=out)
    except Exception:
        _rulings = None
    from _log import attach as _log_attach  # noqa: E402
    _log_attach(out, "build_deck.py")

    # 1. The brief first: one slide fewer, numbered 1..count-1, and the slide
    #    missing from it is the one at N (by its fixed id).
    brief = parse_brief(Path(brief_path), bypass_gate=True)
    bslides = sorted(brief["slides"], key=lambda s: s["slide_n"])
    if [s["slide_n"] for s in bslides] != list(range(1, count)):
        sys.stderr.write(
            f"ERROR: --delete expects the brief to have exactly one slide fewer than the build "
            f"({count - 1}), numbered 1..{count - 1} with no gaps; it has "
            f"{[s['slide_n'] for s in bslides]}. Take slide {n} out of the brief, renumber the "
            "later slides, then run this again. Nothing was changed.\n")
        return 2
    mslides = sorted(meta.get("slides") or [], key=lambda e: e.get("n", 0))
    gone = next((e for e in mslides if e.get("n") == n), {}) or {}
    gone_id = (gone.get("slide_id") or "").strip().lower()
    rest = [e for e in mslides if e.get("n") != n]
    if gone_id and all(e.get("slide_id") for e in rest) and all(s.get("slide_id") for s in bslides):
        want = [e["slide_id"].lower() for e in rest]
        have = [s["slide_id"].lower() for s in bslides]
        if have != want:
            sys.stderr.write(
                f"ERROR: the brief's slides are not the build's slides with slide {n} "
                f"({gone_id}) taken out. By slide id the brief has {have}; it should have "
                f"{want}. Fix the brief (or delete the slide that is actually missing), then "
                "run this again. Nothing was changed.\n")
            return 2
    else:
        want = [(e.get("title") or "").strip() for e in rest]
        have = [(s.get("title") or "").strip() for s in bslides]
        if have != want:
            sys.stderr.write(
                f"ERROR: the slides have no fixed ids to match on, and the brief's titles are "
                f"not the build's titles with slide {n} taken out ({have} vs {want}). Add the "
                f"ids (py -3 scripts/slide_ids.py --brief \"{brief_path}\") or make the other "
                "titles match the build, delete, then make other edits. Nothing was changed.\n")
            return 2

    # Mentions of page numbers that moved (listed, never edited).
    mentions = [("brief", ln, t) for ln, t in _number_mentions(read_text_safe(Path(brief_path)), n)]
    sl_path = Path(((meta.get("storyline") or {}).get("path")) or "")
    if sl_path.suffix.lower() in (".md", ".html", ".htm", ".txt") and sl_path.is_file():
        mentions += [(sl_path.name, ln, t) for ln, t in
                     _number_mentions(read_text_safe(sl_path), n)]

    # 2. Re-seal a sealed brief (before anything on disk moves).
    rc = _reseal_if_sealed(Path(brief_path))
    if rc:
        sys.stderr.write("ERROR: the brief could not be sealed again (above), so the slide "
                         "was not removed. Nothing in the build was changed.\n")
        return 3
    brief = parse_brief(Path(brief_path), bypass_gate=True)

    # 3. Folders: slide N to _session/removed_slides/, later ones down one.
    sd = _rulings.session_dir(out=out) if _rulings else out / "_session"
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    archive = sd / "removed_slides" / f"{n:02d}_{gone_id or 'slide'}_{stamp}"
    try:
        _shift_build_for_delete(out, n, count, archive)
    except FolderLocked as exc:
        for _ln in locked_folder_message(out, exc.folder,
                                         [str(Path(sys.argv[0]).resolve())] + list(argv),
                                         op="delete"):
            sys.stderr.write(_ln + "\n")
        return 5
    except OSError as exc:
        sys.stderr.write(f"ERROR: could not move the slide folders for the delete: {exc}. "
                         "Every folder is back where it was.\n")
        return 5

    # 4. Every slide-numbered record, in one helper (shared with --insert).
    note = f"slide {n}" + (f" ({gone_id})" if gone_id else "") + " removed"
    removed = _state.shift_slide_records(out, n, -1, note=note)
    removed.setdefault("meta_entry", gone)
    (archive / "removed_records.json").write_text(
        json.dumps({"slide": n, "id": gone_id, "title": gone.get("title", ""),
                    "removed_at": datetime.now().isoformat(timespec="seconds"),
                    "records": removed}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    _mark_fix_snapshots(out, note)
    reg = _retire_slide_id(Path(brief_path), gone_id, n)
    tpl = args.template or Path(meta.get("template") or "")
    deck_hash = _state.deck_content_hash(json.dumps(brief, sort_keys=True, default=str),
                                         str(tpl), _resolve_effective_pattern(None))
    _state.record_delete(out, deck_hash, n, gone_id)
    plan_path = regenerate_dispatch_plan_from_meta(out)

    # 5. What changed, and what the user decides.
    moved = (f"; slides {n + 1}..{count} are now {n}..{count - 1}" if n < count else "")
    print(f"Deleted slide {n}" + (f" ({gone_id})" if gone_id else "")
          + f": the build now has {count - 1} slides{moved}.")
    print("  Kept, not deleted (its designs, picks and records):")
    print(f"    {archive}")
    if reg:
        print(f"  The id {gone_id!r} is retired in {reg}: it is never handed out again.")
    if plan_path is not None:
        print(f"  Renumbered dispatch plan: {plan_path}")
    if removed.get("orphan_copies"):
        print("  These slides were copies of the removed page and now have no design of "
              "their own: " + ", ".join(map(str, removed["orphan_copies"]))
              + ". Prep each again (build_deck.py --slide N).")
    if _rulings:
        data = _rulings.load(sd)
        mine = _rulings.active(data, gone_id) if gone_id else []
        named = [r for r in _rulings.active(data)
                 if r not in mine and any(int(m.group(2)) >= n
                                          for m in _MENTION_RE.finditer(r.get("quote", "")))]
        if mine:
            print()
            print(f"RULINGS on the removed slide ({gone_id}): never re-tagged or deleted by "
                  "this command. Ask the user, for each, whether it now belongs to another "
                  "slide or is retired, then run what they say:")
            for r in mine:
                print(f"  R{r['n']} {r.get('topic', '')}: \"{r['quote']}\"")
            here = Path(__file__).resolve().parent
            print(f"  move:   py -3 \"{here / 'add_ruling.py'}\" --out \"{out}\" --move <R> --to "
                  "<slide id> --user-said \"<their words>\"")
            print(f"  retire: py -3 \"{here / 'add_ruling.py'}\" --out \"{out}\" --retire <R> "
                  "--user-said \"<their words>\"")
        if named:
            print()
            print("RULINGS that name a page number which moved (their words are kept as "
                  "typed; read them with the new numbering):")
            for r in named:
                print(f"  R{r['n']} [{r['id']}]: \"{r['quote']}\"")
    if mentions:
        print()
        print(f"PAGE NUMBERS in the brief or storyline at or after {n} (they now point at "
              "another page; fix them in the words, then re-seal a sealed brief):")
        for where, ln, t in mentions[:20]:
            print(f"  {where} line {ln}: {t}")
    o = f'"{out}"'
    print()
    print("Next (the other slides keep their picks and finished designs; the final check "
          "and the page-by-page QC start again):")
    print(f"  a. py -3 scripts/build_review.py --out {o} --final")
    print("     SHOW the user FINAL-CHECK.html and WAIT for its Build command")
    print("     (compile_picks.py ... --final-token <t>). Run it as pasted.")
    print("  b. slide-qc on the deck (every page is read again: the pages were renumbered),")
    print("     record_vision_qc.py, then check_done.py.")
    return 0


def update_meta_for_insert(
    out_dir: Path,
    brief: dict[str, Any],
    insert_n: int,
    forecasts: list[str],
    pattern_per_slide: Optional[dict[str, str]] = None,
    old_count: int = 0,
) -> Optional[Path]:
    """Splice a newly inserted slide's entry into `_meta.json`.

    Assumes `_shift_build_for_insert` already moved the on-disk dirs and
    renumbered the existing `_meta` entries (and the pattern map). Inserts the
    new slide's entry at insert_n (recomputed with the shared builder), sets
    slide_count, and re-validates before writing. Other slides'
    entries are preserved verbatim apart from their renumbered `n`."""
    pattern_per_slide = pattern_per_slide or {}
    meta_path = _p.meta_json(out_dir)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: cannot read {meta_path} for insert: {exc}\n")
        return None

    # The existing entries and the routing map were already renumbered by
    # _state.shift_slide_records (in _shift_build_for_insert).
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

    try:
        MetaJson.model_validate(meta)
    except Exception as exc:
        # A malformed on-disk _meta.json (e.g. an incomplete hand-built or
        # adopted manifest) should fail with a clear message, not a raw
        # traceback out of a rebuild/insert. Caller treats None as exit 2.
        print(f"[error] _meta.json failed schema validation: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return None
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
    cover_default = ""
    try:
        theme_path = _p.theme_json(template_path)
        if theme_path.exists():
            theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
            template_default = (theme_data.get("default_content_layout") or "").strip()
            cover_default = (theme_data.get("cover_layout") or "").strip()
    except Exception:
        template_default = ""

    # Cover routing. The brief's Archetype already yields page_type "cover", but
    # that token was never used to pick a layout, so slide 1 landed on the CONTENT
    # layout and the template's branded Cover layout went unused. The deck then
    # needed a hand-built cover, and building it outside the pipeline is what
    # orphaned a slide part and lost a page number. Prefer a cover layout
    # registered on the template; otherwise accept an UNAMBIGUOUS name match so
    # templates registered before this keep working without re-registration.
    if not cover_default and available:
        _cover_names = {"cover", "title", "cover / title", "cover/title", "title slide"}
        _matches = [n for n in available if n.strip().lower() in _cover_names]
        if len(_matches) == 1:
            cover_default = _matches[0]
    if cover_default and available and cover_default not in available:
        cover_default = ""   # registered name no longer in the template

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
    _cover_routed: list[int] = []
    for slide in slides:
        per_slide = (slide.get("layout") or "").strip()
        # page_type resolves the same way _build_slide_meta_entry resolves it.
        _pt = ((slide.get("page_type", "") or "").strip()
               or _normalize_archetype_to_page_type(slide.get("archetype", "") or ""))
        _cover_pick = cover_default if (_pt == "cover" and cover_default) else ""
        if _cover_pick and not per_slide:
            _cover_routed.append(slide.get("slide_n"))
        # An explicit per-slide `Layout:` still wins over cover routing.
        chosen = per_slide or _cover_pick or deck_default or template_default or auto_default
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

    if _cover_routed:
        sys.stderr.write(
            f"[layout] cover routing: slide(s) {_cover_routed} have page_type "
            f"'cover' and were routed to the {cover_default!r} layout.\n"
        )
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


def stage1_sanity_check(template_path: Path, allow_unconfirmed: bool = False) -> int:
    """Verify shared-infra prerequisites BEFORE agent dispatch.

    Returns 0 on success; non-zero exit code on failure (caller should
    propagate). Halts at prep time, before agent compute is sunk.
    """
    # Check (0): the agents Claude Code will dispatch are the ones in this repo.
    # Fixes to slide-builder/agents/ do nothing until they are copied to
    # ~/.claude/agents/; the installed copies once sat three months stale while
    # every translator fix in between existed only in the repo.
    import _install
    _stale = _install.check_installed_agents()
    if _stale:
        sys.stderr.write(
            "ERROR: The agents Claude Code will dispatch are not the ones in this repo.\n\n"
            + "".join(f"  - {p}\n" for p in _stale)
            + "\nEvery fix in slide-builder/agents/ is invisible until it is copied over.\n"
            "Do what each line above says. To copy the repo version over (the\n"
            "installed files are backed up first):\n\n" + _install.copy_command() + "\n\n"
            + _install.NEW_SESSION + " Then re-run.\n")
        return 7

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

    # Check (a.3): if theme.json records a normalized build copy, it should be
    # on disk — finalize/compile build on it. A missing copy is non-fatal (the
    # resolver falls back to the original) but it means builds won't get the
    # normalized template, so surface it rather than silently degrade.
    try:
        _theme_data = json.loads(_p.theme_json(template_path).read_text(encoding="utf-8"))
        _btp = (_theme_data.get("build_template_path") or "").strip()
        if _btp and not Path(_btp).exists():
            sys.stderr.write(
                "WARNING: this template's normalized build copy is missing.\n"
                f"  Expected at: {_btp}\n"
                "  Builds will fall back to the original template. Re-register to "
                "regenerate the copy:\n"
                f"  py -3 scripts/register_template.py propose \"{template_path}\"\n"
                f"  py -3 scripts/register_template.py commit  \"{template_path}\" --picks <picks.json>\n"
            )
        if not _theme_data.get("confirmed", False):
            # Owner's decision (2026-09-30): stop, don't warn. The warning was
            # printed and the build went ahead, while the docs said it stopped;
            # building on a template nobody checked is how a deck comes out in
            # inverted colors with every slide wrong.
            _mock = _p.selftest_pptx(template_path)
            _label = "NOTE (--allow-unconfirmed)" if allow_unconfirmed else "ERROR"
            if _mock.exists():
                sys.stderr.write(
                    f"{_label}: this template hasn't been confirmed by a human yet.\n"
                    "  Registration's automated self-test can miss things, so open the "
                    "mock slide in PowerPoint and confirm before relying on this template:\n"
                    f"  {_mock}\n"
                    f"  py -3 scripts/register_template.py confirm \"{template_path}\"\n"
                )
            else:
                sys.stderr.write(
                    f"{_label}: this template hasn't been confirmed by a human yet, and no "
                    "mock slide was produced (registered via the legacy interactive flow, "
                    "or the render was skipped).\n"
                    "  Re-register via commit/commit-cli to get a mock slide to review, "
                    "then confirm:\n"
                    f"  py -3 scripts/register_template.py commit \"{template_path}\" --picks <picks.json>\n"
                    f"  py -3 scripts/register_template.py confirm \"{template_path}\"\n"
                )
            if not allow_unconfirmed:
                sys.stderr.write(
                    "\nBuild stopped. Ask the user to open the mock slide above in "
                    "PowerPoint. Record the confirmation only after they say the "
                    "title, takeaway, footnote, source and page number look right; never confirm "
                    "it yourself to get past this. If the user tells you to build "
                    "anyway, use --allow-unconfirmed: it is recorded and shown to "
                    "them when the deck is delivered.\n")
                return 12
    except (OSError, ValueError):
        pass  # theme.json already validated above via load_brand_sidecar

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
    count, registration timestamp) for the transcript. No prompt: see the note
    at the end. Returns non-zero only if the template's settings can't be read.
    auto_confirm is the retired --confirm-template flag, ignored.
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

    # No yes/no prompt. Claude Code runs this without a terminal anyone can
    # type into, so the prompt always aborted, and the orchestrator learned to
    # pass --confirm-template by reflex: a gate that certified nothing. The
    # summary is printed for the transcript; the protection that matters is that
    # a person confirmed the template at registration (enforced in the sanity
    # check above).
    print()
    return 0


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    # --pending --out <out>: which slides have no worker output (no template,
    # no brief; owner's decision 2026-10-14).
    if "--pending" in sys.argv[1:]:
        return pending_main(sys.argv[1:])
    # --delete N --out <out>: remove a slide, the reverse of --insert
    # (2026-10-27).
    if "--delete" in sys.argv[1:]:
        return delete_main(sys.argv[1:])
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
    parser.add_argument("--like-slide", required=False, type=int, default=None, dest="like_slide",
                        help="With --slide N: force slide N onto the SAME build path "
                             "(sketch/direct) as reference slide M in the existing build, "
                             "instead of re-classifying it. Use when the user says 'make slide N "
                             "look like slide M' — the reference slide's cleaner look often comes "
                             "from its build path, and re-classifying would silently re-route N.")
    parser.add_argument("--options",  required=False, type=int, default=None,
                        help="How many design options to build per slide (1-3), overriding "
                             "settings. Default: options_per_slide for a full build or an "
                             "insert (1 out of the box; settings.local.json can set 3); "
                             "options_per_slide_revision (1) for a --slide rebuild, or 3 when "
                             "the user marked the slide +3 designs in REVIEW.html "
                             "(redesign_round.py start --three). Use --options 3 only when "
                             "the user asked for three.")
    parser.add_argument("--storyline", required=False, type=Path, default=None,
                        help="The storyline file the user approved (.html, .md or .docx), "
                             "shown on REVIEW.html as written. Overrides the brief's front "
                             "matter line approved_storyline: (emit_dot_dash.py writes that "
                             "line; for a prose storyline written by hand, add it yourself).")
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
        help="No longer needed; accepted so older commands still run. The template "
             "summary is always printed and there is no prompt.",
    )
    parser.add_argument(
        "--assume-gated",
        action="store_true",
        help="Build a brief that did not come through storyline-helper's quality "
             "gate (for example one written in this session). Recorded in the "
             "build's _state.json. Briefs that did pass the gate are sealed with "
             "seal_brief.py instead.",
    )
    parser.add_argument(
        "--allow-unconfirmed",
        action="store_true",
        help="Build on a template no person has confirmed yet (register_template.py "
             "confirm). Recorded in the build's _state.json.",
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
    # How many options this run builds. A full build or a new inserted slide
    # uses options_per_slide (1 out of the box, owner's decision 2026-10-13;
    # a computer's settings.local.json may set 3); a rebuild follows the user's
    # feedback and builds one, or three when they asked for +3 designs on that
    # slide. --options overrides all; a value already pinned in the environment
    # (tests) is left alone.
    if args.options is not None:
        if not 1 <= args.options <= 3:
            sys.stderr.write("ERROR: --options must be 1, 2 or 3.\n")
            return 1
        os.environ["SLIDE_LAB_OPTIONS_PER_SLIDE"] = str(args.options)
    elif rebuild_slide_n is not None and not os.environ.get("SLIDE_LAB_OPTIONS_PER_SLIDE"):
        # "+3 designs" on the slide's card in REVIEW.html (or three asked for in
        # chat) is recorded by redesign_round.py start --three; it wins here.
        try:
            import redesign_round as _rr
            _three = _rr.three_for(args.out, rebuild_slide_n)
        except Exception:
            _three = False
        os.environ["SLIDE_LAB_OPTIONS_PER_SLIDE"] = (
            "3" if _three else str(_p.options_per_slide_revision()))
        if _three:
            sys.stderr.write(f"  slide {rebuild_slide_n}: three new designs (the user asked "
                             "for +3 designs on this slide).\n")
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
    sanity_rc = stage1_sanity_check(args.template, allow_unconfirmed=args.allow_unconfirmed)
    if sanity_rc != 0:
        return sanity_rc

    # 0.5. Template summary — what template will drive the build, printed BEFORE
    # any agent dispatch so a wrong pick is visible in the transcript. Whether a
    # person has checked the template is enforced in the sanity check (exit 12).
    confirm_rc = confirm_template_choice(args.template, args.confirm_template)
    if confirm_rc != 0:
        return confirm_rc

    # Output dir — only created after sanity check passes
    try:
        args.out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"ERROR: cannot create output directory {args.out}: {exc}\n")
        return 5
    if args.allow_unconfirmed:
        _state.record_override(args.out, "allow_unconfirmed",
                               f"built on unconfirmed template {args.template}")
    if args.assume_gated and not single_slide_mode:
        _state.record_override(args.out, "assume_gated",
                               f"brief built without a sealed storyline gate: {args.brief}")

    # 1. Read brief
    brief = parse_brief(args.brief, bypass_gate=single_slide_mode or args.assume_gated)
    # A mode: line (template-fill / rebuild-slice / rfp) skips the storyline
    # gate. Legitimate for the flows that write it, but on a full build it was
    # also a silent way past the gate, so it is recorded like any override.
    _mode = (brief.get("front_matter", {}).get("mode") or "").strip().lower()
    if _mode in GATE_BYPASS_MODES and not single_slide_mode:
        _state.record_override(args.out, "storyline_gate_skipped_by_mode", f"mode: {_mode}")
    slides = brief["slides"]
    slide_total = brief["slide_total"]
    deck_notes = brief["deck_notes"]
    # Say what in the brief prep could not read, instead of dropping it silently.
    for _w in brief.get("warnings") or []:
        print(f"WARNING (brief): {_w}")

    # Build-state manifest: a stable hash of the deck inputs. Any (re)prep records
    # it and invalidates a prior review approval, so a rebuilt/edited deck can
    # never compile on a stale review (Rule 1). Computed here so all three exit
    # paths (full / --slide / --insert) share it.
    _deck_hash = _state.deck_content_hash(
        json.dumps(brief, sort_keys=True, default=str), str(args.template), effective_pattern)
    _density_note = density_directive(brief.get("front_matter", {}) or {})

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
        # The brief slides must be numbered contiguously 1..count+1 (so the new
        # slide at insert_n exists and the shift math is sound). Checked BEFORE
        # any on-disk shift, so a mis-numbered / non-1-based brief fails cleanly
        # here instead of leaving the build half-shifted.
        _brief_ns = sorted(s["slide_n"] for s in slides)
        _expected_ns = list(range(1, existing_slide_count + 2))
        if _brief_ns != _expected_ns:
            sys.stderr.write(
                f"ERROR: --insert needs the brief slides numbered 1..{existing_slide_count + 1} "
                f"with no gaps (found {_brief_ns}). Renumber the brief headers so the new slide "
                f"sits at position {insert_slide_n} and the rest follow in order, then re-run.\n"
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

    # --like-slide M (issue #2 follow-up): force the rebuilt slide onto the SAME
    # build path as an existing reference slide, instead of re-classifying from
    # scratch. "Make slide N look like slide M" usually means "the reference
    # slide's cleaner look came from ITS path" — re-classifying N would silently
    # re-route it (a visual archetype defaults to sketch) and reproduce the
    # mismatch. We read the reference's recorded pattern from the existing
    # _meta.json and pin N to it.
    if rebuild_slide_n is not None and getattr(args, "like_slide", None) is not None:
        try:
            _existing_meta = json.loads(_p.meta_json(args.out).read_text(encoding="utf-8"))
        except Exception:
            _existing_meta = {}
        _ref = str(args.like_slide)
        _ref_pattern = (_existing_meta.get("pattern_per_slide", {}) or {}).get(_ref)
        if _ref_pattern not in ("sketch", "direct"):
            for _s in _existing_meta.get("slides", []):
                if _s.get("n") == args.like_slide:
                    _ref_pattern = _s.get("pattern")
                    break
        if _ref_pattern in ("sketch", "direct"):
            pattern_per_slide[str(rebuild_slide_n)] = _ref_pattern
            sys.stderr.write(
                f"  --like-slide {args.like_slide}: pinning slide {rebuild_slide_n} "
                f"to the '{_ref_pattern}' path to match slide {args.like_slide}.\n"
            )
        else:
            sys.stderr.write(
                f"  WARN: --like-slide {args.like_slide} — no recorded build path for "
                f"slide {args.like_slide} in _meta.json (legacy build, or slide not "
                f"found); keeping the classifier's choice for slide {rebuild_slide_n}.\n"
            )

    # Pages designed once and copied by script (clone_pages.py, owner's
    # decision 2026-10-14): worked out before anything on disk changes.
    copy_plan, _rc = plan_page_copies(args, slides, pattern_per_slide,
                                      rebuild_slide_n, insert_slide_n)
    if _rc:
        return _rc

    # Insert mode: make room at position N by shifting slides >= N (dirs + picks)
    # up by one BEFORE rendering, so the new slide N renders into the freed slot
    # and the shifted slides keep their built output. Must run before the render.
    if insert_slide_n is not None:
        try:
            _shift_build_for_insert(args.out, insert_slide_n, existing_slide_count)
        except FolderLocked as exc:
            for _ln in locked_folder_message(args.out, exc.folder,
                                             [str(Path(sys.argv[0]).resolve())] + sys.argv[1:]):
                sys.stderr.write(_ln + "\n")
            return 5
        except OSError as exc:
            sys.stderr.write(f"ERROR: could not shift build for insert: {exc}\n")
            return 5

    # 4.9 The Storyline tab of the one Slide Lab page (owner's decision
    # 2026-10-16): on a full build the user edits the storyline wording and
    # picks each slide's visual before any designer starts. While it waits,
    # prep writes no slide prompts (nothing to dispatch by mistake).
    _storyline_wait: list[str] = []
    _storyline_lines: list[str] = []
    if not single_slide_mode:
        import record_storyline as _rs
        _skip_tab = _mode in ("template-fill", "rebuild-slice")
        _gate, _lines = _rs.prep_gate(args.out.resolve(), args.brief.resolve(), args.template,
                                      full_build=not _skip_tab)
        if _gate == "wait":
            _storyline_wait = _lines
        else:
            _storyline_lines = _lines
            # Tables plus side-by-side boxes over a third of the slides, while
            # some are only suggestions: refused (the user marks the ones they
            # want as Must use, or changes some).
            _mix = _visuals.mix([
                (s["slide_n"], _v["name"], _v["lock"]) for s in slides
                for _v in [_visuals.parse_visual(s.get("visual") or "")]
                if _v and not _v.get("unknown")])
            if _mix["refuse"]:
                sys.stderr.write(
                    "ERROR: " + _visuals.cap_message(_mix) + " Some of them are only "
                    "suggestions, so prep stopped before any designer started.\n"
                    "  Change some visuals on the Storyline tab, or mark the ones the user wants "
                    "as Must use (their words), then prep again.\n"
                    f"  The Storyline tab: py -3 \"{Path(__file__).resolve().parent / 'slidelab_page.py'}\" "
                    f"show --out \"{args.out}\"\n")
                return 13
            _bad = [(s["slide_n"], _q) for s in slides
                    for _q in _visuals.problems(s.get("visual") or "")]
            for _n, _q in _bad:
                print(f"WARNING (brief): slide {_n} **Visual:** {_q}; the designer gets "
                      "Designer's choice.")

    # 5. Render per-slide prompts. In single-slide modes, render only the target
    # slide and leave every other slide's prompt/context/meta untouched.
    target_slide_n = rebuild_slide_n if rebuild_slide_n is not None else insert_slide_n
    template_text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    render_targets = [
        (slide, seeds) for slide, seeds in zip(slides, seeds_by_slide)
        if target_slide_n is None or slide["slide_n"] == target_slide_n
    ]
    if _storyline_wait:
        render_targets = []  # the Storyline tab is open: no prompts yet
    for slide, seeds in render_targets:
        slide_n = slide["slide_n"]
        slide_dir = _p.slide_dir(args.out, slide_n)
        slide_dir.mkdir(parents=True, exist_ok=True)
        if target_slide_n is not None:
            _retire_previous_options(slide_dir)
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
            density_note=_density_note,
        )
        rendered = render_prompt(template_text, placeholders)
        rendered = page_copy_prompt(slide_dir, slide, rendered, copy_plan)
        _p.prompt_md(args.out, slide_n).write_text(rendered, encoding="utf-8")
        # Write a `_context.md` sibling that bundles the canonical reference,
        # design rules, brief metadata, and feedback ledger for the
        # per-slide worker agent to reason against.
        try:
            write_slide_context_md(slide, brand, slide_dir, slide_n, args.template,
                                   deck=brief)
        except Exception as _exc:
            sys.stderr.write(
                f"  WARN: could not write slide {slide_n} _context.md: "
                f"{type(_exc).__name__}: {_exc}\n"
            )

    # Rebuild mode: merge only the target slide's entry into the existing
    # _meta.json and stop. Every other slide's prompt, context, themed PPTX,
    # and meta entry (including artifacts) are preserved. The operator then
    # dispatches one worker for slide N, runs finalize_deck.py --slide N, picks,
    # and re-runs compile_picks.py to graft the rebuilt slide into the deck.
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
        record_page_copies(meta_path, copy_plan)
        rb_dir = _p.slide_dir(args.out, rebuild_slide_n)
        print(f"Re-prepped slide {rebuild_slide_n} at:")
        print(f"  {rb_dir.resolve()}")
        print()
        print(f"Updated deck manifest:")
        print(f"  {meta_path.resolve()}")
        print()
        print(f"Next, to rebuild slide {rebuild_slide_n} (its worker reads "
              f"{rb_dir / '_context.md'} then {rb_dir / '_prompt.md'}):")
        for _ln in review_sequence_lines(args.out, args.template, rebuild_slide_n):
            print(_ln)
        for _ln in page_copy_target_lines(copy_plan, rebuild_slide_n, args.out):
            print(_ln)
        record_prep_with_notice(args.out, _deck_hash, "rebuild")
        _one_page_after_prep(args.out)
        _sl = record_storyline(args.out, args.brief, getattr(args, "storyline", None))
        if _sl:
            print(_sl)
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
        record_page_copies(meta_path, copy_plan)
        # Keep the human-readable dispatch plan's numbering in sync with the
        # shifted _meta.json (best-effort; never fails the insert).
        plan_path = regenerate_dispatch_plan_from_meta(args.out)
        ins_dir = _p.slide_dir(args.out, insert_slide_n)
        print(f"Inserted new slide {insert_slide_n} (build now has {existing_slide_count + 1} slides):")
        print(f"  {ins_dir.resolve()}")
        print()
        print(f"Updated deck manifest:")
        print(f"  {meta_path.resolve()}")
        if plan_path is not None:
            print(f"Renumbered dispatch plan:")
            print(f"  {plan_path.resolve()}")
        print()
        # Say the frozen count out loud (2026-10-13: workers were told "option A
        # only" while their _prompt.md said three; finalize then refused eight
        # slides for 16 missing options).
        _letters = list(_p.option_letters())
        print(f"Slide {insert_slide_n} is set up for {len(_letters)} design(s): option "
              f"{', '.join(_letters)} (frozen in _meta.json; its _prompt.md says the same).")
        print("  The worker builds exactly that many. Never tell a worker a different number.")
        _other = 1 if len(_letters) > 1 else 3
        print(f"  To change it, prep this slide again before any worker runs: py -3 "
              f"scripts/build_deck.py --template \"{args.template}\" --out \"{args.out}\" "
              f"--slide {insert_slide_n} --options {_other}")
        print()
        print(f"Next, to build the inserted slide {insert_slide_n} (its worker reads "
              f"{ins_dir / '_context.md'} then {ins_dir / '_prompt.md'}):")
        for _ln in review_sequence_lines(args.out, args.template, insert_slide_n):
            print(_ln)
        print()
        print(f"  Note: the deck-level RESULT.md still shows the pre-insert numbering — it")
        print(f"  refreshes on the next FULL finalize (finalize_deck.py --out <out> with no")
        print(f"  --slide). The single-slide finalize in step b writes RESULT-slide-{insert_slide_n:02d}.md.")
        for _ln in page_copy_target_lines(copy_plan, insert_slide_n, args.out):
            print(_ln)
        record_prep_with_notice(args.out, _deck_hash, "insert")
        _one_page_after_prep(args.out)
        _sl = record_storyline(args.out, args.brief, getattr(args, "storyline", None))
        if _sl:
            print(_sl)
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
    record_page_copies(meta_path, copy_plan)

    if _storyline_wait:
        record_prep_with_notice(args.out, _deck_hash, "prep")
        _sl = record_storyline(args.out, args.brief, getattr(args, "storyline", None))
        # the page needs the manifest: write it again now that it exists
        import record_storyline as _rs
        _rs.open_stage(args.out.resolve(), args.brief.resolve())
        print(f"Prepped {slide_total} slides at:")
        print(f"  {args.out.resolve()}")
        print()
        for _ln in _storyline_wait:
            print(_ln)
        return 0

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
    _copy_lines = page_copy_lines(copy_plan, args.out, args.template, plan_path)

    # Console summary (paths as plain text)
    print(f"Prepped {slide_total} slides at:")
    print(f"  {args.out.resolve()}")
    print()
    # Takeaways over ~130 characters wrap to a second line under the title and
    # crowd the body; designers then squeeze around them. Say so now, while the
    # brief is still cheap to edit.
    _long = [(s.get("slide_n"), len((s.get("so_what") or "").strip()))
             for s in slides
             if "cover" not in (s.get("archetype") or "").lower()
             and len((s.get("so_what") or "").strip()) > 130]
    if _long:
        print("Takeaway lines over 130 characters (they will wrap to two lines): "
              + ", ".join(f"slide {n} ({k})" for n, k in _long))
        print("  Tighten them in the brief and re-seal it, or accept the wrap.")
        print()
    if brief.get("warnings"):
        print(f"Brief warnings: {len(brief['warnings'])} part(s) of the brief prep could "
              "not read; the designers will not see them:")
        for _w in brief["warnings"]:
            print(f"  WARNING: {_w}")
        print("  Fix the brief and prep again, or tell the user what is being left out.")
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
    print("Next (each worker reads _context.md first, then _prompt.md, in its slide_NN/):")
    for _ln in review_sequence_lines(args.out, args.template):
        print(_ln)
    for _ln in pinned_pages_note(slides):
        print(_ln)
    for _ln in _copy_lines:
        print(_ln)
    record_prep_with_notice(args.out, _deck_hash, "prep")
    _sl = record_storyline(args.out, args.brief, getattr(args, "storyline", None))
    if _sl:
        print(_sl)
    _pg = _one_page_after_prep(args.out)
    for _ln in _storyline_lines:
        print(_ln)
    if _pg:
        print(f"Slide Lab page (one file for the whole build): {_pg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
