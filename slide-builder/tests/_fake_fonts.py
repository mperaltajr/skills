"""Made-up font files for the font tests (no real brand fonts in the repo).

make_font() writes a small TrueType file whose name table, weight, width and
letter widths are whatever the test says. Each letter is a filled box, so a
render shows where the text went.
"""
from __future__ import annotations

from pathlib import Path

_CHARS = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
          ".,;:!?'\"()-%$&/ ")


def make_font(path: Path, *, family: str, style: str = "Regular",
              typo_family: str | None = None, typo_style: str | None = None,
              weight: int = 400, width: int = 5, scale: float = 1.0) -> Path:
    """Write one face. scale multiplies every advance width (0.75 = narrow)."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    upm = 1000
    names = [".notdef"] + [f"g{ord(c):04X}" for c in _CHARS]
    cmap = {ord(c): f"g{ord(c):04X}" for c in _CHARS}
    glyphs, metrics = {}, {}
    for n in names:
        ch = chr(int(n[1:], 16)) if n != ".notdef" else "?"
        base = 280 if ch == " " else (620 if ch.isupper() else 520)
        if ch in "il.,;:!'|":
            base = 260
        adv = int(round(base * scale * (1.12 if weight >= 600 else 1.0)))
        pen = TTGlyphPen(None)
        if ch != " ":
            pen.moveTo((40, 0)); pen.lineTo((40, 700)); pen.lineTo((max(60, adv - 40), 700))
            pen.lineTo((max(60, adv - 40), 0)); pen.closePath()
        glyphs[n] = pen.glyph()
        metrics[n] = (adv, 40)
    fb = FontBuilder(upm, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-200)
    nm = {"familyName": family, "styleName": style,
          "uniqueFontIdentifier": f"{family}-{style}-{weight}-{width}",
          "fullName": f"{family} {style}", "psName": f"{family}-{style}".replace(" ", "")}
    if typo_family:
        nm["typographicFamily"] = typo_family
    if typo_style:
        nm["typographicSubfamily"] = typo_style
    fb.setupNameTable(nm)
    sel = 0x40 if style.lower() == "regular" else 0
    if "bold" in style.lower():
        sel |= 0x20
    fb.setupOS2(usWeightClass=weight, usWidthClass=width, fsSelection=sel,
                sTypoAscender=900, sTypoDescender=-200, usWinAscent=900, usWinDescent=200)
    fb.setupPost()
    fb.setupHead(unitsPerEm=upm, macStyle=1 if sel & 0x20 else 0)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(path))
    return path
