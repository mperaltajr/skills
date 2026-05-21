"""
Builder for pattern 262: Multi-line event flags — NPS index with annotated events.

Source HTML: _pattern-library/262_multi-line-event-flags.html

Layout: title + line chart (12 quarters, 3 product lines, 3 event flags) on left,
trend insights panel on right.

LEGEND PLACEMENT: Right-aligned below subheadline (top-y ≥ 230, right edge ≈ 1240).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def _draw_polyline(slide, points, color, width_emu, dashed=False):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        line = slide.shapes.add_connector(1, 0, 0, 0, 0)
        line.begin_x = px_to_emu(x1)
        line.begin_y = px_to_emu(y1)
        line.end_x = px_to_emu(x2)
        line.end_y = px_to_emu(y2)
        line.line.color.rgb = color
        line.line.width = width_emu
        if dashed:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            line.line.dash_style = MSO_LINE_DASH_STYLE.DASH


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Product A momentum accelerates <strong>as competitors retreat and pricing resets.</strong>",
        subtitle="Customer satisfaction index (0–100) by quarter, Q1 2024–Q4 2026 — three product lines with annotated market events.",
    )

    # === LEGEND — below subheadline, right-aligned ===
    leg_y = 230
    leg_w = 380
    leg_x = 1240 - leg_w
    # Product A
    add_rect(slide, "legend-A-swatch", leg_x, leg_y + 8, 16, 4, BRAND_ACCENT)
    add_text(slide, "legend-A-label", "Product A",
             x_px=leg_x + 20, y_px=leg_y + 2, w_px=80, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)
    # Product B
    add_rect(slide, "legend-B-swatch", leg_x + 110, leg_y + 8, 16, 4, BRAND_PRIMARY_MID)
    add_text(slide, "legend-B-label", "Product B",
             x_px=leg_x + 130, y_px=leg_y + 2, w_px=80, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)
    # Product C (dashed)
    add_rect(slide, "legend-C-swatch", leg_x + 220, leg_y + 8, 16, 4, TEXT_MID)
    add_text(slide, "legend-C-label", "Product C (dashed)",
             x_px=leg_x + 240, y_px=leg_y + 2, w_px=140, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)

    # === Body ===
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
    chart_bg = add_rect(slide, "chart-canvas", chart_x, chart_y, chart_w, body_h, CARD_BG)
    chart_bg.line.color.rgb = CARD_BORDER
    chart_bg.line.width = 9525

    # Plot area inside chart
    plot_left = chart_x + 44
    plot_right = chart_x + chart_w - 24
    plot_top = chart_y + 40
    plot_bottom = chart_y + body_h - 40
    plot_w = plot_right - plot_left
    plot_h = plot_bottom - plot_top

    # Y axis label
    add_text(slide, "y-axis-title", "NPS INDEX",
             x_px=chart_x + 4, y_px=plot_top + plot_h // 2 - 8, w_px=40, h_px=16,
             font_size_px=8, color=BRAND_PRIMARY, bold=True,
             letter_spacing_px=0.8)
    # Y-axis tick labels
    for v in (0, 20, 40, 60, 80, 100):
        gy = plot_bottom - int((v / 100) * plot_h)
        add_text(slide, f"y-tick-{v}", str(v),
                 x_px=chart_x + 18, y_px=gy - 7, w_px=24, h_px=14,
                 font_size_px=9, color=TEXT_FAINT, align="right")
        add_rect(slide, f"y-grid-{v}", plot_left, gy, plot_w, 1, CARD_BORDER)

    # X-axis baseline
    add_rect(slide, "x-axis", plot_left, plot_bottom, plot_w, 2, BRAND_PRIMARY)

    # 12 quarters: Q1'24...Q4'26
    quarters = ["Q1", "Q2", "Q3", "Q4"] * 3
    year_marks = {0: "'24", 4: "'25", 8: "'26"}
    step = plot_w / 11
    for i, q in enumerate(quarters):
        gx = plot_left + int(i * step)
        add_text(slide, f"x-tick-{i+1}", q,
                 x_px=gx - 14, y_px=plot_bottom + 4, w_px=28, h_px=12,
                 font_size_px=8, color=TEXT_FAINT, align="center")
        if i in year_marks:
            add_text(slide, f"x-year-{i+1}", year_marks[i],
                     x_px=gx - 14, y_px=plot_bottom + 16, w_px=28, h_px=12,
                     font_size_px=8, color=TEXT_MID, bold=True, align="center")

    # Data
    A = [42, 48, 51, 55, 58, 62, 67, 71, 74, 78, 81, 85]
    B = [65, 63, 60, 58, 55, 52, 50, 48, 47, 46, 45, 44]
    C = [50, 50, 52, 53, 55, 57, 58, 60, 62, 63, 65, 67]

    def to_points(series):
        pts = []
        for i, v in enumerate(series):
            x = plot_left + int(i * step)
            y = plot_bottom - int((v / 100) * plot_h)
            pts.append((x, y))
        return pts

    pts_A = to_points(A)
    pts_B = to_points(B)
    pts_C = to_points(C)

    # Event flags at i=2 (Q3'24), i=4 (Q1'25), i=6 (Q3'25)
    events = [
        (2, "Product A relaunch"),
        (4, "Competitor exit"),
        (6, "Price reduction — B"),
    ]
    for ei, (idx, label) in enumerate(events):
        ex = plot_left + int(idx * step)
        # vertical dashed line via thin rect (no real dashes in pptx for rects, approximate solid grey)
        add_rect(slide, f"event-{ei+1}-line", ex, plot_top, 1, plot_h, TEXT_FAINT)
        # flag pill at top
        flag_w = 110
        flag_x = ex - flag_w // 2
        add_rect(slide, f"event-{ei+1}-flag", flag_x, plot_top + 2, flag_w, 18, TEXT_FAINT)
        add_text(slide, f"event-{ei+1}-flag-text", label,
                 x_px=flag_x, y_px=plot_top + 2, w_px=flag_w, h_px=18,
                 font_size_px=8, color=WHITE, bold=True, align="center", anchor="middle")

    # Draw lines (C first - underneath)
    _draw_polyline(slide, pts_C, TEXT_MID, 19050, dashed=True)
    _draw_polyline(slide, pts_B, BRAND_PRIMARY_MID, 25400, dashed=False)
    _draw_polyline(slide, pts_A, BRAND_ACCENT, 25400, dashed=False)

    # Dots
    for i, (x, y) in enumerate(pts_C):
        add_rect(slide, f"dot-C-{i+1}", x - 3, y - 3, 6, 6, TEXT_MID)
    for i, (x, y) in enumerate(pts_B):
        add_rect(slide, f"dot-B-{i+1}", x - 3, y - 3, 6, 6, BRAND_PRIMARY_MID)
    for i, (x, y) in enumerate(pts_A):
        add_rect(slide, f"dot-A-{i+1}", x - 3, y - 3, 6, 6, BRAND_ACCENT)

    # Right insight panel
    pn_x = chart_x + chart_w + gap
    pn_y = body_top
    add_rect(slide, "insight-panel", pn_x, pn_y, panel_w, body_h, BRAND_PRIMARY)

    add_text(slide, "panel-header", "TREND INSIGHTS",
             x_px=pn_x + 18, y_px=pn_y + 16, w_px=panel_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             letter_spacing_px=1.4, uppercase=True)
    add_text(slide, "panel-headline",
             "Product A is the clear beneficiary of every market disruption over the period.",
             x_px=pn_x + 18, y_px=pn_y + 36, w_px=panel_w - 36, h_px=72,
             font_size_px=14, color=WHITE, bold=True)

    bullets = [
        "The Q3 2024 relaunch inflected A's curve sharply upward — adding 16 index points in the following four quarters alone.",
        "Product B's Q3 2025 price cut slowed share erosion but has not reversed it — the gap to A now stands at 41 points.",
        "Product C tracks a stable mid-market position; absent a catalyst it will remain a credible floor but not a growth driver.",
    ]
    bul_top = pn_y + 124
    bul_area_h = body_h - 170
    item_h = bul_area_h // len(bullets)
    for i, b in enumerate(bullets):
        iy = bul_top + i * item_h
        add_text(slide, f"bullet-{i+1}-marker", "■",
                 x_px=pn_x + 18, y_px=iy, w_px=12, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"bullet-{i+1}", b,
                 x_px=pn_x + 34, y_px=iy - 2, w_px=panel_w - 52, h_px=item_h - 6,
                 font_size_px=10, color=WHITE)

    add_text(slide, "panel-source",
             "Source: Internal VoC, n=1,200/quarter. Index rebased to Q1 2024.",
             x_px=pn_x + 18, y_px=pn_y + body_h - 36, w_px=panel_w - 36, h_px=30,
             font_size_px=8, color=BRAND_ACCENT_SOFT, italic=True)

    add_footer(slide, page_num=262)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "262_multi-line-event-flags.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
