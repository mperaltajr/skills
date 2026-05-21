"""
Builder for pattern 66: Combo chart (bars + line) with annotation panel.

SVG-driven (picture-asset per SHAPE-ROLES): single chart-canvas placeholder
for the bar+line chart. Legends, annotation panel, convergence are addressable.

Source HTML: _pattern-library/66_combo-chart-bars-line.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER = RGBColor(0xF4, 0xF4, 0xF6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Volume and quality, both rising — the pilot signal.",
        x_px=64, y_px=50, w_px=1050, h_px=40,
        font_size_px=27, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Weekly decks completed (bars) and average QC score (line), pilot weeks 1-8.",
        x_px=64, y_px=98, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 140, 56, 3, BRAND_ACCENT)

    # Body row: chart-zone (1fr) + annotation (320)
    g_top = 188
    g_left = 64
    g_right = 1280 - 64
    g_bottom = 720 - 72 - 48  # leave room for convergence + footer
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    annot_w = 320
    gap = 24
    chart_w = g_w - annot_w - gap

    # Chart zone
    cz = add_rect(slide, "chart-zone-bg", g_left, g_top, chart_w, g_h, CARD_BG)
    cz.line.color.rgb = CARD_BORDER
    cz.line.width = 9525

    # Chart head: title + legend
    add_text(
        slide, "chart-title", "PILOT THROUGHPUT VS QUALITY · W1–W8",
        x_px=g_left + 24, y_px=g_top + 20, w_px=chart_w - 48 - 200, h_px=18,
        font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True,
    )
    # Legend (top-right of chart) — give item 2 a 30px wider gap to prevent touching
    leg_x = g_left + chart_w - 260
    leg_y = g_top + 20
    add_rect(slide, "legend-1-swatch", leg_x, leg_y + 4, 12, 12, BRAND_PRIMARY)
    add_text(
        slide, "legend-1-label", "Decks completed",
        x_px=leg_x + 16, y_px=leg_y + 2, w_px=110, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )
    add_rect(slide, "legend-2-swatch", leg_x + 130, leg_y + 9, 14, 2, BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "Avg QC score",
        x_px=leg_x + 146, y_px=leg_y + 2, w_px=110, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )

    # Chart canvas (picture-asset placeholder)
    chart_canvas_y = g_top + 50
    chart_canvas_h = g_h - 70
    add_rect(slide, "chart-canvas", g_left + 24, chart_canvas_y,
             chart_w - 48, chart_canvas_h, CHART_PLACEHOLDER)

    # Annotation panel (right)
    ap_x = g_left + chart_w + gap
    ap = add_rect(slide, "annot-bg", ap_x, g_top, annot_w, g_h, BRAND_PRIMARY)

    add_text(
        slide, "annot-header", "WHAT THE CURVES SAY",
        x_px=ap_x + 22, y_px=g_top + 22, w_px=annot_w - 44, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "annot-sub", "Volume more than doubled while QC climbed 25 points.",
        x_px=ap_x + 22, y_px=g_top + 42, w_px=annot_w - 44, h_px=44,
        font_size_px=16, color=WHITE, bold=True,
    )

    bullets = [
        "Typical pilot pattern is one-or-the-other — throughput rises, quality slips, or vice versa.",
        "Both lines bent up after W3, when skeleton-first rendering shipped.",
        "W7–W8 plateau on volume is capacity, not demand — queue is at 11 decks.",
    ]
    list_top = g_top + 102
    item_h = (g_h - 110) // 3
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = list_top + bi * item_h
        add_text(
            slide, f"annot-{bn}-marker", "■",
            x_px=ap_x + 22, y_px=by, w_px=14, h_px=18,
            font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"annot-{bn}-body", b,
            x_px=ap_x + 40, y_px=by, w_px=annot_w - 60, h_px=item_h - 8,
            font_size_px=12, color=WHITE,
        )

    # Convergence band
    cv_y = g_bottom + 6
    cv_h = 38
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, BRAND_PRIMARY)
    add_text(
        slide, "convergence",
        "If W9–W10 hold this shape, the pilot clears its gate and we scope a Q3 rollout.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_footer(slide, page_num=66)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "66_combo-chart-bars-line.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
