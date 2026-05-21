"""
Builder for pattern 77d: Multi-image grid with captions — dark variant.

Source HTML: _pattern-library/77_multi-image-grid-dark.html
Light template: twins/builders/build_77.py
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

IMAGE_BG_DARK = RGBColor(0x46, 0x26, 0x68)
IMAGE_BORDER_DARK = RGBColor(0x66, 0x42, 0x88)
FEATURED_BG_DARK = RGBColor(0x5C, 0x2D, 0x87)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "Pilot deck galleries — six pages, six redos.",
             x_px=64, y_px=20, w_px=1000, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Side-by-side before and after for the three slides reviewers flagged hardest. One redo carries the deck.",
             x_px=64, y_px=108, w_px=900, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 56, 3, BRAND_ACCENT_SOFT)

    # Grid 3 cols x 2 rows
    grid_left = 64
    grid_top = 220
    grid_right = 1280 - 64
    grid_bot = 596  # leave room for convergence strip below
    grid_w = grid_right - grid_left
    grid_h = grid_bot - grid_top
    gap = 18
    card_w = (grid_w - gap * 2) // 3
    card_h = (grid_h - gap) // 2

    items = [
        ("SLIDE 2 · BEFORE", "[ Wall-of-bullets layout, no visual hierarchy ]",
         "Slide 2 — Before", "Wall of bullets, no structure.", False),
        ("SLIDE 2 · AFTER", "[ Anchor statement with three supporting cards ]",
         "Slide 2 — After", "Anchor + three cards.", False),
        ("SLIDE 5 · BEFORE", "[ Three-column table, undifferentiated rows ]",
         "Slide 5 — Before", "3-col table, no story.", False),
        ("SLIDE 5 · AFTER", "[ Three vertical pillars, headline-first logic ]",
         "Slide 5 — After", "Vertical pillars, clear logic.", True),
        ("SLIDE 7 · BEFORE", "[ Generic ask slide, mixed formats ]",
         "Slide 7 — Before", "Generic ask, generic format.", False),
        ("SLIDE 7 · AFTER", "[ Single focal-point ask, isolated on slide ]",
         "Slide 7 — After", "Single focal point ask.", False),
    ]

    for i, (corner, label, cap_head, cap_desc, featured) in enumerate(items):
        n = i + 1
        row = i // 3
        col = i % 3
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)

        card_fill = FEATURED_BG_DARK if featured else CARD_BG_DARK
        card = add_rect(slide, f"photo-{n}-card", cx, cy, card_w, card_h, card_fill)
        if featured:
            card.line.color.rgb = BRAND_ACCENT_SOFT
            card.line.width = 19050
        else:
            card.line.color.rgb = CARD_BORDER_DARK
            card.line.width = 9525

        img_x = cx + 10
        img_y = cy + 10
        img_w = card_w - 20
        img_h = card_h - 70
        zone_fill = FEATURED_BG_DARK if featured else IMAGE_BG_DARK
        zone = add_rect(slide, f"photo-{n}-zone", img_x, img_y, img_w, img_h, zone_fill)
        zone.line.color.rgb = BRAND_ACCENT_SOFT if featured else IMAGE_BORDER_DARK
        zone.line.width = 14288

        add_text(slide, f"photo-{n}-corner-tag", corner,
                 x_px=img_x + 8, y_px=img_y + 6, w_px=160, h_px=18,
                 font_size_px=9, color=WHITE if featured else BRAND_ACCENT_SOFT, bold=True,
                 bg_fill=BRAND_ACCENT if featured else BRAND_PRIMARY,
                 padding_px=(2, 6, 2, 6))

        if featured:
            add_text(slide, f"photo-{n}-featured-flag", "FEATURED",
                     x_px=img_x + img_w - 78, y_px=img_y + 6, w_px=70, h_px=18,
                     font_size_px=9, color=WHITE, bold=True, align="center",
                     bg_fill=BRAND_ACCENT, padding_px=(2, 6, 2, 6))

        add_text(slide, f"photo-{n}-label", label,
                 x_px=img_x, y_px=img_y, w_px=img_w, h_px=img_h,
                 font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
                 align="center", anchor="middle")

        cap_y = img_y + img_h + 10
        add_text(slide, f"photo-{n}-caption", cap_head,
                 x_px=cx + 12, y_px=cap_y, w_px=card_w - 24, h_px=18,
                 font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"photo-{n}-caption-desc", cap_desc,
                 x_px=cx + 12, y_px=cap_y + 20, w_px=card_w - 24, h_px=18,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # Convergence
    conv_y = 612
    conv_h = 46
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, conv_h, BRAND_PRIMARY_MID)
    add_rect(slide, "convergence-accent", 64, conv_y, 4, conv_h, BRAND_ACCENT_SOFT)
    add_text(slide, "convergence",
             "Slide 5 is the one that flipped the room — pillars beat tables when the audience has to repeat the argument later.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=conv_h,
             font_size_px=14, color=WHITE, italic=True, anchor="middle",
             padding_px=(0, 22, 0, 22))

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "77",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "77d_multi-image-grid-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
