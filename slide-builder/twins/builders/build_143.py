"""
Builder for pattern 143: Differentiators (3 columns).

Source HTML: _pattern-library/143_differentiators-3col.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (26px, no subtitle in this pattern)
    add_text(slide, "title",
             "<strong>Three structural advantages</strong> competitors cannot replicate — speed, depth, and accountability",
             x_px=56, y_px=58, w_px=1000, h_px=70,
             font_size_px=26, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_rect(slide, "brand-rule", 56, 138, 56, 3, BRAND_ACCENT)

    # 3 cols: top:148 left:48 right:48 bottom:100
    col_x = 48
    col_y = 148
    total_w = 1280 - 96
    col_w = total_w // 3
    col_h = 720 - 100 - col_y

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
            add_rect(slide, f"card-{n}-divider", cx, col_y + 4, 1, col_h - 4, CARD_BORDER)

        # Numeral (52px brand-accent)
        add_text(slide, f"card-{n}-num", num,
                 x_px=cx + 28, y_px=col_y + 24, w_px=120, h_px=58,
                 font_size_px=46, color=BRAND_ACCENT, bold=True)

        # Heading
        add_text(slide, f"card-{n}-heading", heading,
                 x_px=cx + 28, y_px=col_y + 90, w_px=col_w - 56, h_px=24,
                 font_size_px=17, color=BRAND_PRIMARY, bold=True)

        # Description body
        add_text(slide, f"card-{n}-body", body,
                 x_px=cx + 28, y_px=col_y + 122, w_px=col_w - 56, h_px=160,
                 font_size_px=12, color=TEXT_DARK)

        # Proof box (footer)
        pb_y = col_y + col_h - 80
        add_text(slide, f"card-{n}-footer-stat", metric,
                 x_px=cx + 36, y_px=pb_y + 8, w_px=col_w - 72, h_px=24,
                 font_size_px=20, color=BRAND_PRIMARY_MID, bold=True)
        add_text(slide, f"card-{n}-footer", label,
                 x_px=cx + 36, y_px=pb_y + 34, w_px=col_w - 72, h_px=22,
                 font_size_px=11, color=TEXT_MID)

    # Convergence bar
    conv_y = 720 - 60
    add_rect(slide, "conv-line-left", 48, conv_y, 480, 2, BRAND_PRIMARY)
    add_text(slide, "convergence", "Speed · Depth · Accountability",
             x_px=540, y_px=conv_y - 6, w_px=200, h_px=18,
             font_size_px=11, color=BRAND_PRIMARY_MID, italic=True, bold=True, align="center")
    add_rect(slide, "conv-line-right", 752, conv_y, 480, 2, BRAND_ACCENT)

    add_footer(slide, page_num=143)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "143_differentiators-3col.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
