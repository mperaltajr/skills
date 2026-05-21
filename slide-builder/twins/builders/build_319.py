"""
Builder for pattern 319: 3-bucket dark.

3-card grid with numbered badge, title, bullets, and bottom stat strip.

Source HTML: _pattern-library/319_3bucket-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_STAT_BG = RGBColor(0x42, 0x24, 0x68)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Three pillars driving <strong>sustainable growth</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=24, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Strategic priorities for the next planning horizon — Q3 through Q4 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # 3-card grid
    grid_top = 220
    grid_bot = 668
    grid_left = 48
    grid_right = 1232
    gap = 20
    card_w = (grid_right - grid_left - 2 * gap) // 3
    card_h = grid_bot - grid_top

    accent_colors = [BRAND_ACCENT, RGBColor(0x77, 0x77, 0x90), BRAND_ACCENT_SOFT]
    cards = [
        ("01", "Accelerate Core Modernisation",
         ["Migrate legacy platforms to cloud-native architecture",
          "Retire technical debt across three critical systems",
          "Standardise APIs for interoperability at scale",
          "Deliver zero-downtime cutover for flagship product"],
         "$42M", "Annualised cost saving target"),
        ("02", "Scale AI-Enabled Operations",
         ["Deploy intelligent automation across finance and ops",
          "Embed GenAI copilots in front-office workflows",
          "Build data foundation to support model governance",
          "Upskill 2,400 employees through AI fluency programme"],
         "35%", "Productivity lift by end of FY26"),
        ("03", "Strengthen Client Value Delivery",
         ["Redesign delivery model around outcome-based pricing",
          "Launch integrated CX measurement across all accounts",
          "Reduce time-to-value from 18 months to under 9",
          "Activate strategic alliance ecosystem for co-delivery"],
         "+18 pts", "NPS improvement target vs. baseline"),
    ]

    for i, (badge, title, bullets, stat_v, stat_l) in enumerate(cards):
        cx = grid_left + i * (card_w + gap)
        add_rect(slide, f"card-{i+1}-bg", cx, grid_top, card_w, card_h, CARD_BG)
        # Top accent strip
        add_rect(slide, f"card-{i+1}-accent", cx, grid_top, card_w, 3, accent_colors[i])
        # Numbered badge circle
        add_rect(slide, f"card-{i+1}-badge", cx + 20, grid_top + 20, 32, 32, BRAND_ACCENT)
        add_text(slide, f"card-{i+1}-badge-text", badge,
                 x_px=cx + 20, y_px=grid_top + 20, w_px=32, h_px=32,
                 font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle")
        # Title
        add_text(slide, f"card-{i+1}-title", title,
                 x_px=cx + 20, y_px=grid_top + 64, w_px=card_w - 40, h_px=44,
                 font_size_px=14, color=WHITE, bold=True)
        # Bullets
        by = grid_top + 120
        for j, b in enumerate(bullets):
            add_text(slide, f"card-{i+1}-bullet-{j+1}", "– " + b,
                     x_px=cx + 20, y_px=by, w_px=card_w - 40, h_px=44,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
            by += 42
        # Bottom stat strip
        st_h = 64
        st_y = grid_bot - st_h
        add_rect(slide, f"card-{i+1}-stat-bg", cx, st_y, card_w, st_h, CARD_STAT_BG)
        add_text(slide, f"card-{i+1}-stat-value", stat_v,
                 x_px=cx + 20, y_px=st_y + 10, w_px=card_w - 40, h_px=28,
                 font_size_px=20, color=WHITE, bold=True)
        add_text(slide, f"card-{i+1}-stat-label", stat_l,
                 x_px=cx + 20, y_px=st_y + 40, w_px=card_w - 40, h_px=18,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, letter_spacing_px=1)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "319",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "319_3bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
