"""_chrome_schema.py — pydantic schema for <template-stem>.chrome.yml.

Single source of truth for client-template layout chrome geometry. Written by
register_template.py at registration time; consumed by finalize_deck.py +
build_deck.py at build time.

Two layout classes:

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
geometry. Layout helpers, QC rules, and twin builders read it via
finalize_deck.py's _ACTIVE_CHROME injection; they never re-encode positions
locally. Numeric coordinate literals outside this module + chrome.yml are
a contract violation enforced by `_contract.py::check_chrome_field_single_source`.

Loud-failure contract
---------------------
Any sidecar/config file whose absence is recoverable must be recovered loudly.
If chrome.yml is missing or any required position field is None for a bespoke
layout, helpers raise ChromeSidecarMissingError. Silent fallback to hardcoded
defaults is the slot-mapping bug class — see feedback_sidecar_fallback_must_be_loud.

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
#
# Schema version 2 adds the body-canonical layout-inheritance fields:
#   title_placeholder_idx, body_top_y_px, body_bottom_y_px, body_overlay_hex.
# Version-1 chrome.yml is still readable — validate_chrome_dict defaults the
# new fields to None so version-1 sidecars load without re-registration.
# Templates already registered at version 1 keep working in "strip-and-redraw"
# mode until they are re-registered.
CHROME_SCHEMA_VERSION_CURRENT: int = 2
SUPPORTED_SCHEMA_VERSIONS: tuple[int, ...] = (1, 2)


# ---------------------------------------------------------------------------
# Canvas <-> EMU helpers
# ---------------------------------------------------------------------------
#
# python-pptx convention at 96 DPI is 1 px = 9525 EMU. Slide Lab locked the
# sketch-path HTML render canvas at 1280×720, which makes the
# px↔EMU mapping exact: 12,192,000 EMU (the standard 16:9 slide width) ÷
# 1280 px = 9525. There is no scaling factor — one HTML pixel is one OOXML
# EMU step.
#
# These helpers are the canonical location for that conversion. Used by
# register_template.py (which extracts placeholder geometry from PPTX
# layout XML) and by the sketch-path translator agent when it converts
# HTML pixel coordinates from `getComputedStyle()` into `Emu(...)` kwargs
# for `slide.shapes.add_shape(...)`. No magic 9525s elsewhere — see
# `_contract.py::check_chrome_field_single_source` for the contract test.
EMU_PER_PX_AT_1280: int = 9525


def emu_to_px(emu: int) -> int:
    """Convert OOXML EMU to HTML pixel at the locked 1280×720 canvas scale."""
    return int(round(int(emu) / EMU_PER_PX_AT_1280))


def px_to_emu(px: int) -> int:
    """Convert HTML pixel to OOXML EMU at the locked 1280×720 canvas scale."""
    return int(round(int(px) * EMU_PER_PX_AT_1280))


def _emu_to_px_dict(emu_box: dict) -> dict:
    """Convert a {x,y,width,height,...} EMU dict to its pixel equivalent.

    Used by register_template.py to derive `BoxPx` fields from the EMU
    values it reads off PPTX layout placeholders.
    """
    return {k: emu_to_px(v) for k, v in emu_box.items()}


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

# Body-zone fallbacks for body-canonical layouts that lack title / footer
# placeholders during registration. Used only when register_template cannot
# locate the inherited placeholder bounds; real templates populate these
# fields per layout in chrome.yml.
CANONICAL_BODY_TOP_Y: int = 110
CANONICAL_BODY_BOTTOM_Y: int = 660


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
# Title-wrap line count
# ---------------------------------------------------------------------------

class TitleMetricsUnavailableError(RuntimeError):
    """Raised when title line-count cannot be measured because the configured
    TTF font cannot be loaded or Pillow is missing. Per
    feedback_sidecar_fallback_must_be_loud — silent char-count fallback was
    the bug class we're not repeating. Recovery: re-run register_template
    so it records the brand TTF path in brand.yml.
    """


def _find_brand_ttf(font_name: str | None = None) -> str | None:
    """Discover a brand TTF on disk by name. Returns absolute path or None.

    Scans `%LOCALAPPDATA%\\Microsoft\\Windows\\Fonts` (user fonts) then
    `C:\\Windows\\Fonts` (system fonts) for a file matching `font_name`. Used
    as a transitional fallback when brand.yml doesn't yet record the TTF path;
    once register_template writes the resolved path into brand.yml, callers
    prefer that and skip this scan. With no `font_name` there is nothing to
    search for, so the function returns None.
    """
    import os
    candidates: list[str] = []
    if font_name:
        candidates.append(font_name)
    else:
        return None
    user_fonts = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")
    system_fonts = r"C:\Windows\Fonts"
    for dir_path in (user_fonts, system_fonts):
        for fn in candidates:
            full = os.path.join(dir_path, fn)
            if os.path.isfile(full):
                return full
    return None


def count_wrapped_lines(text: str, ttf_path: str | None,
                         size_pt: int, box_width_px: int) -> int:
    """Return the number of visual lines `text` wraps to in a box of width
    `box_width_px` at `size_pt` using the TTF at `ttf_path`.

    Greedy word-wrap (matches PowerPoint's behavior closely enough for the
    threshold check). Raises TitleMetricsUnavailableError when Pillow is
    missing or the TTF can't be loaded — this is a loud-fail surface per
    feedback_sidecar_fallback_must_be_loud. The caller is responsible for
    either re-registering the template to record a valid TTF path OR
    falling back to a char-count proxy and warning the operator.
    """
    if not text:
        return 0
    try:
        from PIL import ImageFont
    except ImportError as e:
        raise TitleMetricsUnavailableError(
            f"Pillow not available for title-wrap measurement: {e}. "
            f"Pillow is a pinned dependency — check requirements.txt."
        ) from e
    if not ttf_path:
        raise TitleMetricsUnavailableError(
            "No TTF path supplied for title-wrap measurement. Recovery: "
            "re-run register_template so brand.yml records the resolved "
            "title font path."
        )
    try:
        # 96 DPI: px = pt * 96/72
        font = ImageFont.truetype(ttf_path, int(round(size_pt * 96 / 72)))
    except (OSError, IOError) as e:
        raise TitleMetricsUnavailableError(
            f"Cannot load TTF {ttf_path!r}: {e}. Recovery: re-run "
            f"register_template to discover and record a valid TTF path."
        ) from e
    words = text.split()
    if not words:
        return 0
    lines = 0
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.getlength(trial) <= box_width_px:
            current = trial
        else:
            lines += 1
            current = word
    if current:
        lines += 1
    return lines


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
    # Body-canonical layout-inheritance fields.
    # For body-canonical layouts ONLY:
    #   title_placeholder_idx: which inherited placeholder holds the title
    #     (so finalize_deck writes the slide title text into the layout's
    #      title placeholder rather than drawing a free-floating textbox).
    #   subtitle_placeholder_idx: same idea for the subtitle. When set, the
    #     worker skips drawing a free-floating subtitle textbox and finalize
    #     populates the inherited subtitle placeholder instead. Subtitle
    #     drift was traced to the absence of
    #     this field — the worker drew subtitle at a hardcoded canonical
    #     position while the real subtitle placeholder sat empty.
    #   body_top_y_px / body_bottom_y_px: drawable zone between the inherited
    #     title placeholder bottom and the footer placeholder top — patterns
    #     compose body content inside this zone.
    # For bespoke layouts these remain None (covers/dividers keep today's
    # strip-and-redraw path).
    title_placeholder_idx: int | None = None
    subtitle_placeholder_idx: int | None = None
    body_top_y_px: int | None = None
    body_bottom_y_px: int | None = None
    # Title placeholder geometry (px) + controlled title font size, captured for
    # body-canonical layouts. Additive/optional (older chrome.yml files omit
    # them → None → callers fall back to canonical). Used to (a) render the
    # free-floating takeaway line as wide as the title, and (b) populate the
    # title placeholder at a consistent title_font_pt. Also feed the title-wrap
    # fit calc (finalize) which already reads title_box_width_px / title_font_pt.
    title_box_x_px: int | None = None
    title_box_y_px: int | None = None
    title_box_width_px: int | None = None
    title_box_height_px: int | None = None
    title_font_pt: int | None = None
    # body_overlay_hex retained for backward-compat with existing chrome.yml
    # files; never populated by current register_template and unread by any
    # downstream code. Slated for removal once existing templates are
    # re-registered.
    body_overlay_hex: str | None = None


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

    Silent fallback to hardcoded defaults is the slot-mapping bug class.
    Helpers MUST raise this rather than substitute a default — production-grade
    bar requires the operator to re-register the template instead of shipping
    a slide built against guessed geometry.

    See feedback_sidecar_fallback_must_be_loud.md.
    """


class ChromeSchemaError(RuntimeError):
    """Raised when chrome.yml fails validation or has unsupported version."""


class ChromeLayoutMissingError(RuntimeError):
    """Raised when a slide references a layout name that does not exist in
    the loaded chrome.yml.

    Silent fallback to a default layout was the bug that hid a
    chrome regression — slides resolved to a stand-in layout
    whose geometry didn't match the actual template. Helpers MUST raise this
    instead of substituting a default.

    See feedback_sidecar_fallback_must_be_loud.md.
    """


# Note: LegacyTemplateLayoutError (raised when an older flat sidecar layout
# is detected) lives in twins/client_theme.py, where it's the only thing
# that raises it. The duplicate definition here was removed —
# previously both files defined the same name with different parent classes
# (RuntimeError vs FileNotFoundError), which would have caught operators by
# surprise if anyone tried to except-block both.


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
