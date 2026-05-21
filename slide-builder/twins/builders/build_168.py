"""
Builder for pattern 168: Awards & Accolades — hero award + 4 secondary tiles.

Source HTML: _pattern-library/168_awards-accolades.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Industry <strong>Recognition</strong> &amp; Awards",
        subtitle="A track record of excellence, independently validated by leading industry bodies",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Hero award (centered) — enlarged to fill whitespace
    hero_y = 188
    add_icon(slide, "hero-award-icon", x_px=(1280 - 96) // 2, y_px=hero_y, size_px=96,
             glyph="★", color=BRAND_ACCENT)
    add_text(slide, "hero-award-name", "Global Technology Services Partner of the Year",
             x_px=(1280 - 900) // 2, y_px=hero_y + 108, w_px=900, h_px=64,
             font_size_px=32, color=BRAND_PRIMARY, bold=True, align="center")
    add_text(slide, "hero-award-body", "Forrester Wave — Enterprise Technology & Consulting",
             x_px=(1280 - 700) // 2, y_px=hero_y + 178, w_px=700, h_px=22,
             font_size_px=16, color=TEXT_MID, align="center")
    add_text(slide, "hero-award-year", "2026",
             x_px=(1280 - 200) // 2, y_px=hero_y + 206, w_px=200, h_px=16,
             font_size_px=12, color=TEXT_FAINT, bold=True, align="center", uppercase=True)

    # Section divider
    div_y = hero_y + 244
    add_rect(slide, "section-divider-rule-left", 200, div_y + 7, 350, 1, BRAND_ACCENT_SOFT)
    add_rect(slide, "section-divider-rule-right", 1280 - 200 - 350, div_y + 7, 350, 1, BRAND_ACCENT_SOFT)
    add_text(slide, "section-divider-label", "Also recognized",
             x_px=(1280 - 200) // 2, y_px=div_y, w_px=200, h_px=18,
             font_size_px=9, color=TEXT_FAINT, bold=True, align="center", uppercase=True)

    # Secondary tiles (4)
    sec_data = [
        ("Leader in Digital Transformation", "Gartner MQ · 2025"),
        ("Best Managed Services Provider", "IDC MarketScape · 2025"),
        ("Top AI & Data Consultancy", "HFS Research · 2024"),
        ("Excellence in Sustainability", "World Economic Forum · 2024"),
    ]
    tile_y = div_y + 36
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
                 font_size_px=12, color=BRAND_PRIMARY, bold=True, align="center")
        add_text(slide, f"award-{n}-year", year,
                 x_px=x + 12, y_px=tile_y + 72, w_px=tile_w - 24, h_px=14,
                 font_size_px=10, color=TEXT_FAINT, align="center")
        if i > 0:
            add_rect(slide, f"award-{n}-divider", x, tile_y + 16, 1, 70, CARD_BORDER)

    # Convergence bar above footer
    conv_y = 720 - 56 - 36
    add_rect(slide, "convergence-bg", 0, conv_y, 1280, 36, BRAND_PRIMARY)
    add_text(slide, "convergence",
             "Recognized across 5 industry awards & analyst rankings in the past 24 months",
             x_px=0, y_px=conv_y, w_px=1280, h_px=36,
             font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle", uppercase=True)

    add_footer(slide, page_num=168)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "168_awards-accolades.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
