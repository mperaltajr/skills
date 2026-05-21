"""
Builder for pattern 143d: Differentiators (3 columns) — dark.

Source HTML: _pattern-library/143_differentiators-3col-dark.html
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

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Three structural advantages</strong> competitors cannot replicate — speed, depth, and accountability",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Speed · Depth · Accountability — the three differentiators evaluators cite most often",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 3 cols
    col_x = 48
    col_y = 220
    col_bot = 644
    total_w = 1280 - 96
    col_w = total_w // 3
    col_h = col_bot - col_y

    cards = [
        ("01", "Integrated Delivery Model",
         "We embed strategy, technology, and change in one team — no handoffs, no gaps. Your program doesn't get translated between three firms.",
         "3.2×", "faster time to value vs. multi-vendor approach"),
        ("02", "Proprietary Accelerators",
         "Our pre-built tools reduce design and build phases by 40%. Components are tested at scale and maintained by 200+ practitioners.",
         "40%", "reduction in build phase cost"),
        ("03", "Outcome Accountability",
         "We put skin in the game. Fees tied to adoption and benefit realization — not just deliverables. We succeed when you succeed.",
         "94%", "of outcomes delivered to target within 6 months"),
    ]

    for i, (num, heading, body, metric, label) in enumerate(cards):
        n = i + 1
        cx = col_x + i * col_w

        # Top accent strip
        add_rect(slide, f"card-{n}-bg", cx, col_y, col_w, 4, BRAND_ACCENT)
        # Vertical divider (between columns)
        if i > 0:
            add_rect(slide, f"card-{n}-divider", cx, col_y + 4, 1, col_h - 4, CARD_BORDER_DARK)

        # Numeral
        add_text(slide, f"card-{n}-num", num,
                 x_px=cx + 28, y_px=col_y + 24, w_px=120, h_px=58,
                 font_size_px=46, color=BRAND_ACCENT, bold=True)

        # Heading
        add_text(slide, f"card-{n}-heading", heading,
                 x_px=cx + 28, y_px=col_y + 90, w_px=col_w - 56, h_px=24,
                 font_size_px=17, color=BRAND_ACCENT_SOFT, bold=True)

        # Description body
        add_text(slide, f"card-{n}-body", body,
                 x_px=cx + 28, y_px=col_y + 122, w_px=col_w - 56, h_px=160,
                 font_size_px=12, color=WHITE)

        # Proof box (footer)
        pb_y = col_y + col_h - 80
        add_text(slide, f"card-{n}-footer-stat", metric,
                 x_px=cx + 36, y_px=pb_y + 8, w_px=col_w - 72, h_px=24,
                 font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"card-{n}-footer", label,
                 x_px=cx + 36, y_px=pb_y + 34, w_px=col_w - 72, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # Convergence bar
    conv_y = col_bot + 12
    add_rect(slide, "conv-line-left", 48, conv_y, 480, 2, BRAND_ACCENT_SOFT)
    add_text(slide, "convergence", "Speed · Depth · Accountability",
             x_px=540, y_px=conv_y - 6, w_px=200, h_px=18,
             font_size_px=11, color=BRAND_ACCENT_SOFT, italic=True, bold=True, align="center")
    add_rect(slide, "conv-line-right", 752, conv_y, 480, 2, BRAND_ACCENT)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "143",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "143d_differentiators-3col.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
