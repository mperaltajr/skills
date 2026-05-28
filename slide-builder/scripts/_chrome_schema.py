"""_chrome_schema.py — pydantic schema for <template-stem>.chrome.yml.

Single source of truth for client-template layout chrome geometry. Written by
register_template.py at registration time; consumed by finalize_deck.py +
build_deck.py at build time.

Two layout classes (locked v0.2 2026-05-28 in
_decisions/v0.2-layout-inheritance-design-lock-2026-05-28.md):

  body-canonical
    Blank-ish body + chrome frame. Master decorates; layout is mostly empty.
    Slide Lab uses CANONICAL positions (see CANONICAL_* constants below) for
    title/subtitle/footnote/source/page-number. Position fields on
    LayoutChrome stay None. ~90% of consulting body layouts.

  bespoke
    Art-directed (cover, section divider, dark hero). Chrome IS the slide;
    placeholder positions are extracted from the template and stored in
    LayoutChrome's position fields. Helpers use those positions directly.

The chrome.yml file is THE canonical home for client-template-specific
geometry. Pattern helpers, QC rules, and twin builders read it via
finalize_deck.py's _ACTIVE_CHROME injection; they never re-encode positions
locally. Numeric coordinate literals outside this module + chrome.yml are
a contract violation enforced by `_contract.py::check_chrome_field_single_source`.

Loud-failure contract
---------------------
Any sidecar/config file whose absence is recoverable must be recovered loudly.
If chrome.yml is missing or any required position field is None for a bespoke
layout, helpers raise ChromeSidecarMissingError. Silent fallback to hardcoded
defaults is the v1 slot-mapping bug class — see feedback_sidecar_fallback_must_be_loud.

Adding a new field
------------------
Bump CHROME_SCHEMA_VERSION_CURRENT. Update SUPPORTED_SCHEMA_VERSIONS to gate
which versions readers accept. Re-register every template to repopulate.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

# Bumped when the schema shape changes. Stay in lockstep with register_template
# (writer) and finalize_deck (reader).
CHROME_SCHEMA_VERSION_CURRENT: int = 1
SUPPORTED_SCHEMA_VERSIONS: tuple[int, ...] = (1,)


# ---------------------------------------------------------------------------
# Canonical body-canonical chrome positions
# ---------------------------------------------------------------------------
#
# These are the positions Slide Lab uses for body-canonical layouts where the
# master decorates and the layout is intentionally mostly-empty. Living here
# (and not in twins/helpers.py) keeps chrome geometry in a single source of
# truth — the same file the contract test allowlists.
#
# 1280x720 reference canvas; px units, 96 DPI assumed.

# Title block — bottom-anchored (feedback_title_bottom_anchor: 2-line titles
# grow UPWARD, never displace subtitle).
CANONICAL_TITLE_X: int = 64
CANONICAL_TITLE_Y: int = 20
CANONICAL_TITLE_W: int = 1000
CANONICAL_TITLE_H: int = 80
CANONICAL_TITLE_FONT_PT: int = 28

# Subtitle — single-line italic, just below title bottom.
CANONICAL_SUBTITLE_H: int = 26
CANONICAL_SUBTITLE_FONT_PT: int = 16

# Footer invariant zone (feedback_invariant_zone_chrome): footnote + source +
# page-number only. No ACCENTURE/DRAFT/CONFIDENTIAL tags.
CANONICAL_FOOTNOTE_X: int = 58
CANONICAL_FOOTNOTE_Y: int = 672
CANONICAL_FOOTNOTE_W: int = 1164
CANONICAL_FOOTNOTE_H: int = 16
CANONICAL_FOOTNOTE_FONT_PX: int = 10

CANONICAL_SOURCE_X: int = 58
CANONICAL_SOURCE_Y: int = 688
CANONICAL_SOURCE_W: int = 1100
CANONICAL_SOURCE_H: int = 16
CANONICAL_SOURCE_FONT_PX: int = 10

CANONICAL_PAGE_NUMBER_X: int = 1170
CANONICAL_PAGE_NUMBER_Y: int = 688
CANONICAL_PAGE_NUMBER_W: int = 52
CANONICAL_PAGE_NUMBER_H: int = 16
CANONICAL_PAGE_NUMBER_FONT_PX: int = 11


def canonical_title_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_TITLE_X, y_px=CANONICAL_TITLE_Y,
        w_px=CANONICAL_TITLE_W, h_px=CANONICAL_TITLE_H,
        font_pt=CANONICAL_TITLE_FONT_PT, anchor="bottom",
    )


def canonical_subtitle_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_TITLE_X,
        y_px=CANONICAL_TITLE_Y + CANONICAL_TITLE_H + 8,
        w_px=CANONICAL_TITLE_W - 120,
        h_px=CANONICAL_SUBTITLE_H,
        font_pt=CANONICAL_SUBTITLE_FONT_PT, anchor="top",
    )


def canonical_footnote_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_FOOTNOTE_X, y_px=CANONICAL_FOOTNOTE_Y,
        w_px=CANONICAL_FOOTNOTE_W, h_px=CANONICAL_FOOTNOTE_H,
        font_pt=None, anchor="top",
    )


def canonical_source_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_SOURCE_X, y_px=CANONICAL_SOURCE_Y,
        w_px=CANONICAL_SOURCE_W, h_px=CANONICAL_SOURCE_H,
        font_pt=None, anchor="top",
    )


def canonical_page_number_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_PAGE_NUMBER_X, y_px=CANONICAL_PAGE_NUMBER_Y,
        w_px=CANONICAL_PAGE_NUMBER_W, h_px=CANONICAL_PAGE_NUMBER_H,
        font_pt=None, anchor="top",
    )


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class BoxPx(BaseModel):
    """A bounding box in 1280x720 reference-canvas px coordinates."""
    x_px: int
    y_px: int
    w_px: int
    h_px: int
    font_pt: int | None = None
    anchor: Literal["top", "middle", "bottom"] = "top"


class LayoutChrome(BaseModel):
    """Chrome spec for one named layout in the client template."""
    name: str
    layout_class: Literal["body-canonical", "bespoke"]
    text_role: Literal["dark_on_light", "light_on_dark"]
    background: Literal["light", "dark"]
    has_page_number: bool
    # Position fields — populated only for bespoke layouts; None for
    # body-canonical (canonical_*_box() constants supply the geometry).
    title: BoxPx | None = None
    subtitle: BoxPx | None = None
    footnote: BoxPx | None = None
    source: BoxPx | None = None
    page_number: BoxPx | None = None


class ChromeSpec(BaseModel):
    """Top-level chrome.yml document — version + sha8 + per-layout chrome."""
    schema_version: int = CHROME_SCHEMA_VERSION_CURRENT
    source_template_sha8: str
    layouts: dict[str, LayoutChrome]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ChromeSidecarMissingError(RuntimeError):
    """Raised when chrome.yml is absent OR a required field is None.

    Silent fallback to hardcoded defaults is the v1 slot-mapping bug class.
    Helpers MUST raise this rather than substitute a default — production-grade
    bar requires the operator to re-register the template instead of shipping
    a slide built against guessed geometry.

    See feedback_sidecar_fallback_must_be_loud.md.
    """


class ChromeSchemaError(RuntimeError):
    """Raised when chrome.yml fails validation or has unsupported version."""


# ---------------------------------------------------------------------------
# Loader / validator
# ---------------------------------------------------------------------------

def validate_chrome_dict(raw: dict[str, Any]) -> ChromeSpec:
    """Validate a parsed dict against ChromeSpec. Raises ChromeSchemaError on failure."""
    version = raw.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ChromeSchemaError(
            f"chrome.yml schema_version={version!r} not supported. "
            f"Supported: {SUPPORTED_SCHEMA_VERSIONS}. "
            f"Re-register the template (register_template.py propose -> commit)."
        )
    try:
        return ChromeSpec.model_validate(raw)
    except ValidationError as e:
        raise ChromeSchemaError(
            f"chrome.yml failed validation:\n{e}"
        ) from e


def load_chrome_yml(chrome_yml_path: Path) -> ChromeSpec:
    """Load + validate <template-stem>.chrome.yml.

    Raises ChromeSidecarMissingError if the file does not exist;
    ChromeSchemaError on validation failure.
    """
    if not chrome_yml_path.exists():
        raise ChromeSidecarMissingError(
            f"chrome.yml not found at {chrome_yml_path}. "
            f"Register the template first: "
            f"register_template.py propose -> commit."
        )
    import yaml
    raw = yaml.safe_load(chrome_yml_path.read_text(encoding="utf-8")) or {}
    return validate_chrome_dict(raw)


def dump_chrome_yml(spec: ChromeSpec, chrome_yml_path: Path) -> None:
    """Serialize ChromeSpec to YAML at the given path."""
    import yaml
    chrome_yml_path.parent.mkdir(parents=True, exist_ok=True)
    data = spec.model_dump(mode="python", exclude_none=False)
    text = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
    chrome_yml_path.write_text(text, encoding="utf-8")
