"""
Client theme — brand.yml / theme.json sidecar reader.

Theme detection used to live here as a stack of HSV-saturation heuristics
(`_pick_brand_colors`, `_pick_primary_mid`, `_pick_accent_soft`, `is_branded`,
slot-position fallbacks). Those were retired in the 2026-05 rewrite because
they produced wrong colors on real templates — most visible: NFL stadium
photos bleeding through finalized decks, ACN deep purple being passed over
in favor of bright purple, FedEx orange/purple swap.

The new contract:

    Every client template ships with two sidecar files, written ONCE by
    `scripts/register_template.py`:

      <template_stem>.brand.yml    — 15 lines, human-editable, ground truth
      <template_stem>.theme.json   — SHA-stamped audit, machine-generated

    `load_client_theme(template_path)` reads both:
      1. Confirms brand.yml + theme.json exist (else FileNotFoundError)
      2. Confirms theme.json's template_sha matches the actual template
         file's SHA-256 (else ValueError — template was edited post-register)
      3. Builds a ClientTheme dataclass with brand.yml's values as direct
         fields (NOT derived). brand_primary, brand_accent, cover_bg_hex,
         strip_master_backgrounds all come straight from brand.yml.

Build-time refusal: if either sidecar is missing or the SHA mismatches,
`load_client_theme` raises. Callers (finalize_deck.py) catch this and
abort with a clear "register the template first" message.

Color map: `ClientTheme.color_map()` produces a Slide-Lab-literal-hex →
client-hex remapping. Primary, accent, and the text/card neutrals are
mechanical derivations from the brand.yml values (no heuristic picking).

Usage (composer-internal):

    theme = load_client_theme("path/to/Client Template.pptx")
    color_map = theme.color_map()
    apply_theme_to_shape_xml(shape.element, color_map,
                             theme.major_font, theme.minor_font)
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from pptx import Presentation

try:
    import yaml
except ImportError:  # pragma: no cover
    raise ImportError(
        "PyYAML required for brand.yml sidecar reader. Install: pip install pyyaml"
    )


# ---------------------------------------------------------------------------
# Slide Lab default palette (from helpers.py — must stay in sync)
# ---------------------------------------------------------------------------

# These are the literal RGB hex strings (no leading #) that every twin builder
# bakes into its shapes via helpers.py. The color_map() function maps each of
# these to the closest equivalent in the client's theme. KEEP IN SYNC WITH
# helpers.py — these are the hex values python-pptx writes into XML, and the
# graft pass matches on these exact bytes.
SLIDE_LAB_BRAND_PRIMARY = "460073"      # helpers.BRAND_PRIMARY (deep purple)
SLIDE_LAB_BRAND_PRIMARY_MID = "7500C0"  # helpers.BRAND_PRIMARY_MID (medium purple)
SLIDE_LAB_BRAND_ACCENT = "A100FF"       # helpers.BRAND_ACCENT (electric purple)
SLIDE_LAB_BRAND_ACCENT_SOFT = "C2A3FF"  # helpers.BRAND_ACCENT_SOFT (light purple)
SLIDE_LAB_TEXT_DARK = "000000"          # helpers.TEXT_DARK (black)
SLIDE_LAB_TEXT_MID = "595959"           # helpers.TEXT_MID (mid grey)
SLIDE_LAB_TEXT_FAINT = "888888"         # helpers.TEXT_FAINT (light grey)
SLIDE_LAB_CARD_BG_1 = "E6DCFF"          # helpers.CARD_BG (very light purple)
SLIDE_LAB_CARD_BG_2 = "F8F4FC"          # legacy alias (some twins use this)
SLIDE_LAB_CARD_BORDER_1 = "C2A3FF"      # helpers.CARD_BORDER (light purple)
SLIDE_LAB_CARD_BORDER_2 = "E5D5F0"      # legacy alias

# NOTE: SLIDE_LAB_BRAND_ACCENT_SOFT and SLIDE_LAB_CARD_BORDER_1 are both
# "C2A3FF" — same literal hex. In the color_map dict this means the second
# write wins for that key. color_map() resolves the collision deterministically
# (see comment near _color_map assignment).

# Off-palette colors agents have been observed using (despite not being in
# helpers.py). We map these too so existing decks survive the theme pass.
OFF_PALETTE_TEXT_DARK_ALIASES = ("333333", "1E293B", "0F172A", "111827")
OFF_PALETTE_TEXT_MID_ALIASES = ("475569", "6B7280", "4B5563")
OFF_PALETTE_TEXT_FAINT_ALIASES = ("CBD5E1", "D1D5DB", "9CA3AF")
OFF_PALETTE_BORDER_ALIASES = ("E3E3E3", "E5E7EB", "E2E8F0", "D4D4D8")

SLIDE_LAB_DEFAULT_FONT = "Inter"


# ---------------------------------------------------------------------------
# Color math — mechanical derivations only (no heuristic picking)
# ---------------------------------------------------------------------------
def _mix_hex(hex_a: str, hex_b: str, ratio: float) -> str:
    """Blend two RGB hex strings. ratio=0 -> hex_a, ratio=1 -> hex_b.

    Internal name kept for the many existing call sites in this module.
    The public alias `mix_hex` below; new code should
    use the public name.
    """
    a_s = (hex_a or "").lstrip("#")
    b_s = (hex_b or "").lstrip("#")
    a = [int(a_s[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(b_s[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{int(a[i] + (b[i] - a[i]) * ratio):02X}" for i in range(3))


# Public alias (Pattern B M3, 2026-06-16). Public alias of `_mix_hex` so
# register_template.py::write_brand_css and the Pattern B translator can
# import without reaching into a private name. Same semantics; same return.
mix_hex = _mix_hex


def hex_to_rgbcolor(hex_str: str):
    """Convert '#4D148C' or '4D148C' to python-pptx RGBColor.

    Pattern B helper. Used by the translator agent (M4+) when
    converting CSS hex colors back to native python-pptx fills. Raises
    ValueError on malformed input — translator surfaces the slide with QC
    rule R4 (the translator-blocked severity).
    """
    from pptx.dml.color import RGBColor
    s = (hex_str or "").lstrip("#").upper()
    if len(s) != 6:
        raise ValueError(
            f"hex must be 6 chars after stripping '#'; got {hex_str!r}"
        )
    try:
        return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    except ValueError as exc:
        raise ValueError(f"hex contains non-hex chars: {hex_str!r}") from exc


def css_color_to_rgbcolor(css_value: str):
    """Parse a CSS color value. Returns (RGBColor, alpha) where alpha is 0.0-1.0.

    Supports the CSS forms the Pattern B translator encounters in computed
    styles: hex `#RGB`/`#RRGGBB`, `rgb(r,g,b)`, `rgba(r,g,b,a)`. Spec 2 §3.
    Raises ValueError on unsupported forms (named colors, hsl(), color()).
    """
    import re
    v = (css_value or "").strip()
    if not v:
        raise ValueError("empty CSS color")
    if v.startswith("#"):
        body = v.lstrip("#")
        if len(body) == 3:
            v = "#" + "".join(c * 2 for c in body)
        return hex_to_rgbcolor(v), 1.0
    m = re.match(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
        v, flags=re.IGNORECASE,
    )
    if m:
        from pptx.dml.color import RGBColor
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        for n, name in ((r, "r"), (g, "g"), (b, "b")):
            if not 0 <= n <= 255:
                raise ValueError(f"CSS {name} channel out of range in {css_value!r}")
        alpha = float(m.group(4)) if m.group(4) is not None else 1.0
        return RGBColor(r, g, b), alpha
    raise ValueError(f"unsupported CSS color form: {css_value!r}")


def resolve_css_var(var_expr: str, brand_css_vars: dict) -> str:
    """Resolve a `var(--name)` or `var(--name, fallback)` expression.

    Pattern B helper (Spec 2 §4 "static resolution"). `brand_css_vars` is
    the dict the translator builds by parsing the `:root` block of
    brand.css. Returns the resolved CSS value (typically a hex string)
    or raises KeyError when the variable is undefined and no fallback was
    given.
    """
    import re
    m = re.match(
        r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*([^)]+?)\s*)?\)",
        (var_expr or "").strip(),
    )
    if not m:
        raise ValueError(f"not a CSS var() expression: {var_expr!r}")
    name, fallback = m.group(1), m.group(2)
    if name in brand_css_vars:
        return brand_css_vars[name]
    if fallback is not None:
        return fallback
    raise KeyError(f"CSS variable {name!r} not defined and no fallback")


def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """WCAG 2.1 contrast ratio between two hex colors. Returns a float >= 1.0.

    Pattern B helper (Spec 2 §5). Used by register_template.py to warn
    when brand primary on brand accent fails the AA 4.5:1 threshold.
    Pure function; safe on any 6-digit hex (with or without leading '#').
    """
    def _rel_lum(hex_str: str) -> float:
        s = (hex_str or "").lstrip("#")
        rgb = [int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        rgb = [
            (c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            for c in rgb
        ]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    l1, l2 = _rel_lum(fg_hex), _rel_lum(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _normalize_hex(value: str) -> str:
    """Strip leading '#' and uppercase a hex string. Returns '' for falsy."""
    if not value:
        return ""
    v = value.strip().lstrip("#").upper()
    return v if len(v) == 6 else v.zfill(6)[:6]


# ---------------------------------------------------------------------------
# Brand sidecar reader (brand.yml + theme.json)
# ---------------------------------------------------------------------------
def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(str(path), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_paths(template_path: Path) -> tuple:
    """Return (brand_yml_path, theme_json_path) for a given template.

    Resolves via _paths.py to the v0.4 subfolder layout
    (`<template-stem>/brand.yml`, `<template-stem>/theme.json`).
    """
    # Local import: twins/ is imported in many places where the scripts/
    # dir isn't on sys.path. Defer the resolve so import-time doesn't
    # require the scripts dir.
    import sys
    from pathlib import Path as _P
    _scripts = str((_P(__file__).resolve().parent.parent / "scripts").resolve())
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    import _paths as _p  # type: ignore
    return (_p.brand_yml(template_path), _p.theme_json(template_path))


def resolve_build_template(original_template: Path) -> Path:
    """Return the .pptx a build should OPEN for this registered template.

    Registration saves a normalized "build copy" next to the sidecars and
    records it in ``theme.json::build_template_path``; builds open that copy so
    every deck comes out consistent, while ALL sidecar lookups stay keyed off
    the ORIGINAL stem. Falls back to the original when no copy is recorded
    (legacy / un-normalized templates) or the recorded copy is missing.

    Rail: if handed a path that already lives inside a sidecar dir (i.e. the
    build copy itself, whose parent contains theme.json), return it unchanged —
    never try to re-resolve it, which would key sidecars off a phantom
    ``<build-template>/`` folder.
    """
    original_template = Path(original_template)
    # A real template's sidecars live in a SUBfolder (`<stem>/theme.json`), so
    # theme.json is NOT next to the .pptx. The build copy lives INSIDE that
    # subfolder, so theme.json IS next to it — use that to detect + bail.
    if (original_template.parent / "theme.json").exists():
        return original_template
    _brand, theme_json = sidecar_paths(original_template)
    try:
        data = json.loads(theme_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return original_template
    btp = (data.get("build_template_path") or "").strip()
    if btp and Path(btp).exists():
        return Path(btp)
    return original_template


class BrandSidecarMissing(FileNotFoundError):
    """Raised when brand.yml or theme.json is missing next to a template."""
    pass


class BrandSidecarStale(ValueError):
    """Raised when theme.json's template_sha doesn't match the template file."""
    pass


class LegacyTemplateLayoutError(FileNotFoundError):
    """Raised when a template is registered with the pre-v0.4 flat sidecar
    layout. Points the operator at the one-shot migration script rather than
    silently reading from the legacy path. See feedback_sidecar_fallback_must_be_loud.
    """
    pass


def load_brand_sidecar(template_path: Path) -> dict:
    """Read <template>.brand.yml and validate against <template>.theme.json.

    Returns a dict with the canonical brand fields:
      primary_hex, accent_hex, cover_bg_hex     (6-char uppercase, no '#')
      primary_slot, accent_slot, cover_bg_slot  (str slot names)
      font_heading, font_body                   (str)
      strip_master_backgrounds                  (bool)
      _template_sha                             (str — verified before return)

    Raises:
      BrandSidecarMissing — brand.yml or theme.json missing
      BrandSidecarStale   — theme.json SHA doesn't match template file
      ValueError          — brand.yml malformed
    """
    brand_yml, theme_json = sidecar_paths(template_path)

    if not brand_yml.exists() or not theme_json.exists():
        # Detect pre-v0.4 flat layout — point operator at migration script
        # rather than ask them to re-register from scratch.
        import sys as _sys
        from pathlib import Path as _P
        _scripts = str((_P(__file__).resolve().parent.parent / "scripts").resolve())
        if _scripts not in _sys.path:
            _sys.path.insert(0, _scripts)
        import _paths as _p  # type: ignore
        if _p.detect_legacy_template_layout(template_path):
            raise LegacyTemplateLayoutError(
                f"Template {template_path.name} uses the pre-v0.4 flat sidecar "
                f"layout (sidecars live next to the .pptx instead of in a "
                f"subfolder). Run the one-shot migration:\n"
                f'  py -3 slide-builder/scripts/migrate_template_layout.py "{template_path.parent}"\n'
                f"This moves <stem>.brand.yml, <stem>.theme.json, <stem>.chrome.yml "
                f"and all other sidecars into <stem>/ next to the .pptx. "
                f"Existing builds will continue to work after the migration."
            )
        msg_lines = [
            f"Brand sidecar(s) missing for template: {template_path}",
        ]
        if not brand_yml.exists():
            msg_lines.append(f"  MISSING: {brand_yml}")
        if not theme_json.exists():
            msg_lines.append(f"  MISSING: {theme_json}")
        msg_lines.append("")
        msg_lines.append("Register the template first:")
        msg_lines.append(f'  py -3 scripts/register_template.py "{template_path}"')
        raise BrandSidecarMissing("\n".join(msg_lines))

    try:
        brand_raw = yaml.safe_load(brand_yml.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML in {brand_yml}: {e}") from e
    if not isinstance(brand_raw, dict):
        raise ValueError(f"Expected dict at top of {brand_yml}, got {type(brand_raw)}")

    try:
        theme = json.loads(theme_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in {theme_json}: {e}") from e

    expected_sha = theme.get("template_sha", "")
    actual_sha = _sha256_of_file(template_path)
    if not expected_sha or expected_sha != actual_sha:
        raise BrandSidecarStale(
            f"Template SHA mismatch — refusing to build.\n"
            f"  Template: {template_path}\n"
            f"  Expected SHA (from {theme_json.name}): {expected_sha or '(empty)'}\n"
            f"  Actual SHA:                              {actual_sha}\n"
            f"The template file has changed since registration.\n"
            f"Re-register to re-validate:\n"
            f'  py -3 scripts/register_template.py "{template_path}"'
        )

    return {
        "primary_hex": _normalize_hex(brand_raw.get("primary_hex", "")),
        "accent_hex": _normalize_hex(brand_raw.get("accent_hex", "")),
        "cover_bg_hex": _normalize_hex(
            brand_raw.get("cover_bg_hex", "") or brand_raw.get("primary_hex", "")
        ),
        # v0.3: dark_bg_hex defaults to primary_hex when brand.yml predates
        # the field (back-compat with templates registered before v0.3).
        "dark_bg_hex": _normalize_hex(
            brand_raw.get("dark_bg_hex", "") or brand_raw.get("primary_hex", "")
        ),
        "primary_slot": str(brand_raw.get("primary_slot", "") or ""),
        "accent_slot": str(brand_raw.get("accent_slot", "") or ""),
        "cover_bg_slot": str(brand_raw.get("cover_bg_slot", "") or ""),
        "dark_bg_slot": str(
            brand_raw.get("dark_bg_slot", "") or brand_raw.get("primary_slot", "") or ""
        ),
        "font_heading": str(brand_raw.get("font_heading", "") or ""),
        "font_body": str(brand_raw.get("font_body", "") or ""),
        # Default false — KEEP the master decoration. The master IS the
        # brand chrome for most templates (FedEx purple bars, Accenture
        # rules, OTC top/bottom bands). Stripping makes every slide look
        # off-spec. Set true ONLY for legacy templates with photographic
        # decoration that shouldn't bleed behind every slide.
        # (Matches register_template.py commit a8a79e2 and brand.yml docs.)
        "strip_master_backgrounds": bool(
            brand_raw.get("strip_master_backgrounds", False)
        ),
        # Gate A.3: resolved TTF path from brand.yml (empty when unresolved
        # at registration; finalize_deck falls back to disk scan).
        "title_font_ttf_path": str(
            brand_raw.get("title_font_ttf_path", "") or ""
        ),
        # Gate A.1: reference-slide spec (dict or None). Captured at
        # registration when the user designates a canonical slide in the
        # template ("make every output look like this slide").
        "reference_slide": (
            brand_raw.get("reference_slide")
            if isinstance(brand_raw.get("reference_slide"), dict)
            else None
        ),
        "_template_sha": actual_sha,
    }


# ---------------------------------------------------------------------------
# ClientTheme dataclass
# ---------------------------------------------------------------------------
@dataclass
class ClientTheme:
    """Theme attributes for a registered client template.

    Brand values (brand_primary, brand_accent, cover_bg_hex,
    strip_master_backgrounds) are read DIRECTLY from <template>.brand.yml —
    no heuristic picking, no slot-position inference.

    Raw theme1.xml palette attrs (dk1/lt1/dk2/lt2/accent1..6) are kept for
    text-color derivation (dk1 = body text) and for the off-palette alias
    map. They are NOT consulted for brand color decisions.
    """
    # ---- raw theme1.xml palette (text colors + off-palette mapping use these) ----
    dk1: str
    lt1: str
    dk2: str
    lt2: str
    accent1: str
    accent2: str
    accent3: str
    accent4: str
    accent5: str
    accent6: str
    major_font: str
    minor_font: str
    template_path: Optional[Path] = None

    # ---- brand.yml fields (ground truth) ----
    brand_primary: str = ""              # primary_hex
    brand_accent: str = ""               # accent_hex
    cover_bg_hex: str = ""               # cover_bg_hex
    dark_bg_hex: str = ""                # dark_bg_hex (v0.3: full-bleed dark variant fill)
    primary_slot: str = ""               # informational
    accent_slot: str = ""                # informational
    cover_bg_slot: str = ""              # informational
    dark_bg_slot: str = ""               # informational
    strip_master_backgrounds: bool = False
    template_sha: str = ""
    # Gate A.3: on-disk path to the heading font's TTF, resolved
    # at registration time. Empty string when the registering machine did not
    # have the font installed; finalize_deck falls back to a runtime disk scan.
    title_font_ttf_path: str = ""
    # Gate A.1: canonical reference-slide spec from brand.yml.
    # None when the user did not designate a reference slide at registration.
    # Schema: {slide_n, layout_name, title_box_px, subtitle_box_px,
    #          observed_colors}.
    reference_slide: Optional[dict] = None

    # Cached maps
    _color_map: Optional[Dict[str, str]] = field(default=None, repr=False)
    _theme_slot_map: Optional[Dict[str, str]] = field(default=None, repr=False)

    @property
    def brand_primary_source(self) -> str:
        """Slot name from brand.yml (e.g. 'dk2', 'lt2', 'accent1'). Informational."""
        return self.primary_slot or "brand.yml"

    @property
    def brand_accent_source(self) -> str:
        """Slot name from brand.yml. Informational."""
        return self.accent_slot or "brand.yml"

    def color_map(self) -> Dict[str, str]:
        """Map every Slide Lab literal brand color -> the client's equivalent.

        Uses brand.yml ground-truth for primary and accent. Derives midtones,
        soft variants, and card neutrals mechanically (mix toward lt1). No
        heuristic slot-selection.

        Returned dict has UPPERCASE hex keys and values (no leading #).

        Collision: SLIDE_LAB_BRAND_ACCENT_SOFT and SLIDE_LAB_CARD_BORDER_1 are
        both literal C2A3FF. Python dict literals let the LAST write win, so
        C2A3FF maps to card_border (subtle neutral). Exemplars using C2A3FF
        as a soft accent will read as a subtle neutral after theming — known
        regression carried from the heuristic era; not introduced here.
        """
        if self._color_map is not None:
            return self._color_map

        primary = self.brand_primary or self.dk2
        accent = self.brand_accent or self.lt2

        # Mechanical derivations — mix toward lt1 (typically #FFFFFF)
        primary_mid = _mix_hex(primary, self.lt1 or "FFFFFF", 0.30)
        accent_soft = _mix_hex(accent, self.lt1 or "FFFFFF", 0.60)

        # Neutrals derived from dk1+lt1 — independent of brand colors so they
        # stay readable regardless of how the client structured their accents.
        # (ACN accent6 is #05F2DB teal; using accents for card_bg was a bug.)
        text_mid = _mix_hex(self.dk1, self.lt1, 0.45)        # ~55% dark
        text_faint = _mix_hex(self.dk1, self.lt1, 0.65)      # ~35% dark
        border_neutral = _mix_hex(self.dk1, self.lt1, 0.88)  # very light grey
        card_bg = _mix_hex(self.dk1, self.lt1, 0.95)         # very pale near-white
        card_border = _mix_hex(self.dk1, self.lt1, 0.85)     # subtle grey

        # Insert order matters for the C2A3FF collision — see docstring.
        self._color_map = {
            SLIDE_LAB_BRAND_PRIMARY:      primary,
            SLIDE_LAB_BRAND_PRIMARY_MID:  primary_mid,
            SLIDE_LAB_BRAND_ACCENT:       accent,
            SLIDE_LAB_BRAND_ACCENT_SOFT:  accent_soft,   # written first
            SLIDE_LAB_CARD_BG_1:          card_bg,
            SLIDE_LAB_CARD_BG_2:          card_bg,
            SLIDE_LAB_CARD_BORDER_1:      card_border,   # overwrites C2A3FF -> card_border
            SLIDE_LAB_CARD_BORDER_2:      card_border,
            SLIDE_LAB_TEXT_DARK:          self.dk1,
            SLIDE_LAB_TEXT_MID:           text_mid,
            SLIDE_LAB_TEXT_FAINT:         text_faint,
        }
        # Off-palette aliases (agents that went rogue still get remapped)
        for hex_in in OFF_PALETTE_TEXT_DARK_ALIASES:
            self._color_map[hex_in] = self.dk1
        for hex_in in OFF_PALETTE_TEXT_MID_ALIASES:
            self._color_map[hex_in] = text_mid
        for hex_in in OFF_PALETTE_TEXT_FAINT_ALIASES:
            self._color_map[hex_in] = text_faint
        for hex_in in OFF_PALETTE_BORDER_ALIASES:
            self._color_map[hex_in] = border_neutral
        return self._color_map

    def theme_slot_map(self) -> Dict[str, str]:
        """Reverse map: theme-slot hex value -> schemeClr slot name.

        Used by ``apply_theme_to_shape_xml`` to rewrite literal srgbClr
        references emitted by the translator/worker into schemeClr
        references that bind to the template's color scheme. Recipient can
        then re-theme the deck by editing the template master.

        Built from the canonical theme part (the one referenced by
        slideMaster1; resolved by ``_canonical_theme_part_name`` rather
        than zip-iteration luck) — so the values reflect the brand truth,
        not a dead orphan theme.

        Slot names use modern OOXML vocabulary (tx1/tx2/bg1/bg2/accent1-6).
        First slot in iteration order wins on collision.
        """
        if self._theme_slot_map is not None:
            return self._theme_slot_map
        mapping: Dict[str, str] = {}
        for hex_val, slot in (
            (self.dk1, "tx1"),
            (self.lt1, "bg1"),
            (self.dk2, "tx2"),
            (self.lt2, "bg2"),
            (self.accent1, "accent1"),
            (self.accent2, "accent2"),
            (self.accent3, "accent3"),
            (self.accent4, "accent4"),
            (self.accent5, "accent5"),
            (self.accent6, "accent6"),
        ):
            if hex_val:
                up = hex_val.upper().lstrip("#")
                if up not in mapping:
                    mapping[up] = slot
        self._theme_slot_map = mapping
        return mapping


# ---------------------------------------------------------------------------
# Theme loader — extracts canonical theme + reads brand.yml sidecar
# ---------------------------------------------------------------------------
def _canonical_theme_part_name(template_path: Path) -> Optional[str]:
    """Return the zip part name of the theme referenced by the primary slide
    master, or None if the relationship graph can't be resolved.

    Walks: ``ppt/_rels/presentation.xml.rels`` -> first slideMaster's
    ``_rels`` -> theme Target. The returned name is the canonical theme for
    brand-color extraction.

    Without this, callers that iterate the zip's parts get a non-deterministic
    "first hit" (depends on storage order in the zip). The OTC template was
    authored with an orphan ``theme4.xml`` carrying Microsoft Office defaults
    (accent1=156082); zip-order luck made the loader pick that part instead
    of the FedEx-correct ``theme1.xml``. This function fixes that by reading
    the OOXML relationship graph the way PowerPoint itself does.
    """
    import zipfile
    import posixpath
    try:
        with zipfile.ZipFile(str(template_path)) as zf:
            try:
                pres_rels = zf.read(
                    "ppt/_rels/presentation.xml.rels"
                ).decode("utf-8", errors="replace")
            except KeyError:
                return None
            m = re.search(
                r'Target="([^"]*slideMaster\d+\.xml)"', pres_rels
            )
            if not m:
                return None
            # presentation.xml.rels Targets are relative to ppt/
            master_part = posixpath.normpath(
                posixpath.join("ppt", m.group(1))
            )
            master_rels = posixpath.join(
                posixpath.dirname(master_part), "_rels",
                posixpath.basename(master_part) + ".rels",
            )
            try:
                rels_data = zf.read(master_rels).decode(
                    "utf-8", errors="replace"
                )
            except KeyError:
                return None
            tm = re.search(
                r'Target="([^"]*theme/theme\d+\.xml)"', rels_data
            )
            if not tm:
                return None
            theme_part = posixpath.normpath(
                posixpath.join(posixpath.dirname(master_part), tm.group(1))
            )
            try:
                zf.getinfo(theme_part)
            except KeyError:
                return None
            return theme_part
    except (zipfile.BadZipFile, OSError):
        return None


def _extract_raw_theme(template_path: Path) -> dict:
    """Parse the canonical theme part from a .pptx/.potx. Returns a dict with
    dk1..accent6 plus major_font/minor_font. All hex values are 6-char
    uppercase (no '#').

    Canonical = the theme referenced by slideMaster1 (see
    ``_canonical_theme_part_name``). Falls back to first-hit-in-iter-parts
    only when the rels graph is unreadable (corrupt zip, unusual structure).
    """
    canonical = _canonical_theme_part_name(template_path)
    prs = Presentation(str(template_path))

    theme_xml = None
    if canonical:
        target = canonical.lower().lstrip("/")
        for part in prs.part.package.iter_parts():
            if part.partname.lower().lstrip("/") == target:
                theme_xml = part.blob.decode("utf-8", errors="replace")
                break
    if not theme_xml:
        # Fallback: any theme part (legacy non-deterministic behavior).
        for part in prs.part.package.iter_parts():
            if "/theme/theme" in part.partname.lower():
                theme_xml = part.blob.decode("utf-8", errors="replace")
                break
    if not theme_xml:
        raise ValueError(f"No theme XML found in {template_path}")

    def extract_color(name: str) -> str:
        m = re.search(rf"<a:{name}>(.*?)</a:{name}>", theme_xml, re.DOTALL)
        if not m:
            return "000000"
        inner = m.group(1)
        srgb = re.search(r'srgbClr\s+val="([0-9A-Fa-f]{6})"', inner)
        sysc = re.search(r'sysClr[^/>]*lastClr="([0-9A-Fa-f]{6})"', inner)
        if srgb:
            return srgb.group(1).upper()
        if sysc:
            return sysc.group(1).upper()
        return "000000"

    _FONT_STYLE_SUFFIXES = (
        " Regular", " Bold", " Italic", " Bold Italic", " Light", " Medium",
        " SemiBold", " ExtraBold", " Black", " Thin", " ExtraLight", " Heavy",
        " Oblique", " Light Italic", " Medium Italic", " SemiBold Italic",
        " ExtraBold Italic", " Black Italic",
    )

    def _strip_font_style(name: str) -> str:
        n = name.strip()
        for suffix in _FONT_STYLE_SUFFIXES:
            if n.endswith(suffix):
                return n[:-len(suffix)].strip()
        return n

    def extract_font(kind: str) -> str:
        m = re.search(rf"<a:{kind}>(.*?)</a:{kind}>", theme_xml, re.DOTALL)
        if not m:
            return ""
        latin = re.search(r'<a:latin\s+typeface="([^"]+)"', m.group(1))
        return _strip_font_style(latin.group(1)) if latin else ""

    return {
        "dk1": extract_color("dk1"),
        "lt1": extract_color("lt1"),
        "dk2": extract_color("dk2"),
        "lt2": extract_color("lt2"),
        "accent1": extract_color("accent1"),
        "accent2": extract_color("accent2"),
        "accent3": extract_color("accent3"),
        "accent4": extract_color("accent4"),
        "accent5": extract_color("accent5"),
        "accent6": extract_color("accent6"),
        "major_font": extract_font("majorFont"),
        "minor_font": extract_font("minorFont"),
    }


def load_client_theme(template_path: str) -> ClientTheme:
    """Open a registered client template and return its ClientTheme.

    Reads brand.yml + theme.json sidecars NEXT TO the template (same dir,
    same stem). brand.yml provides ground-truth primary/accent/cover_bg
    hexes + fonts + strip_master_backgrounds. theme.json provides SHA-256
    audit so we can refuse to build against a template that has changed
    since registration.

    Raises:
      FileNotFoundError       — template doesn't exist
      BrandSidecarMissing     — brand.yml or theme.json missing
      BrandSidecarStale       — template SHA differs from theme.json's record
      ValueError              — sidecar files malformed or no theme XML
    """
    tpl = Path(template_path)
    if not tpl.exists():
        raise FileNotFoundError(f"Client template not found: {tpl}")

    # 1. Read + validate brand.yml + theme.json (raises if missing/stale)
    brand = load_brand_sidecar(tpl)

    # 2. Extract raw theme1.xml palette (text colors + off-palette aliases)
    raw = _extract_raw_theme(tpl)

    # 3. Build ClientTheme with brand.yml fields as ground truth
    # Fonts: brand.yml overrides raw if set; raw is fallback.
    major_font = brand["font_heading"] or raw["major_font"]
    minor_font = brand["font_body"] or raw["minor_font"]

    return ClientTheme(
        dk1=raw["dk1"],
        lt1=raw["lt1"],
        dk2=raw["dk2"],
        lt2=raw["lt2"],
        accent1=raw["accent1"],
        accent2=raw["accent2"],
        accent3=raw["accent3"],
        accent4=raw["accent4"],
        accent5=raw["accent5"],
        accent6=raw["accent6"],
        major_font=major_font,
        minor_font=minor_font,
        template_path=tpl,
        brand_primary=brand["primary_hex"],
        brand_accent=brand["accent_hex"],
        cover_bg_hex=brand["cover_bg_hex"],
        dark_bg_hex=brand["dark_bg_hex"],
        primary_slot=brand["primary_slot"],
        accent_slot=brand["accent_slot"],
        cover_bg_slot=brand["cover_bg_slot"],
        dark_bg_slot=brand["dark_bg_slot"],
        strip_master_backgrounds=brand["strip_master_backgrounds"],
        template_sha=brand["_template_sha"],
        title_font_ttf_path=brand.get("title_font_ttf_path", "") or "",
        reference_slide=brand.get("reference_slide"),
    )


# ---------------------------------------------------------------------------
# Master/layout background stripping (called by finalize_deck.py at graft time
# when brand.yml says strip_master_backgrounds: true)
# ---------------------------------------------------------------------------
_PML_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
_DML_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def strip_master_layout_backgrounds(prs) -> int:
    """Remove baked-in background decoration from every slide master + layout
    in `prs`. Returns the count of elements removed.

    Strips three element kinds:
      - <p:bg>     — slide/layout/master background fills (solid or image)
      - <p:pic>    — picture shapes at master/layout level (logos, photos)
      - <p:sp>     — shapes with a blipFill (image fill on a regular shape)

    Placeholders (title, body, footer) are kept — only visual chrome goes.
    Used when brand.yml has `strip_master_backgrounds: true` (default for
    new registrations; especially load-bearing for NFL whose masters bake
    full-bleed stadium photos into 8 of 12 layouts).
    """
    from lxml import etree
    ns = {"p": _PML_NS, "a": _DML_NS}

    targets = []
    for master in prs.slide_masters:
        targets.append(master.element)
        for layout in master.slide_layouts:
            targets.append(layout.element)

    removed = 0
    for el in targets:
        # 1. <p:bg> direct children of cSld
        for bg in el.findall(f".//{{{_PML_NS}}}bg"):
            parent = bg.getparent()
            if parent is not None:
                parent.remove(bg)
                removed += 1
        # 2. <p:pic> picture shapes
        for pic in el.findall(f".//{{{_PML_NS}}}pic"):
            parent = pic.getparent()
            if parent is not None:
                parent.remove(pic)
                removed += 1
        # 3. <p:sp> shapes whose fill is a blipFill (image)
        for sp in list(el.findall(f".//{{{_PML_NS}}}sp")):
            blipfill = sp.find(f".//{{{_DML_NS}}}blipFill")
            if blipfill is not None:
                parent = sp.getparent()
                if parent is not None:
                    parent.remove(sp)
                    removed += 1
    return removed


# ---------------------------------------------------------------------------
# Apply theme to a cloned shape (XML rewrite) — unchanged from prior version
# ---------------------------------------------------------------------------
_SRGB_RE = re.compile(rb'(srgbClr\s+val=")([0-9A-Fa-f]{6})(")')
_LATIN_RE = re.compile(rb'(latin\s+typeface=")([^"]+)(")')
# Self-closing srgbClr (no child color modifications). Only this form is
# eligible for srgbClr -> schemeClr swap; srgbClr with children (alpha,
# lumMod, etc.) is left to the hex-substitution path so children survive.
_SRGB_SELFCLOSE_RE = re.compile(
    rb'<a:srgbClr\s+val="([0-9A-Fa-f]{6})"\s*/>'
)


def apply_theme_to_shape_xml(element, color_map: Dict[str, str],
                             major_font: str = "", minor_font: str = "",
                             theme_slot_map: Optional[Dict[str, str]] = None) -> int:
    """Walk a shape's XML (in-place), rewriting srgbClr / latin typeface
    references to be theme-aware. Returns the number of substitutions made.

    Three ordered passes:

    1. **srgbClr hex rewrite** (color_map): srgb hex values matching a
       Slide-Lab-canonical literal are remapped to the client's equivalent
       hex. Preserves the srgbClr tag and any children. Runs first so
       Pass 2 sees client hexes (worker/translator may emit either
       canonical or client hexes — this normalizes).
    2. **srgbClr -> schemeClr** (when theme_slot_map is provided): self-
       closing srgbClr elements whose hex (now the client hex post-Pass 1)
       matches a theme slot become ``<a:schemeClr val="accent1"/>`` (or
       the appropriate slot). Self-closing form only — srgbClr with child
       modifications (alpha, lumMod, etc.) was preserved through Pass 1
       and stays as srgbClr here. Once brand fills become schemeClr refs,
       the recipient can re-theme the deck by editing the template master.
    3. **latin typeface -> theme font reference**: literal font names that
       match the minor_font become ``+mn-lt``; matches against major_font
       become ``+mj-lt``. Icon glyph fonts (Wingdings, Segoe UI Symbol,
       etc.) pass through. Any other non-icon font falls back to the
       minor_font literal — so the recipient sees the template's body font
       rather than whatever the worker typed.
    """
    from lxml import etree
    xml = etree.tostring(element)

    n_subs = 0

    def _replace_color(m):
        nonlocal n_subs
        hex_in = m.group(2).decode("ascii").upper()
        if hex_in in color_map:
            n_subs += 1
            return m.group(1) + color_map[hex_in].encode("ascii") + m.group(3)
        return m.group(0)

    xml = _SRGB_RE.sub(_replace_color, xml)

    if theme_slot_map:
        def _replace_to_scheme(m):
            nonlocal n_subs
            hex_in = m.group(1).decode("ascii").upper()
            slot = theme_slot_map.get(hex_in)
            if slot:
                n_subs += 1
                return b'<a:schemeClr val="' + slot.encode("ascii") + b'"/>'
            return m.group(0)
        xml = _SRGB_SELFCLOSE_RE.sub(_replace_to_scheme, xml)

    _ICON_FONTS = {
        "segoe ui symbol", "segoe ui emoji", "wingdings", "wingdings 2",
        "wingdings 3", "symbol", "symbola", "noto color emoji",
        "apple color emoji", "marlett", "webdings",
    }
    minor_norm = (minor_font or "").strip().lower()
    major_norm = (major_font or "").strip().lower()
    if minor_norm or major_norm:
        def _replace_font(m):
            nonlocal n_subs
            cur = m.group(2).decode("utf-8").strip()
            cur_lower = cur.lower()
            if cur_lower in _ICON_FONTS:
                return m.group(0)
            if cur.startswith("+"):
                return m.group(0)
            if major_norm and cur_lower == major_norm:
                replacement = b"+mj-lt"
            elif minor_norm:
                # Match against minor OR fall back to minor for any
                # unrecognized font — recipient sees the template's body
                # font (theme-bound) rather than a worker-chosen literal.
                replacement = b"+mn-lt"
            else:
                return m.group(0)
            n_subs += 1
            return m.group(1) + replacement + m.group(3)
        xml = _LATIN_RE.sub(_replace_font, xml)

    new_el = etree.fromstring(xml)
    parent = element.getparent()
    if parent is not None:
        parent.replace(element, new_el)
    return n_subs


def apply_theme_to_slide(slide, theme: ClientTheme) -> int:
    """Apply the theme to every shape on a slide. Returns substitution count."""
    color_map = theme.color_map()
    slot_map = theme.theme_slot_map()
    total = 0
    for shape in list(slide.shapes):
        total += apply_theme_to_shape_xml(
            shape.element, color_map,
            major_font=theme.major_font, minor_font=theme.minor_font,
            theme_slot_map=slot_map,
        )
    return total


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m twins.client_theme <template.pptx>")
        sys.exit(1)
    try:
        t = load_client_theme(sys.argv[1])
    except BrandSidecarMissing as e:
        print(f"REFUSED: {e}")
        sys.exit(2)
    except BrandSidecarStale as e:
        print(f"REFUSED: {e}")
        sys.exit(2)
    print(f"Theme (raw from theme1.xml):")
    print(f"  dk1={t.dk1}  lt1={t.lt1}  dk2={t.dk2}  lt2={t.lt2}")
    print(f"  accents: {t.accent1} {t.accent2} {t.accent3} {t.accent4} {t.accent5} {t.accent6}")
    print(f"  fonts: heading={t.major_font!r}  body={t.minor_font!r}")
    print(f"Brand (from brand.yml):")
    print(f"  primary=#{t.brand_primary}  (slot: {t.primary_slot})")
    print(f"  accent =#{t.brand_accent}   (slot: {t.accent_slot})")
    print(f"  cover  =#{t.cover_bg_hex}   (slot: {t.cover_bg_slot})")
    print(f"  strip_master_backgrounds: {t.strip_master_backgrounds}")
    print(f"  template_sha[:8]: {t.template_sha[:8]}")
    print(f"\nColor map (Slide Lab default -> client):")
    for k, v in t.color_map().items():
        print(f"  #{k} -> #{v}")
