"""
Builder for pattern 97d: Mission statement slide — dark variant.

Source HTML: _pattern-library/97_mission-statement-slide-dark.html
Light template: twins/builders/build_97.py

Pure hero. Compact action title + brand-rule, then centered hero stage.
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

    # Compact action title (hero pattern — small chrome title above stage)
    add_text(slide, "title",
             "Our mission — sharp thinking, every time.",
             x_px=56, y_px=42, w_px=1168, h_px=60,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_rect(slide, "brand-rule", 56, 132, 56, 3, BRAND_ACCENT_SOFT)

    # Centered hero stage
    stage_top = 220
    stage_x = 56
    stage_w = 1280 - 112

    pre_y = stage_top + 20
    add_text(slide, "hero-statement-label", "OUR MISSION",
             x_px=stage_x, y_px=pre_y, w_px=stage_w, h_px=18,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True,
             align="center", uppercase=True)

    add_text(slide, "hero-statement",
             "Make structured thinking the default for every consulting deck.",
             x_px=stage_x + 80, y_px=pre_y + 50, w_px=stage_w - 160, h_px=160,
             font_size_px=48, color=WHITE, align="center", bold=False)

    add_rect(slide, "hero-rule",
             (1280 - 120) // 2, pre_y + 230, 120, 3, BRAND_ACCENT)

    sub_y = pre_y + 274
    sub_block_w = 980
    sub_block_x = (1280 - sub_block_w) // 2
    half_w = (sub_block_w - 64) // 2

    add_text(slide, "hero-sub-1-label", "WE DO THIS BY",
             x_px=sub_block_x, y_px=sub_y, w_px=half_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "hero-sub-1-text",
             "Locking the argument in a coached storyline session before any slide is built.",
             x_px=sub_block_x, y_px=sub_y + 22, w_px=half_w, h_px=60,
             font_size_px=14, color=WHITE, bold=True)

    add_rect(slide, "hero-sub-divider",
             sub_block_x + half_w + 32, sub_y, 1, 80, CARD_BORDER_DARK)

    right_x = sub_block_x + half_w + 64
    add_text(slide, "hero-sub-2-label", "WE MEASURE IT BY",
             x_px=right_x, y_px=sub_y, w_px=half_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "hero-sub-2-text",
             "Deck cycle time and first-review partner sign-off rate.",
             x_px=right_x, y_px=sub_y + 22, w_px=half_w, h_px=60,
             font_size_px=14, color=WHITE, bold=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "97",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "97d_mission-statement-slide-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
