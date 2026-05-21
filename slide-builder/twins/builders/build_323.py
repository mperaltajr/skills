"""
Builder for pattern 323: 4-bucket dark.

4-card grid with accent strip, numbered circle, title, bullets, and bottom metric.

Source HTML: _pattern-library/323_4bucket-dark.html
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
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
ACCENT_SECONDARY = RGBColor(0x77, 0x77, 0x90)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Four pillars of <strong>operational excellence</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=24, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "A structured framework across strategy, execution, talent, and measurement",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # 4-card grid
    grid_top = 220
    grid_bot = 664
    grid_left = 48
    grid_right = 1232
    gap = 16
    card_w = (grid_right - grid_left - 3 * gap) // 4
    card_h = grid_bot - grid_top

    cards = [
        ("1", "Strategic Alignment",
         ["Link portfolio goals to enterprise priorities",
          "Quarterly OKR review cadence",
          "Executive sponsorship confirmed"],
         "94% aligned", BRAND_ACCENT),
        ("2", "Delivery Execution",
         ["Agile-at-scale across 12 squads",
          "Automated CI/CD pipeline in place",
          "Incident SLA <2 hr P1 resolution"],
         "↑ 18% velocity", ACCENT_SECONDARY),
        ("3", "Talent & Capability",
         ["Skills matrix refreshed bi-annually",
          "Internal mobility rate above benchmark",
          "AI upskilling for 800+ practitioners"],
         "82 NPS score", BRAND_ACCENT),
        ("4", "Performance Measurement",
         ["Real-time dashboard for all KPIs",
          "Monthly steering committee review",
          "Value tracking from day one"],
         "$4.2M tracked", ACCENT_SECONDARY),
    ]

    for i, (num, title, bullets, metric, accent_col) in enumerate(cards):
        cx = grid_left + i * (card_w + gap)
        add_rect(slide, f"card-{i+1}-bg", cx, grid_top, card_w, card_h, CARD_BG)
        # Accent strip
        add_rect(slide, f"card-{i+1}-accent", cx, grid_top, card_w, 4, accent_col)
        # Number circle
        add_rect(slide, f"card-{i+1}-number", cx + 20, grid_top + 20, 34, 34, BRAND_ACCENT)
        add_text(slide, f"card-{i+1}-number-text", num,
                 x_px=cx + 20, y_px=grid_top + 20, w_px=34, h_px=34,
                 font_size_px=14, color=WHITE, bold=True, align="center", anchor="middle")
        # Title
        add_text(slide, f"card-{i+1}-title", title,
                 x_px=cx + 20, y_px=grid_top + 68, w_px=card_w - 40, h_px=44,
                 font_size_px=13, color=WHITE, bold=True)
        # Bullets
        by = grid_top + 126
        for j, b in enumerate(bullets):
            add_text(slide, f"card-{i+1}-bullet-{j+1}", "– " + b,
                     x_px=cx + 20, y_px=by, w_px=card_w - 40, h_px=58,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
            by += 56
        # Metric
        add_text(slide, f"card-{i+1}-metric", metric,
                 x_px=cx + 20, y_px=grid_bot - 50, w_px=card_w - 40, h_px=30,
                 font_size_px=18, color=BRAND_ACCENT_SOFT, bold=True)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "323",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "323_4bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
