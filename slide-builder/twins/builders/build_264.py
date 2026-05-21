"""
Builder for pattern 264: Dot plot / strip chart — performance score distribution.

Source HTML: _pattern-library/264_dot-plot-strip-chart.html

Layout: title + dot plot (5 function rows, ~15 dots each + outlier + median tick)
on left, observations panel on right.

LEGEND PLACEMENT: Right-aligned below subheadline (top-y ≥ 230, right edge ≈ 1240).
"""
from pathlib import Path
import sys
import random

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Performance score distribution — <strong>spread varies sharply across functions.</strong>",
        subtitle="Individual employee performance scores (0–100) across five business functions, Q2 assessment cycle.",
    )

    # === LEGEND — below subheadline, right-aligned ===
    leg_y = 230
    leg_w = 360
    leg_x = 1240 - leg_w
    # data point
    add_rect(slide, "legend-dot-swatch", leg_x, leg_y + 7, 10, 10, BRAND_ACCENT_SOFT)
    add_text(slide, "legend-dot-label", "Data point",
             x_px=leg_x + 16, y_px=leg_y + 2, w_px=80, h_px=18,
             font_size_px=11, color=TEXT_MID, bold=True)
    # outlier
    add_rect(slide, "legend-outlier-swatch", leg_x + 110, leg_y + 7, 10, 10, BRAND_ACCENT)
    add_text(slide, "legend-outlier-label", "Outlier",
             x_px=leg_x + 126, y_px=leg_y + 2, w_px=70, h_px=18,
             font_size_px=11, color=TEXT_MID, bold=True)
    # median
    add_rect(slide, "legend-median-swatch", leg_x + 196, leg_y + 4, 3, 16, BRAND_ACCENT)
    add_text(slide, "legend-median-label", "Median",
             x_px=leg_x + 204, y_px=leg_y + 2, w_px=80, h_px=18,
             font_size_px=11, color=TEXT_MID, bold=True)

    # Body
    body_top = 268
    body_bottom = 635
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    chart_w = int(body_w * 0.68)
    gap = 18
    panel_w = body_w - chart_w - gap

    chart_x = left_x
    chart_y = body_top
    chart_bg = add_rect(slide, "chart-panel", chart_x, chart_y, chart_w, body_h, CARD_BG)
    chart_bg.line.color.rgb = CARD_BORDER
    chart_bg.line.width = 9525

    # Title + n
    add_text(slide, "chart-title", "Performance score · individual observations · n=75",
             x_px=chart_x + 16, y_px=chart_y + 8, w_px=chart_w - 32, h_px=16,
             font_size_px=10, color=BRAND_PRIMARY, bold=True)

    # Plot area
    plot_left = chart_x + 130
    plot_right = chart_x + chart_w - 30
    plot_top = chart_y + 36
    plot_bottom = chart_y + body_h - 50
    plot_w = plot_right - plot_left
    plot_h = plot_bottom - plot_top

    # gridlines at 25, 50, 75
    for v in (0, 25, 50, 75, 100):
        gx = plot_left + int((v / 100) * plot_w)
        if v in (25, 50, 75):
            add_rect(slide, f"grid-{v}", gx, plot_top, 1, plot_h, CARD_BORDER)
        # tick label
        add_text(slide, f"x-tick-{v}", str(v),
                 x_px=gx - 16, y_px=plot_bottom + 4, w_px=32, h_px=14,
                 font_size_px=9, color=TEXT_MID, bold=True, align="center")
    # x-axis baseline
    add_rect(slide, "x-axis", plot_left, plot_bottom, plot_w, 1, BRAND_PRIMARY)
    add_text(slide, "x-axis-title", "PERFORMANCE SCORE",
             x_px=plot_left, y_px=plot_bottom + 20, w_px=plot_w, h_px=14,
             font_size_px=9, color=BRAND_PRIMARY, bold=True, align="center",
             letter_spacing_px=1)

    # 5 rows
    functions = [
        ("Q1 Finance", [45, 52, 58, 61, 65, 67, 70, 73, 75, 78, 81, 84, 88, 91, 95], 38, 72),
        ("Q2 Operations", [58, 61, 63, 65, 67, 70, 72, 74, 76, 79, 81, 84, 88], 55, 68),
        ("Q3 Technology", [35, 40, 44, 48, 53, 56, 59, 62, 65, 67, 70, 74, 78, 83], 99, 61),
        ("Q4 HR", [44, 47, 50, 53, 56, 60, 62, 65, 67, 70, 73, 76, 80], 40, 58),
        ("Q5 Strategy", [54, 58, 62, 65, 68, 71, 74, 76, 82, 85, 88, 90], 92, 76),
    ]
    n_rows = len(functions)
    row_h = plot_h // n_rows
    rng = random.Random(7)
    for i, (name, scores, outlier, median) in enumerate(functions):
        cy = plot_top + i * row_h + row_h // 2
        # category label (left of plot)
        add_text(slide, f"row-{i+1}-name", name,
                 x_px=chart_x + 6, y_px=cy - 8, w_px=118, h_px=16,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True, align="right")
        # row separator hairline
        if i < n_rows - 1:
            add_rect(slide, f"row-sep-{i+1}", plot_left, plot_top + (i + 1) * row_h, plot_w, 1, CARD_BORDER)
        # dots
        for j, sc in enumerate(scores):
            dx = plot_left + int((sc / 100) * plot_w)
            jitter = rng.randint(-7, 7)
            dy = cy + jitter
            add_rect(slide, f"dot-{i+1}-{j+1}", dx - 4, dy - 4, 8, 8, BRAND_ACCENT_SOFT)
        # outlier
        ox = plot_left + int((outlier / 100) * plot_w)
        add_rect(slide, f"outlier-{i+1}", ox - 5, cy - 5, 10, 10, BRAND_ACCENT)
        add_text(slide, f"outlier-{i+1}-label", str(outlier),
                 x_px=ox - 14, y_px=cy - 24, w_px=28, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT, bold=True, align="center")
        # median tick
        mx = plot_left + int((median / 100) * plot_w)
        add_rect(slide, f"median-{i+1}-line", mx - 1, cy - 18, 3, 36, BRAND_ACCENT)
        add_text(slide, f"median-{i+1}-label", str(median),
                 x_px=mx + 6, y_px=cy - 8, w_px=24, h_px=14,
                 font_size_px=10, color=BRAND_ACCENT, bold=True)

    # Observations panel
    pn_x = chart_x + chart_w + gap
    pn_y = body_top
    add_rect(slide, "obs-panel", pn_x, pn_y, panel_w, body_h, BRAND_PRIMARY)
    add_text(slide, "obs-header", "KEY OBSERVATIONS",
             x_px=pn_x + 18, y_px=pn_y + 18, w_px=panel_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             letter_spacing_px=1.4, uppercase=True)
    add_text(slide, "obs-sub", "Three findings that drive action.",
             x_px=pn_x + 18, y_px=pn_y + 40, w_px=panel_w - 36, h_px=40,
             font_size_px=13, color=WHITE, bold=True)

    bullets = [
        ("Widest spread: Technology (35→99).", " A 64-point range signals inconsistent capability development — coaching investment is uneven across teams."),
        ("Highest median: Strategy (76).", " Strategy leads all functions; Finance is second at 72. Both sit above the organisation mid-point of 65."),
        ("Top outliers in Tech & Strategy.", " Scores of 99 and 92 sit more than 30 points above function medians — flag as retention and mentoring priorities."),
    ]
    bul_top = pn_y + 96
    bul_area_h = body_h - 110
    item_h = bul_area_h // len(bullets)
    for i, (head, tail) in enumerate(bullets):
        iy = bul_top + i * item_h
        add_text(slide, f"obs-{i+1}-marker", "■",
                 x_px=pn_x + 18, y_px=iy, w_px=12, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"obs-{i+1}", f"<strong>{head}</strong>{tail}",
                 x_px=pn_x + 34, y_px=iy - 2, w_px=panel_w - 52, h_px=item_h - 6,
                 font_size_px=10, color=WHITE, emphasis_color=WHITE)

    add_footer(slide, page_num=264)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "264_dot-plot-strip-chart.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
