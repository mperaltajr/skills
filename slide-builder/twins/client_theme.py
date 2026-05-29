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
    """Blend two RGB hex strings. ratio=0 -> hex_a, ratio=1 -> hex_b."""
    a = [int(hex_a[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{int(a[i] + (b[i] - a[i]) * ratio):02X}" for i in range(3))


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
    """Return (brand_yml_path, theme_json_path) for a given template."""
    stem = template_path.stem  # filename without final extension
    return (
        template_path.with_name(f"{stem}.brand.yml"),
        template_path.with_name(f"{stem}.theme.json"),
    )


class BrandSidecarMissing(FileNotFoundError):
    """Raised when brand.yml or theme.json is missing next to a template."""
    pass


class BrandSidecarStale(ValueError):
    """Raised when theme.json's template_sha doesn't match the template file."""
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
        "strip_master_backgrounds": bool(
            brand_raw.get("strip_master_backgrounds", True)
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
    strip_master_backgrounds: bool = True
    template_sha: str = ""

    # Cached map
    _color_map: Optional[Dict[str, str]] = field(default=None, repr=False)

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


# ---------------------------------------------------------------------------
# Theme loader — extracts raw theme1.xml + reads brand.yml sidecar
# ---------------------------------------------------------------------------
def _extract_raw_theme(template_path: Path) -> dict:
    """Parse theme1.xml from a .pptx/.potx. Returns a dict with dk1..accent6
    plus major_font/minor_font. All hex values are 6-char uppercase (no '#').
    """
    prs = Presentation(str(template_path))

    theme_xml = None
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


def apply_theme_to_shape_xml(element, color_map: Dict[str, str],
                             major_font: str = "", minor_font: str = "") -> int:
    """Walk a shape's XML (in-place), rewriting srgbClr and latin typeface
    attributes per the provided maps. Returns the number of substitutions made.

    Color matching is case-insensitive on the hex value but writes upper-case
    output. Both color_map keys and values should be uppercase hex (no #).

    Font remap: any latin typeface gets rewritten to `minor_font`. Icon-glyph
    fonts (Wingdings, Segoe UI Symbol, etc.) pass through unchanged because
    their characters don't exist in body fonts.
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

    target_font = (minor_font or "").encode("utf-8")
    _ICON_FONTS = {
        "segoe ui symbol", "segoe ui emoji", "wingdings", "wingdings 2",
        "wingdings 3", "symbol", "symbola", "noto color emoji",
        "apple color emoji", "marlett", "webdings",
    }
    if target_font:
        def _replace_font(m):
            nonlocal n_subs
            cur = m.group(2).decode("utf-8")
            if cur.strip().lower() in _ICON_FONTS:
                return m.group(0)
            n_subs += 1
            return m.group(1) + target_font + m.group(3)
        xml = _LATIN_RE.sub(_replace_font, xml)

    new_el = etree.fromstring(xml)
    parent = element.getparent()
    if parent is not None:
        parent.replace(element, new_el)
    return n_subs


def apply_theme_to_slide(slide, theme: ClientTheme) -> int:
    """Apply the theme to every shape on a slide. Returns substitution count."""
    color_map = theme.color_map()
    total = 0
    for shape in list(slide.shapes):
        total += apply_theme_to_shape_xml(
            shape.element, color_map,
            major_font=theme.major_font, minor_font=theme.minor_font,
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
