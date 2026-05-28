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
from typing import Any

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


class DeckMeta(BaseModel):
    deck_type:         str = ""
    governing_thought: str = ""
    audience:          str = ""


class MetaJson(BaseModel):
    schema_version: int = Field(..., description="Must be in SUPPORTED_SCHEMA_VERSIONS")
    template:       str
    brief:          str
    out:            str
    mermaid_theme:  str
    client_slug:    str
    slide_count:    int
    generated_at:   str  # Top-level; build_review reads from here
    brand_primary:  str = ""  # Added v2 (P1.3). Empty string allowed for legacy v1 files.
    brand_accent:   str = ""  # Same.
    slides:         list[SlideMeta]
    deck_meta:      DeckMeta


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
