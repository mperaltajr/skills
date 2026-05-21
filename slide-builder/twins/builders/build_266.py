"""
Builder for pattern 266: Dual-axis line chart (dark).

Legend MOVED below subheadline per mandatory rule (right side has a 28%-width
content panel — under 30% threshold — so default placement applies).

Source HTML: _pattern-library/266_dual-axis-line-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
NPS_GREEN = RGBColor(0x38, 0xA1, 0x69)
GRID_LINE = RGBColor(0x45, 0x2A, 0x68)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title — canonical chrome
    add_text(slide, "title",
             "Revenue growth and <strong>NPS improvement</strong> are strongly correlated",
             x_px=40, y_px=20, w_px=1200, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Q1 2025 – Q4 2026 · Eight-quarter trend · Pearson r = 0.94",
             x_px=40, y_px=108, w_px=1200, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 40, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Legend below subhead, right-aligned
    leg_y = 230
    leg_items = [
        ("Revenue $M (left axis)", BRAND_ACCENT_SOFT, False),
        ("NPS Score (right axis)", NPS_GREEN, True),
    ]
    leg_widths = [180, 170]
    leg_total = sum(leg_widths) + 24
    cx = 1232 - leg_total
    for i, (lbl, col, dashed) in enumerate(leg_items):
        # Line swatch
        add_rect(slide, f"legend-{i+1}-line", cx, leg_y + 7, 22, 2, col)
        # Dot
        add_rect(slide, f"legend-{i+1}-dot", cx + 28, leg_y + 5, 6, 6, col)
        add_text(slide, f"legend-{i+1}-label", lbl,
                 x_px=cx + 40, y_px=leg_y, w_px=leg_widths[i] - 40, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        cx += leg_widths[i] + 24

    # Body
    body_top = 260
    body_bot = 670
    chart_x = 40
    chart_w = 820
    side_x = 880
    side_w = 360

    # Chart area
    plot_left = chart_x + 50
    plot_right = chart_x + chart_w - 50
    plot_top = body_top + 10
    plot_bot = body_bot - 40
    plot_w = plot_right - plot_left
    plot_h = plot_bot - plot_top

    # Gridlines (6 horizontal)
    for i in range(7):
        gy = plot_top + int(i * plot_h / 6)
        op = 0.3 if i == 6 else 0.07
        col = GRID_LINE if i == 6 else RGBColor(0x3A, 0x22, 0x55)
        add_rect(slide, f"grid-{i}", plot_left, gy, plot_w, 1, col)

    # Y-axis lines
    add_rect(slide, "y-axis-left", plot_left, plot_top, 1, plot_h, GRID_LINE)
    add_rect(slide, "y-axis-right", plot_right, plot_top, 1, plot_h, GRID_LINE)

    # Left Y labels (Revenue $M, 0 to 600)
    rev_labels = ["0", "100", "200", "300", "400", "500", "600"]
    for i, lbl in enumerate(rev_labels):
        ly = plot_bot - int(i * plot_h / 6) - 8
        add_text(slide, f"y-left-{i}", lbl,
                 x_px=chart_x, y_px=ly, w_px=44, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, align="right")
    add_text(slide, "y-left-title", "Revenue $M",
             x_px=chart_x, y_px=plot_top - 14, w_px=80, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True)

    # Right Y labels (NPS 0 to 80)
    nps_labels = ["0", "20", "40", "60", "80"]
    for i, lbl in enumerate(nps_labels):
        ly = plot_bot - int(i * plot_h / 4) - 8
        add_text(slide, f"y-right-{i}", lbl,
                 x_px=plot_right + 6, y_px=ly, w_px=30, h_px=14,
                 font_size_px=9, color=NPS_GREEN)
    add_text(slide, "y-right-title", "NPS Score",
             x_px=plot_right - 20, y_px=plot_top - 14, w_px=80, h_px=14,
             font_size_px=9, color=NPS_GREEN, bold=True, align="right")

    # X-axis labels (8 quarters)
    quarters = ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26", "Q3'26", "Q4'26"]
    x_step = plot_w / 7.0
    for i, q in enumerate(quarters):
        qx = plot_left + int(i * x_step)
        add_text(slide, f"x-{i}", q,
                 x_px=qx - 24, y_px=plot_bot + 6, w_px=48, h_px=16,
                 font_size_px=9, color=TEXT_ON_DARK_MID, align="center")

    # Alignment zone (cols 3-5, Q4'25-Q2'26)
    az_x1 = plot_left + int(2.7 * x_step)
    az_x2 = plot_left + int(5.3 * x_step)
    add_rect(slide, "alignment-zone", az_x1, plot_top + 20, az_x2 - az_x1, plot_h - 40,
             RGBColor(0x4E, 0x1A, 0x7A))
    add_text(slide, "alignment-label", "Alignment zone",
             x_px=az_x1, y_px=plot_top + 6, w_px=az_x2 - az_x1, h_px=14,
             font_size_px=10, color=WHITE, bold=True, align="center")

    # Revenue data (0-600 scale)
    rev_vals = [320, 345, 380, 415, 440, 468, 491, 520]
    # NPS data (0-80 scale)
    nps_vals = [42, 44, 48, 51, 55, 58, 61, 65]

    def rev_y(v):
        return plot_bot - int((v / 600.0) * plot_h)

    def nps_y(v):
        return plot_bot - int((v / 80.0) * plot_h)

    # Revenue line segments
    pts_rev = [(plot_left + int(i * x_step), rev_y(v)) for i, v in enumerate(rev_vals)]
    for i in range(len(pts_rev) - 1):
        x1, y1 = pts_rev[i]
        x2, y2 = pts_rev[i + 1]
        # approximate line via thin rect — use small rotated rect alternative:
        # Use polyline-equivalent: draw a 2px tall rect rotated; simpler: skip line, use dots.
        # Use connect via mini-rect along path: use multiple small rects.
        # For simplicity, approximate with a 2px rect oriented horizontally between dots.
        # If diagonal, approximate as series of stepped 1px rects.
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps > 0:
            for s in range(0, steps, 2):
                t = s / steps
                px = int(x1 + (x2 - x1) * t)
                py = int(y1 + (y2 - y1) * t)
                add_rect(slide, f"rev-line-{i}-{s}", px, py, 2, 2, BRAND_ACCENT_SOFT)

    # Revenue dots
    for i, (px, py) in enumerate(pts_rev):
        add_rect(slide, f"rev-dot-{i}", px - 3, py - 3, 6, 6, BRAND_ACCENT_SOFT)

    # NPS line (dashed approximation)
    pts_nps = [(plot_left + int(i * x_step), nps_y(v)) for i, v in enumerate(nps_vals)]
    for i in range(len(pts_nps) - 1):
        x1, y1 = pts_nps[i]
        x2, y2 = pts_nps[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps > 0:
            for s in range(0, steps, 6):
                t = s / steps
                px = int(x1 + (x2 - x1) * t)
                py = int(y1 + (y2 - y1) * t)
                add_rect(slide, f"nps-line-{i}-{s}", px, py, 3, 2, NPS_GREEN)

    for i, (px, py) in enumerate(pts_nps):
        add_rect(slide, f"nps-dot-{i}", px - 3, py - 3, 6, 6, NPS_GREEN)

    # ---- Right panel ----
    add_text(slide, "section-label", "KEY CORRELATION",
             x_px=side_x, y_px=body_top, w_px=side_w, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=2)

    # Stat card
    sc_y = body_top + 26
    sc_h = 90
    add_rect(slide, "stat-card-bg", side_x, sc_y, side_w, sc_h, CARD_BG)
    add_text(slide, "stat-number", "r = 0.94",
             x_px=side_x + 18, y_px=sc_y + 14, w_px=side_w - 36, h_px=44,
             font_size_px=36, color=BRAND_ACCENT_SOFT, bold=True)
    add_text(slide, "stat-label", "PEARSON CORRELATION · Q1 2025 – Q4 2026",
             x_px=side_x + 18, y_px=sc_y + 60, w_px=side_w - 36, h_px=18,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=1.2)

    # Insight card
    ic_y = sc_y + sc_h + 14
    ic_h = 200
    add_rect(slide, "insight-card-bg", side_x, ic_y, side_w, ic_h, CARD_BG)
    add_text(slide, "insight-1",
             "• Revenue grew +62% ($320M → $520M) as NPS climbed 23 points — the two curves move in near-lockstep.",
             x_px=side_x + 16, y_px=ic_y + 14, w_px=side_w - 32, h_px=90,
             font_size_px=11, color=TEXT_ON_DARK_MID)
    add_text(slide, "insight-2",
             "• The Alignment zone (Q4'25 – Q2'26) marks the inflection: both metrics steepened after CX programme deployment.",
             x_px=side_x + 16, y_px=ic_y + 110, w_px=side_w - 32, h_px=84,
             font_size_px=11, color=TEXT_ON_DARK_MID)

    # Source
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source",
             "Source: Finance BI dashboard v4.2 & Customer Insights survey (n ≈ 2,400/quarter).",
             x_px=side_x, y_px=ic_y + ic_h + 14, w_px=side_w, h_px=30,
             font_size_px=8, color=TEXT_ON_DARK_FAINT)

    # Footer
    add_text(slide, "page-number", "266",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "266_dual-axis-line-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
