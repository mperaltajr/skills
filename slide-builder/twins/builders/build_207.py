"""
Builder for pattern 207: Dual Chart Side by Side.

Two chart-canvas placeholders (line chart + horizontal bar chart) with title,
caption, and shared legend.

Source HTML: _pattern-library/207_dual-chart-side-by-side.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Two charts, one <strong>clear story</strong>",
        subtitle="Volume trend and segment share displayed side by side for instant comparison",
        title_h=42, subtitle_h=20, brand_rule_w=64, title_w=820,
    )

    # Legend (top right, shared)
    leg_x = 64 + 820 + 16
    leg_y = 64
    legend_items = [
        ("Series A", BRAND_PRIMARY_MID),
        ("Series B", BRAND_ACCENT),
        ("Highlighted segment", BRAND_ACCENT),
    ]
    for i, (label, color) in enumerate(legend_items):
        ly = leg_y + i * 18
        add_rect(slide, f"legend-{i+1}-swatch", leg_x, ly + 5, 14, 3, color)
        add_text(slide, f"legend-{i+1}-label", label,
                 x_px=leg_x + 22, y_px=ly, w_px=180, h_px=14,
                 font_size_px=9, color=TEXT_MID)

    # Two chart panels
    body_top = 170
    body_bot = 600
    body_h = body_bot - body_top
    panel_w = (1280 - 128 - 24) // 2  # leave 24px in middle for divider
    div_x = 64 + panel_w + 12

    # Left chart panel
    add_text(slide, "chart-1-title", "Volume Trend",
             x_px=64, y_px=body_top, w_px=panel_w, h_px=18,
             font_size_px=12, color=TEXT_DARK, bold=True)
    add_rect(slide, "chart-1-title-rule", 64, body_top + 22, panel_w, 1, CARD_BORDER)
    canvas1 = add_rect(slide, "chart-1-canvas", 64, body_top + 32, panel_w, body_h - 70, CARD_BG)
    canvas1.line.color.rgb = CARD_BORDER
    canvas1.line.width = 9525
    add_text(slide, "chart-1-caption",
             "Both series indexed to 0 at Q1. Series B shows faster acceleration from Q3 onward.",
             x_px=64, y_px=body_top + body_h - 32, w_px=panel_w, h_px=24,
             font_size_px=10, color=TEXT_MID, italic=True)

    # Divider
    add_rect(slide, "divider-line", div_x, body_top + 8, 2, body_h - 16, BRAND_ACCENT)

    # Right chart panel
    right_x = div_x + 12
    add_text(slide, "chart-2-title", "Top Segments by Share",
             x_px=right_x, y_px=body_top, w_px=panel_w, h_px=18,
             font_size_px=12, color=TEXT_DARK, bold=True)
    add_rect(slide, "chart-2-title-rule", right_x, body_top + 22, panel_w, 1, CARD_BORDER)
    canvas2 = add_rect(slide, "chart-2-canvas", right_x, body_top + 32, panel_w, body_h - 70, CARD_BG)
    canvas2.line.color.rgb = CARD_BORDER
    canvas2.line.width = 9525
    add_text(slide, "chart-2-caption",
             "Health leads all segments at 91 index points — 7 pts above nearest peer (Retail at 85).",
             x_px=right_x, y_px=body_top + body_h - 32, w_px=panel_w, h_px=24,
             font_size_px=10, color=TEXT_MID, italic=True)

    add_footer(slide, page_num=207)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "207_dual-chart-side-by-side.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
