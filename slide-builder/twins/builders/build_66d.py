"""
Builder for pattern 66d: Combo chart bars + line (dark variant).

Source HTML: _pattern-library/66_combo-chart-bars-line-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
CHART_PLACEHOLDER = RGBColor(0x42, 0x22, 0x66)
ANNOT_BG = RGBColor(0x1A, 0x05, 0x30)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Volume and quality, both rising — the pilot signal.",
        x_px=64, y_px=20, w_px=1050, h_px=80,
        font_size_px=27, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Weekly decks completed (bars) and average QC score (line), pilot weeks 1-8.",
        x_px=64, y_px=108, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 64
    g_right = 1280 - 64
    g_bottom = 720 - 72 - 48
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    annot_w = 320
    gap = 24
    chart_w = g_w - annot_w - gap

    cz = add_rect(slide, "chart-zone-bg", g_left, g_top, chart_w, g_h, CARD_BG_DARK)
    cz.line.color.rgb = CARD_BORDER_DARK
    cz.line.width = 9525

    add_text(
        slide, "chart-title", "PILOT THROUGHPUT VS QUALITY · W1–W8",
        x_px=g_left + 24, y_px=g_top + 20, w_px=chart_w - 48 - 200, h_px=18,
        font_size_px=13, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    leg_x = g_left + chart_w - 260
    leg_y = g_top + 20
    add_rect(slide, "legend-1-swatch", leg_x, leg_y + 4, 12, 12, BRAND_ACCENT_SOFT)
    add_text(
        slide, "legend-1-label", "Decks completed",
        x_px=leg_x + 16, y_px=leg_y + 2, w_px=110, h_px=18,
        font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
    )
    add_rect(slide, "legend-2-swatch", leg_x + 130, leg_y + 9, 14, 2, BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "Avg QC score",
        x_px=leg_x + 146, y_px=leg_y + 2, w_px=110, h_px=18,
        font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
    )

    chart_canvas_y = g_top + 50
    chart_canvas_h = g_h - 70
    add_rect(slide, "chart-canvas", g_left + 24, chart_canvas_y,
             chart_w - 48, chart_canvas_h, CHART_PLACEHOLDER)

    ap_x = g_left + chart_w + gap
    add_rect(slide, "annot-bg", ap_x, g_top, annot_w, g_h, ANNOT_BG)

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

    cv_y = g_bottom + 6
    cv_h = 38
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, ANNOT_BG)
    add_text(
        slide, "convergence",
        "If W9–W10 hold this shape, the pilot clears its gate and we scope a Q3 rollout.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "66",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "66d_combo-chart-bars-line.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
