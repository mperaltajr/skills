"""
Builder for pattern 105d: Time series with confidence band — dark variant.

Source HTML: _pattern-library/105_time-series-confidence-band-dark.html
Light template: twins/builders/build_105.py
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

    add_text(slide, "title",
             "<strong>ARR on track</strong> — forecast band narrows as pipeline converts",
             x_px=64, y_px=20, w_px=1000, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Projected ARR, Q1 2024 - Q4 2025 - $M - Central trend, 80% confidence band, actuals vs. forecast",
             x_px=64, y_px=108, w_px=880, h_px=24,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 134, 56, 3, BRAND_ACCENT_SOFT)

    # Legend
    leg_y = 240
    leg_items = [
        ("Actuals", BRAND_ACCENT),
        ("Forecast", BRAND_ACCENT_SOFT),
        ("80% confidence band", BRAND_ACCENT_SOFT),
    ]
    leg_x = 1240 - 360
    for i, (label, color) in enumerate(leg_items):
        n = i + 1
        x = leg_x + i * 120
        add_rect(slide, f"legend-{n}-swatch", x, leg_y + 6, 16, 8, color)
        add_text(slide, f"legend-{n}-label", label,
                 x_px=x + 22, y_px=leg_y, w_px=98, h_px=16,
                 font_size_px=10, color=TEXT_ON_DARK_MID, bold=True)

    # Chart canvas + minimal axes/gridlines so it reads as a chart, not a flat slab.
    chart_x, chart_y, chart_w, chart_h = 80, 268, 1280 - 80 - 48, 720 - 268 - 100
    add_rect(slide, "chart-canvas", chart_x, chart_y, chart_w, chart_h, CARD_BG_DARK)

    plot_left = chart_x + 56
    plot_right = chart_x + chart_w - 24
    plot_top = chart_y + 20
    plot_bot = chart_y + chart_h - 28
    plot_w = plot_right - plot_left
    plot_h = plot_bot - plot_top

    # Horizontal gridlines + y-axis labels
    y_labels = ["$120M", "$100M", "$80M", "$60M", "$40M"]
    for i, lbl in enumerate(y_labels):
        gy = plot_top + int(i * plot_h / (len(y_labels) - 1))
        add_rect(slide, f"chart-grid-{i}", plot_left, gy, plot_w, 1, CARD_BORDER_DARK)
        add_text(slide, f"chart-y-{i}", lbl,
                 x_px=chart_x + 8, y_px=gy - 8, w_px=44, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="right")

    # Confidence band (semi-transparent stand-in — drawn as soft accent)
    band_pts_top = [70, 65, 60, 55, 48, 40, 32, 22]
    band_pts_bot = [85, 82, 78, 73, 68, 62, 55, 48]
    x_step = plot_w / (len(band_pts_top) - 1)

    def _py(svg_y):
        return plot_top + int((svg_y / 100.0) * plot_h)

    # Approximate band fill as a series of thin verticals
    for i in range(len(band_pts_top) - 1):
        x1 = plot_left + int(i * x_step)
        x2 = plot_left + int((i + 1) * x_step)
        for px in range(x1, x2, 3):
            t = (px - x1) / max(1, x2 - x1)
            yt = band_pts_top[i] + (band_pts_top[i + 1] - band_pts_top[i]) * t
            yb = band_pts_bot[i] + (band_pts_bot[i + 1] - band_pts_bot[i]) * t
            top_y = _py(yt)
            h = _py(yb) - top_y
            add_rect(slide, f"chart-band-{i}-{px}", px, top_y, 3, h, BRAND_ACCENT_SOFT)

    # Central forecast line (mid of band)
    line_pts = [(band_pts_top[i] + band_pts_bot[i]) // 2 for i in range(len(band_pts_top))]
    for i in range(len(line_pts) - 1):
        x1 = plot_left + int(i * x_step)
        x2 = plot_left + int((i + 1) * x_step)
        y1 = _py(line_pts[i])
        y2 = _py(line_pts[i + 1])
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for s in range(0, steps, 2):
            t = s / max(1, steps)
            add_rect(slide, f"chart-line-{i}-{s}",
                     int(x1 + (x2 - x1) * t),
                     int(y1 + (y2 - y1) * t),
                     2, 2, BRAND_ACCENT)

    # Actuals dots (first 4 quarters)
    for i in range(4):
        ax = plot_left + int(i * x_step)
        ay = _py(line_pts[i] + 4)
        add_rect(slide, f"chart-actual-{i}", ax - 3, ay - 3, 7, 7, WHITE)

    # X-axis labels
    quarters = ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"]
    for i, q in enumerate(quarters):
        qx = plot_left + int(i * x_step)
        add_text(slide, f"chart-x-{i}", q,
                 x_px=qx - 24, y_px=plot_bot + 6, w_px=48, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="center")

    # Convergence
    conv_y = 720 - 56 - 44
    conv_h = 44
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence",
             "Band narrows from +/-$16M today to +/-$12M by Q4 2025 as late-stage deals convert "
             "— Q3 forecast range is tight enough to commit to board guidance.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=conv_h,
             font_size_px=14, color=WHITE, italic=True, anchor="middle",
             padding_px=(0, 22, 0, 22))

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "105",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "105d_time-series-confidence-band-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
