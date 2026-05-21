"""
Builder for pattern 76d: Logo wall — dark variant.

Source HTML: _pattern-library/76_logo-wall-dark.html
Light template: twins/builders/build_76.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
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

    add_text(slide, "title",
             "Where Slide Lab has worked — twelve practices, eight industries.",
             x_px=48, y_px=20, w_px=1180, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Engagements span Fortune 500 and category leaders across four continents. Logos shown as placeholders pending client approval — full reference list available on request.",
             x_px=48, y_px=108, w_px=1060, h_px=40,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 152, 56, 3, BRAND_ACCENT_SOFT)

    # 4x3 grid of logo tiles
    grid_left = 48
    grid_top = 220
    grid_w = 1280 - 96
    grid_h = 380
    cols, rows = 4, 3
    gap = 14
    tile_w = (grid_w - gap * (cols - 1)) // cols
    tile_h = (grid_h - gap * (rows - 1)) // rows

    logos = [
        "ACME CORP", "GLOBEX", "INITECH", "UMBRELLA",
        "WEYLAND", "TYRELL", "STARK", "WAYNE",
        "SOYLENT", "CYBERDYNE", "MASSIVE", "OMNI",
    ]
    featured = {2, 7}

    for i, label in enumerate(logos):
        n = i + 1
        row = i // cols
        col = i % cols
        tx = grid_left + col * (tile_w + gap)
        ty = grid_top + row * (tile_h + gap)

        is_featured = n in featured
        fill = BRAND_PRIMARY_MID if is_featured else CARD_BG_DARK
        tile = add_rect(slide, f"logo-{n}-tile", tx, ty, tile_w, tile_h, fill)
        if is_featured:
            tile.line.color.rgb = BRAND_ACCENT_SOFT
            tile.line.width = 19050
            text_color = WHITE
        else:
            tile.line.color.rgb = CARD_BORDER_DARK
            tile.line.width = 9525
            text_color = TEXT_ON_DARK_FAINT

        add_text(slide, f"logo-{n}-text", label,
                 x_px=tx, y_px=ty, w_px=tile_w, h_px=tile_h,
                 font_size_px=13, color=text_color, bold=True,
                 align="center", anchor="middle", uppercase=True)

    # Convergence
    conv_y = 720 - 56 - 42
    conv_h = 42
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence",
             "12 practices, 8 industries, 3 continents — common pattern.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=conv_h,
             font_size_px=14, color=WHITE, italic=True, anchor="middle",
             padding_px=(0, 22, 0, 22))

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "76",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "76d_logo-wall-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
