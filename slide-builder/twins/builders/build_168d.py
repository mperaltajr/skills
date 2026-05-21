"""
Builder for pattern 168d: Awards & Accolades — hero award + 4 secondary tiles — dark.

Source HTML: _pattern-library/168_awards-accolades-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title", "Industry <strong>Recognition</strong> &amp; Awards",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "A track record of excellence, independently validated by leading industry bodies",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Hero award
    hero_y = 230
    add_icon(slide, "hero-award-icon", x_px=(1280 - 96) // 2, y_px=hero_y, size_px=88,
             glyph="★", color=BRAND_ACCENT)
    add_text(slide, "hero-award-name", "Global Technology Services Partner of the Year",
             x_px=(1280 - 900) // 2, y_px=hero_y + 100, w_px=900, h_px=56,
             font_size_px=30, color=WHITE, bold=True, align="center")
    add_text(slide, "hero-award-body", "Forrester Wave — Enterprise Technology & Consulting",
             x_px=(1280 - 700) // 2, y_px=hero_y + 160, w_px=700, h_px=20,
             font_size_px=15, color=TEXT_ON_DARK_MID, align="center")
    add_text(slide, "hero-award-year", "2026",
             x_px=(1280 - 200) // 2, y_px=hero_y + 184, w_px=200, h_px=16,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True)

    # Section divider
    div_y = hero_y + 216
    add_rect(slide, "section-divider-rule-left", 200, div_y + 7, 350, 1, BRAND_ACCENT_SOFT)
    add_rect(slide, "section-divider-rule-right", 1280 - 200 - 350, div_y + 7, 350, 1, BRAND_ACCENT_SOFT)
    add_text(slide, "section-divider-label", "Also recognized",
             x_px=(1280 - 200) // 2, y_px=div_y, w_px=200, h_px=18,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, align="center", uppercase=True)

    # Secondary tiles
    sec_data = [
        ("Leader in Digital Transformation", "Gartner MQ · 2025"),
        ("Best Managed Services Provider", "IDC MarketScape · 2025"),
        ("Top AI & Data Consultancy", "HFS Research · 2024"),
        ("Excellence in Sustainability", "World Economic Forum · 2024"),
    ]
    tile_y = div_y + 32
    tile_w = 200
    total_w = tile_w * 4
    start_x = (1280 - total_w) // 2
    for i, (name, year) in enumerate(sec_data):
        n = i + 1
        x = start_x + i * tile_w
        add_icon(slide, f"award-{n}-icon", x_px=x + (tile_w - 32) // 2, y_px=tile_y, size_px=32,
                 glyph="★", color=BRAND_ACCENT)
        add_text(slide, f"award-{n}-name", name,
                 x_px=x + 12, y_px=tile_y + 38, w_px=tile_w - 24, h_px=32,
                 font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, align="center")
        add_text(slide, f"award-{n}-year", year,
                 x_px=x + 12, y_px=tile_y + 72, w_px=tile_w - 24, h_px=14,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, align="center")
        if i > 0:
            add_rect(slide, f"award-{n}-divider", x, tile_y + 16, 1, 70, CARD_BORDER_DARK)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "168",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "168d_awards-accolades.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
