"""
Client theme extraction + application.

When a client PPTX template is set in a deck spec, this module extracts the
client's actual brand attributes (theme colors, theme fonts) and provides a
mapping from the Slide Lab default palette (Accenture purple/violet, Inter
font) to the client's equivalents.

The composer walks each cloned twin shape's XML and rewrites srgbClr fills,
text-run colors, and latin typeface attributes using these maps. End result:
the same twin layout renders in the client's brand without any builder code
needing to know about the client.

Usage (composer-internal):

    theme = load_client_theme("path/to/FedEx Template.pptx")
    color_map = theme.color_map()
    apply_theme_to_shape_xml(shape.element, color_map, theme.major_font, theme.minor_font)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from pptx import Presentation


# ---------------------------------------------------------------------------
# Slide Lab default palette (from helpers.py — must stay in sync)
# ---------------------------------------------------------------------------

# These are the literal RGB hex strings (no leading #) that every twin builder
# bakes into its shapes. The color_map() function maps each of these to the
# closest equivalent in the client's theme.
SLIDE_LAB_BRAND_PRIMARY = "2D0A4E"      # accenture violet
SLIDE_LAB_BRAND_PRIMARY_MID = "5C2D87"  # midtone violet
SLIDE_LAB_BRAND_ACCENT = "A100FF"       # bright violet accent
SLIDE_LAB_BRAND_ACCENT_SOFT = "C780FF"  # soft violet accent
SLIDE_LAB_TEXT_DARK = "1A1A2E"
SLIDE_LAB_TEXT_MID = "64748B"           # helpers.TEXT_MID (slate-500)
SLIDE_LAB_TEXT_FAINT = "94A3B8"         # helpers.TEXT_FAINT (slate-400)
SLIDE_LAB_CARD_BG_1 = "F8F4FC"
SLIDE_LAB_CARD_BG_2 = "FBF8FE"
SLIDE_LAB_CARD_BORDER_1 = "E5D5F0"
SLIDE_LAB_CARD_BORDER_2 = "ECE0F5"

# Off-palette colors agents have been observed using (despite not being in
# helpers.py). We map these too so existing decks survive the theme pass.
# Long-term fix is A+C (locked palette + schemeClr); this is the safety net.
OFF_PALETTE_TEXT_DARK_ALIASES = ("333333", "1E293B", "0F172A", "111827")
OFF_PALETTE_TEXT_MID_ALIASES = ("475569", "6B7280", "4B5563")
OFF_PALETTE_TEXT_FAINT_ALIASES = ("CBD5E1", "D1D5DB", "9CA3AF")
OFF_PALETTE_BORDER_ALIASES = ("E3E3E3", "E5E7EB", "E2E8F0", "D4D4D8")

SLIDE_LAB_DEFAULT_FONT = "Inter"

# ---------------------------------------------------------------------------
# Color math
# ---------------------------------------------------------------------------


def _mix_hex(hex_a: str, hex_b: str, ratio: float) -> str:
    """Blend two RGB hex strings. ratio=0 -> hex_a, ratio=1 -> hex_b."""
    a = [int(hex_a[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{int(a[i] + (b[i] - a[i]) * ratio):02X}" for i in range(3))


def _hex_to_hsl(hex_color: str) -> tuple:
    """Convert RRGGBB hex to (H, S, L) where H in [0,360), S/L in [0,1]."""
    r, g, b = [int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin
    L = (cmax + cmin) / 2
    if delta == 0:
        return (0.0, 0.0, L)
    denom = 1 - abs(2 * L - 1)
    S = delta / denom if denom > 0 else 0.0
    if cmax == r:
        H = ((g - b) / delta) % 6
    elif cmax == g:
        H = (b - r) / delta + 2
    else:
        H = (r - g) / delta + 4
    return (H * 60, S, L)


def _pick_brand_colors(palette: list) -> tuple:
    """Pick the best (primary, accent) from a list of (hex, name) candidates.

    Heuristic:
      - Drop neutral colors (saturation < 0.30) — they're grays / off-whites
      - Primary: most saturated DARK color (L < 0.5). Fall back to most saturated overall.
      - Accent: iterate the palette in SLOT ORDER (caller passes dk2, lt2,
        accent1..accent6 in that order) and pick the first saturated color that
        isn't the primary. Real branded palettes put their EDITORIAL accents in
        the early slots; the tertiary "tech / sub-brand" colors (like Accenture's
        bright teal at accent6) live at the end. The earlier max-hue-distance
        heuristic kept selecting those tertiary colors (teal on Accenture decks)
        even though no real Accenture editorial deck uses teal as the accent.

    Returns ("RRGGBB", "RRGGBB"). Caller passes in dk2/lt2 fallbacks as last resort.
    """
    scored = []
    for hex_val, name in palette:
        h, s, l = _hex_to_hsl(hex_val)
        if s >= 0.30:
            scored.append((hex_val, name, h, s, l))
    if not scored:
        return None, None  # caller falls back to dk2/lt2

    # Primary: prefer dark (L<0.5); else most saturated
    dark = [c for c in scored if c[4] < 0.5]
    primary_tuple = max(dark or scored, key=lambda c: c[3])
    primary = primary_tuple[0]

    # Accent: first saturated, non-primary color in SLOT ORDER (dk2, lt2,
    # accent1..accent6). On ACN Graphik this picks A100FF (Accenture bright
    # violet at dk2) over 05F2DB (sub-brand teal at accent6). On FedEx with
    # dk2 already taken as primary, this picks lt2=FF6600 (orange) — same
    # result as the old heuristic gave there.
    accent = None
    for c in scored:
        if c[0] != primary:
            accent = c[0]
            break
    return primary, accent


# ---------------------------------------------------------------------------
# ClientTheme dataclass
# ---------------------------------------------------------------------------


@dataclass
class ClientTheme:
    """Theme attributes extracted from a client template."""
    dk1: str         # dark text (typically #333 or #000)
    lt1: str         # light background (typically #FFF)
    dk2: str         # primary brand color
    lt2: str         # secondary brand / accent
    accent1: str
    accent2: str
    accent3: str
    accent4: str
    accent5: str
    accent6: str
    major_font: str  # heading font (typically used in titles)
    minor_font: str  # body font (typically used in body text)
    template_path: Optional[Path] = None

    # Cached map
    _color_map: Optional[Dict[str, str]] = field(default=None, repr=False)

    def picked_brand_colors(self) -> tuple:
        """Return (primary, accent) selected from the palette via saturation
        heuristic. Falls back to (dk2, lt2) if no saturated colors exist.
        See `_pick_brand_colors`.
        """
        primary, accent = _pick_brand_colors([
            (self.dk2, "dk2"),
            (self.lt2, "lt2"),
            (self.accent1, "accent1"),
            (self.accent2, "accent2"),
            (self.accent3, "accent3"),
            (self.accent4, "accent4"),
            (self.accent5, "accent5"),
            (self.accent6, "accent6"),
        ])
        return (primary or self.dk2, accent or self.lt2)

    def color_map(self) -> Dict[str, str]:
        """Map every Slide Lab literal brand color -> the client's equivalent.

        Uses a saturation-based heuristic (see picked_brand_colors) so clients
        that put their brand in accent1/accent2 instead of dk2/lt2 still get
        the right colors. Returned dict has UPPERCASE hex keys and values (no
        leading #).
        """
        if self._color_map is not None:
            return self._color_map
        primary, accent = self.picked_brand_colors()
        # Derive neutral greys from the client's dk1 (text) so body text inherits
        # the client's text tone rather than Tailwind slate.
        text_mid = _mix_hex(self.dk1, self.lt1, 0.45)    # ~55% dark
        text_faint = _mix_hex(self.dk1, self.lt1, 0.65)  # ~35% dark
        border_neutral = _mix_hex(self.dk1, self.lt1, 0.88)  # very light grey
        # Card backgrounds + borders are DERIVED neutrals, NOT accent5/accent6.
        # Earlier code mapped CARD_BG -> accent6 on the assumption that accent6
        # is always a near-white neutral. That holds for FedEx (#F2F2F2) but
        # NOT for clients whose accent6 is a vivid brand color (ACN Graphik:
        # #05F2DB teal). Result was teal card backgrounds bleeding everywhere.
        # Always derive cards from dk1+lt1 so they read as neutral chrome,
        # regardless of how the client structured their accent palette.
        card_bg     = _mix_hex(self.dk1, self.lt1, 0.95)  # very pale near-white
        card_border = _mix_hex(self.dk1, self.lt1, 0.85)  # subtle grey
        self._color_map = {
            # Primary brand swap
            SLIDE_LAB_BRAND_PRIMARY:      primary,
            SLIDE_LAB_BRAND_PRIMARY_MID:  _mix_hex(primary, self.lt1, 0.30),
            # Accent swap
            SLIDE_LAB_BRAND_ACCENT:       accent,
            SLIDE_LAB_BRAND_ACCENT_SOFT:  _mix_hex(accent, self.lt1, 0.55),
            # Card backgrounds -> derived neutral light (NEVER accent6 which
            # is brand-saturated in some client palettes)
            SLIDE_LAB_CARD_BG_1:          card_bg,
            SLIDE_LAB_CARD_BG_2:          card_bg,
            # Card borders -> derived neutral mid (NEVER accent5)
            SLIDE_LAB_CARD_BORDER_1:      card_border,
            SLIDE_LAB_CARD_BORDER_2:      card_border,
            # Text
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
# Theme loader
# ---------------------------------------------------------------------------


def load_client_theme(template_path: str) -> ClientTheme:
    """Open a .pptx/.potx and extract its theme1 attributes.

    Returns a ClientTheme. Raises FileNotFoundError if the template can't be
    opened or ValueError if no theme XML is found.
    """
    tpl = Path(template_path)
    if not tpl.exists():
        raise FileNotFoundError(f"Client template not found: {tpl}")
    prs = Presentation(str(tpl))

    theme_xml = None
    for part in prs.part.package.iter_parts():
        if "/theme/theme" in part.partname.lower():
            theme_xml = part.blob.decode("utf-8", errors="replace")
            break
    if not theme_xml:
        raise ValueError(f"No theme found in {tpl}")

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

    # Strip weight/style suffixes so the typeface is the font FAMILY (e.g.
    # "FedEx Sans Regular" -> "FedEx Sans"). Bold/italic are applied separately
    # via the rPr b="1" / i="1" attributes, so the typeface only needs to be
    # the family. LibreOffice (and most non-MS renderers) require the family
    # name; only Microsoft tooling tolerates "Family Weight" forms.
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

    return ClientTheme(
        dk1=extract_color("dk1"),
        lt1=extract_color("lt1"),
        dk2=extract_color("dk2"),
        lt2=extract_color("lt2"),
        accent1=extract_color("accent1"),
        accent2=extract_color("accent2"),
        accent3=extract_color("accent3"),
        accent4=extract_color("accent4"),
        accent5=extract_color("accent5"),
        accent6=extract_color("accent6"),
        major_font=extract_font("majorFont"),
        minor_font=extract_font("minorFont"),
        template_path=tpl,
    )


# ---------------------------------------------------------------------------
# Apply theme to a cloned shape (XML rewrite)
# ---------------------------------------------------------------------------

# Regex for matching srgbClr val="RRGGBB" — case-insensitive on the hex.
# Both fill colors and text-run colors use this. Rewriting all of them in
# one pass catches everything our builders emit.
_SRGB_RE = re.compile(rb'(srgbClr\s+val=")([0-9A-Fa-f]{6})(")')

# Regex for matching latin typeface="X" inside <a:rPr> or <a:defRPr>.
_LATIN_RE = re.compile(rb'(latin\s+typeface=")([^"]+)(")')


def apply_theme_to_shape_xml(element, color_map: Dict[str, str],
                             major_font: str = "", minor_font: str = "") -> int:
    """Walk a shape's XML (in-place), rewriting srgbClr and latin typeface
    attributes per the provided maps. Returns the number of substitutions made.

    Color matching is case-insensitive on the hex value but writes upper-case
    output. Both color_map keys and values should be uppercase hex (no #).

    For fonts: any latin typeface matching the Slide Lab default (Inter) is
    rewritten to `minor_font` by default. Title-style runs typically appear
    inside paragraphs that already have <a:rPr b="1"> — we don't bother
    distinguishing those here; using minor_font everywhere is safe because the
    template's theme already binds majorFont to title placeholders. For shapes
    Slide Lab adds on top (not in placeholders), using minor_font keeps text
    legible without dragging in a heavier weight.
    """
    # Serialize to bytes for regex (lxml doesn't expose a clean walk for what
    # we need; raw XML rewrite is faster and unambiguous here).
    from lxml import etree
    xml = etree.tostring(element)

    n_subs = 0
    # Color remap — regex captures bytes since XML is bytes; decode to compare
    # against the str-keyed color_map.
    def _replace_color(m):
        nonlocal n_subs
        hex_in = m.group(2).decode("ascii").upper()
        if hex_in in color_map:
            n_subs += 1
            return m.group(1) + color_map[hex_in].encode("ascii") + m.group(3)
        return m.group(0)

    xml = _SRGB_RE.sub(_replace_color, xml)

    # Font remap — swap EVERY text typeface to the client font so the deck
    # renders consistently. Icon glyph fonts (Segoe UI Symbol, Wingdings, etc.)
    # pass through unchanged because the icon characters don't exist in
    # FedEx Sans / Inter / typical body fonts.
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

    # Reparse and replace the element's contents in place
    new_el = etree.fromstring(xml)
    # Replace the element in its parent
    parent = element.getparent()
    if parent is not None:
        parent.replace(element, new_el)
    else:
        # No parent — caller is responsible for using the returned element.
        # In practice we always have a parent since the shape was added to a slide.
        pass
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
    t = load_client_theme(sys.argv[1])
    print(f"Theme: dk1={t.dk1}, lt1={t.lt1}, dk2={t.dk2}, lt2={t.lt2}")
    print(f"  accents: {t.accent1} {t.accent2} {t.accent3} {t.accent4} {t.accent5} {t.accent6}")
    print(f"Fonts: heading={t.major_font!r}, body={t.minor_font!r}")
    p, a = t.picked_brand_colors()
    print(f"Picked brand: primary=#{p}, accent=#{a}")
    print(f"\nColor map (Slide Lab default -> client):")
    for k, v in t.color_map().items():
        print(f"  #{k} -> #{v}")
