"""_meta_schema.py — pydantic schema for <out>/_meta.json.

Single source of truth for the deck manifest. Writer (build_deck.py::write_meta_json)
constructs and validates a MetaJson model before serialising. Readers
(finalize_deck.py, compile_picks.py, build_review.py, build_gate_preview.py)
parse the JSON through `load_meta_json(out_dir)` which validates on the way in
and raises with a precise field-level error message if the shape drifts.

Adding a new field
------------------
1. Add it to MetaJson (or the nested model) with the correct type and an
   optional default for backward compatibility within the same schema version.
2. If the change is a rename, type change, or required-field addition:
   - Bump META_SCHEMA_VERSION_CURRENT (matched by build_deck.py).
   - Update SUPPORTED_SCHEMA_VERSIONS to gate which versions readers accept.

Removing a field
----------------
Bump version and drop from the current model. Keep a thin compat shim for the
previous version only if old _meta.json files might still be in circulation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

# Bumped in v0.2 P1.4 when the per-slide layout field landed. Stay in lockstep
# with build_deck.py::META_SCHEMA_VERSION.
META_SCHEMA_VERSION_CURRENT: int = 3

# Versions readers accept. v2 is a transition cushion for any _meta.json
# written before P1.4 landed; the compat shim in validate_meta_dict() bumps
# v2 dicts to v3 in-memory and injects layout="body_canonical_light".
# Remove v2 once enough time has passed to be confident no v2 metas remain.
SUPPORTED_SCHEMA_VERSIONS: tuple[int, ...] = (2, 3)

# Default layout name used by the v2 -> v3 compat shim when a per-slide
# layout field is missing. Chosen to match the most-common body slide in
# consulting decks (FedEx, Accenture, NFL templates all expose a similarly-
# named light body layout); if the template's chrome.yml doesn't have this
# exact name, finalize_deck's _pick_default_layout_name takes over at build
# time.
V2_COMPAT_DEFAULT_LAYOUT: str = "body_canonical_light"


class SlideMeta(BaseModel):
    n: int
    title: str = ""
    forecasted_pattern: str = ""
    page_type: str = ""
    # v0.2 P1.4: which chrome.yml layout each slide is built against. Writer
    # (build_deck.py) populates this from the brief's `**Layout:**` field or
    # the deck-level `default_layout:`; readers (finalize_deck.py) graft each
    # slide onto the named layout. Empty string only legal during the v2
    # compat shim transition window — see validate_meta_dict.
    layout: str = ""
    # v2.2 (2026-06-05, SLIDE_LAB_FEEDBACK_LOG #3): so-what subtitle text to
    # populate into the layout's SUBTITLE placeholder. Source: brief's
    # **So-what:** line per slide. Empty string is legitimate (cover slides,
    # divider slides, or any slide whose title is self-contained). Writer
    # (build_deck.py) populates from the brief; reader (finalize_deck.py)
    # passes through as fallback_subtitle to _apply_body_canonical_finishing.
    subtitle: str = ""
    # M1 — Pattern B (2026-06-16) optional fields. Default None preserves
    # legacy semantics: readers that don't know about Pattern B see slides
    # with pattern=None and route through the existing python-pptx-direct
    # path verbatim. Writers set these only when --pattern is not "legacy"
    # (or when settings.json::default_pattern enables Pattern B).
    #
    #   pattern  ∈ {"B", "C", None}
    #     B = HTML-spec → translator → native python-pptx (Pattern B routing)
    #     C = native python-pptx direct (no HTML stage); identical to legacy
    #     None = field absent (legacy behavior; finalize_deck routes through
    #            existing graft/render path)
    #   artifacts: per-slide artifact paths, schema-versioned. Empty dict
    #     for legacy slides; populated with {html, png_target,
    #     translated_py, translated_pptx, translation_report} keys for
    #     Pattern B slides as the build progresses.
    pattern: Optional[str] = None
    artifacts: Optional[dict[str, Any]] = None


class DeckMeta(BaseModel):
    deck_type:         str = ""
    governing_thought: str = ""
    audience:          str = ""


class MetaJson(BaseModel):
    schema_version: int = Field(..., description="Must be in SUPPORTED_SCHEMA_VERSIONS")
    template:       str
    brief:          str
    out:            str
    # Optional legacy field — older _meta.json files carry a path here, new
    # writes omit it. Kept as an ignored optional so historical files still
    # validate without re-writing them.
    mermaid_theme:  str = ""
    client_slug:    str
    slide_count:    int
    generated_at:   str  # Top-level; build_review reads from here
    brand_primary:  str = ""  # Empty string allowed for legacy files.
    brand_accent:   str = ""  # Same.
    slides:         list[SlideMeta]
    deck_meta:      DeckMeta
    # M1 — Pattern B (2026-06-16) optional top-level fields. Default None /
    # empty preserves legacy semantics: readers that don't know about
    # Pattern B see these as absent and route through the existing pipeline.
    # Writers set these only when --pattern != "legacy".
    #
    #   pattern_default  ∈ {"legacy", "auto", "B", "C", None}
    #     "legacy" = use pre-Pattern-B pipeline verbatim (default when no flag)
    #     "auto"   = per-slide routing via _classify_all_slides
    #     "B"      = force all slides to Pattern B
    #     "C"      = force all slides to Pattern C (native, no HTML stage)
    #     None     = field absent; readers treat as "legacy"
    #   pattern_per_slide: optional {slide_n_str: "B"|"C"} dict produced by
    #     the classifier when pattern_default is "auto". Absent / empty for
    #     non-auto modes.
    #   html_render_canvas: locked at "1280x720" per Decision 1; only set
    #     when Pattern B is in play.
    #   translator_dispatched: flipped True after Stage 3.5 completes.
    #   translation_reports: {slide_n_str: report_relative_path} populated
    #     by Stage 3.5 dispatcher; consumed by build_review.py for SSIM
    #     surfacing.
    pattern_default:       Optional[str] = None
    pattern_per_slide:     Optional[dict[str, str]] = None
    html_render_canvas:    Optional[str] = None
    translator_dispatched: bool = False
    translation_reports:   dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Errors + loader
# ---------------------------------------------------------------------------

class MetaJsonSchemaError(RuntimeError):
    """Raised when <out>/_meta.json fails validation or has an unsupported version."""


def validate_meta_dict(raw: dict[str, Any]) -> MetaJson:
    """Validate a parsed dict against MetaJson. Raises MetaJsonSchemaError on failure.

    v2 compat shim: when raw['schema_version'] == 2, the dict is bumped
    in-memory to v3 with `layout = V2_COMPAT_DEFAULT_LAYOUT` injected on each
    slide that lacks one. A migration-required warning is written to stderr so
    finalize_deck surfaces it in RESULT.md downstream.
    """
    import sys
    version = raw.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise MetaJsonSchemaError(
            f"_meta.json schema_version={version!r} is not supported. "
            f"Supported: {SUPPORTED_SCHEMA_VERSIONS}. "
            f"Run a newer build_deck.py or migrate the file."
        )
    if version == 2:
        # In-memory bump. Don't write back to disk — the next build_deck.py
        # run rewrites the meta with v3 properly.
        raw = {**raw, "schema_version": 3}
        slides = []
        for s in raw.get("slides", []) or []:
            if not isinstance(s, dict):
                slides.append(s)
                continue
            if not s.get("layout"):
                s = {**s, "layout": V2_COMPAT_DEFAULT_LAYOUT}
            slides.append(s)
        raw["slides"] = slides
        sys.stderr.write(
            f"WARN: _meta.json v2 loaded with v3 compat shim "
            f"(layout={V2_COMPAT_DEFAULT_LAYOUT!r} injected on slides "
            f"without one). Re-run build_deck.py against a brief with "
            f"`default_layout:` or per-slide `**Layout:**` to upgrade.\n"
        )
    try:
        return MetaJson.model_validate(raw)
    except ValidationError as e:
        # Re-raise with the pydantic field-level detail intact but as our
        # named exception so callers can catch precisely.
        raise MetaJsonSchemaError(
            f"_meta.json failed validation:\n{e}"
        ) from e


def load_meta_json(out_dir: Path) -> MetaJson:
    """Load and validate <out_dir>/_meta.json. Returns the parsed model.

    Raises FileNotFoundError if the file doesn't exist, MetaJsonSchemaError if
    the parsed dict fails validation.
    """
    # Import here to avoid a circular dep if _paths is imported by callers
    # that haven't set up sys.path yet.
    import _paths as _p
    meta_path = _p.meta_json(out_dir)
    if not meta_path.exists():
        raise FileNotFoundError(f"_meta.json not found at {meta_path}")
    raw = json.loads(meta_path.read_text(encoding="utf-8"))
    return validate_meta_dict(raw)


def validate_warn(meta: dict[str, Any], source: str = "") -> None:
    """Belt-and-braces reader-side validation. Writes a warning to stderr on
    schema failure but does NOT raise — readers degrade gracefully on missing
    fields via `.get(..., default)` patterns.

    Writer-side validation (`build_deck.py::write_meta_json`) is the
    load-bearing gate; this helper is the reader-side mirror that catches
    metas authored by older builds, hand-edited dev files, or drift from a
    schema bump that landed in build_deck but not yet in the reader.

    Use at every reader site immediately after `json.loads()`:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        validate_warn(meta, source="finalize_deck")

    `source` is the calling script name; surfaces in the warning so the
    operator can tell which script flagged the drift.
    """
    import sys
    try:
        validate_meta_dict(meta)
    except MetaJsonSchemaError as exc:
        prefix = f"[{source}] " if source else ""
        sys.stderr.write(f"{prefix}WARN: _meta.json schema validation: {exc}\n")
