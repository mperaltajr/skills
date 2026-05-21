"""
Builder for pattern 310: Executive metrics dashboard (dark).

KPI row (4 tiles) + bottom zone (chart 65% / alerts 35%).
Legend MOVED from inside chart to BELOW subheadline per mandatory rule.

Source HTML: _pattern-library/310_executive-metrics-dark.html
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
DELTA_UP = RGBColor(0x4A, 0xDE, 0x80)
DELTA_DOWN = RGBColor(0xF8, 0x71, 0x71)
GRID_LINE = RGBColor(0x3A, 0x22, 0x55)
ALERT_RED = RGBColor(0xF8, 0x71, 0x71)
ALERT_AMBER = RGBColor(0xFB, 0xBF, 0x24)
ALERT_GREEN = RGBColor(0x4A, 0xDE, 0x80)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Q2 2026 <strong>Executive Performance Dashboard</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Portfolio-level metrics across all active workstreams — as of May 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Legend BELOW subhead, right-aligned (will reference chart series)
    leg_y = 230
    leg_items = [
        ("Revenue", WHITE, False),
        ("EBITDA", BRAND_ACCENT, False),
        ("NPS Index", BRAND_ACCENT_SOFT, True),
    ]
    leg_widths = [80, 80, 100]
    leg_total = sum(leg_widths) + 12
    cx = 1232 - leg_total
    for i, (lbl, col, dashed) in enumerate(leg_items):
        add_rect(slide, f"legend-{i+1}-line", cx, leg_y + 7, 18, 2, col)
        add_text(slide, f"legend-{i+1}-label", lbl,
                 x_px=cx + 22, y_px=leg_y, w_px=leg_widths[i] - 22, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        cx += leg_widths[i] + 6

    # KPI row (4 tiles) — body shifted down to clear legend
    kpi_y = 270
    kpi_h = 90
    kpis = [
        ("REVENUE (USD)", "$4.2B", "▲ 8.3% vs Q1", DELTA_UP),
        ("EBITDA MARGIN", "23.7%", "▲ 1.2pp YoY", DELTA_UP),
        ("ACTIVE PROJECTS", "148", "▼ 3 vs target", DELTA_DOWN),
        ("NPS SCORE", "71", "▲ +5 vs Q1", DELTA_UP),
    ]
    tile_w = (1184 - 3 * 14) // 4
    for i, (lbl, val, delta, dcol) in enumerate(kpis):
        tx = 48 + i * (tile_w + 14)
        add_rect(slide, f"kpi-{i+1}-bg", tx, kpi_y, tile_w, kpi_h, CARD_BG)
        add_text(slide, f"kpi-{i+1}-label", lbl,
                 x_px=tx + 16, y_px=kpi_y + 12, w_px=tile_w - 32, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=1.2)
        add_text(slide, f"kpi-{i+1}-value", val,
                 x_px=tx + 16, y_px=kpi_y + 30, w_px=tile_w - 32, h_px=42,
                 font_size_px=30, color=WHITE, bold=True)
        add_text(slide, f"kpi-{i+1}-delta", delta,
                 x_px=tx + 16, y_px=kpi_y + 70, w_px=tile_w - 32, h_px=16,
                 font_size_px=11, color=dcol, bold=True)

    # Bottom zone
    bz_top = 376
    bz_bot = 670
    bz_h = bz_bot - bz_top
    chart_w = int((1184 - 14) * 0.65)
    alerts_w = 1184 - 14 - chart_w
    chart_x = 48
    alerts_x = chart_x + chart_w + 14

    # Chart card
    add_rect(slide, "chart-card-bg", chart_x, bz_top, chart_w, bz_h, CARD_BG)
    add_text(slide, "chart-title", "PERFORMANCE TREND — 8-QUARTER VIEW",
             x_px=chart_x + 18, y_px=bz_top + 12, w_px=chart_w - 36, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=1.2)

    # Plot region
    plot_left = chart_x + 24
    plot_right = chart_x + chart_w - 24
    plot_top = bz_top + 36
    plot_bot = bz_bot - 36
    plot_w = plot_right - plot_left
    plot_h = plot_bot - plot_top

    # Grid lines
    for i in range(5):
        gy = plot_top + int(i * plot_h / 4)
        add_rect(slide, f"grid-{i}", plot_left, gy, plot_w, 1, GRID_LINE)

    # X-axis labels
    quarters = ["Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]
    x_step = plot_w / 7.0
    for i, q in enumerate(quarters):
        qx = plot_left + int(i * x_step)
        add_text(slide, f"x-{i}", q,
                 x_px=qx - 24, y_px=plot_bot + 4, w_px=48, h_px=16,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="center")

    # Plot 3 series (already shown above legend BELOW subhead — using same colors)
    # Revenue trend (white) values: indices 7..0 inverted (low to high)
    rev_y = [130, 120, 115, 105, 95, 85, 72, 55]
    ebt_y = [145, 140, 135, 128, 118, 108, 96, 78]
    nps_y = [155, 148, 142, 138, 130, 122, 112, 95]
    # All are in 0-170 svg space; map y_svg ∈ [0,170] → plot_top..plot_bot inverted
    def py(y_svg):
        return plot_top + int((y_svg / 170.0) * plot_h)

    # Revenue (white)
    pts = [(plot_left + int(i * x_step), py(rev_y[i])) for i in range(8)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]; x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for s in range(0, steps, 2):
            t = s / max(1, steps)
            add_rect(slide, f"rev-line-{i}-{s}",
                     int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t),
                     2, 2, WHITE)
    for i, (px_, py_) in enumerate(pts):
        add_rect(slide, f"rev-dot-{i}", px_ - 3, py_ - 3, 6, 6, WHITE)

    # EBITDA (accent purple)
    pts = [(plot_left + int(i * x_step), py(ebt_y[i])) for i in range(8)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]; x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for s in range(0, steps, 2):
            t = s / max(1, steps)
            add_rect(slide, f"ebt-line-{i}-{s}",
                     int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t),
                     2, 2, BRAND_ACCENT)
    for i, (px_, py_) in enumerate(pts):
        add_rect(slide, f"ebt-dot-{i}", px_ - 3, py_ - 3, 6, 6, BRAND_ACCENT)

    # NPS (soft purple dashed)
    pts = [(plot_left + int(i * x_step), py(nps_y[i])) for i in range(8)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]; x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for s in range(0, steps, 6):
            t = s / max(1, steps)
            add_rect(slide, f"nps-line-{i}-{s}",
                     int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t),
                     3, 2, BRAND_ACCENT_SOFT)
    for i, (px_, py_) in enumerate(pts):
        add_rect(slide, f"nps-dot-{i}", px_ - 2, py_ - 2, 5, 5, BRAND_ACCENT_SOFT)

    # Alerts card
    add_rect(slide, "alerts-bg", alerts_x, bz_top, alerts_w, bz_h, CARD_BG)
    add_text(slide, "alerts-title", "ALERTS & FLAGS",
             x_px=alerts_x + 18, y_px=bz_top + 12, w_px=alerts_w - 36, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=1.2)

    alerts = [
        ("APAC delivery milestone at risk — resource shortfall flagged by PMO",
         "Raised 14 May 2026", ALERT_RED),
        ("NA cost run-rate trending 4% above budget; variance review scheduled",
         "Updated 16 May 2026", ALERT_AMBER),
        ("EMEA client NPS recovered to 74 following Q1 remediation actions",
         "Confirmed 19 May 2026", ALERT_GREEN),
    ]
    ay = bz_top + 40
    ah = (bz_h - 50) // 3
    for i, (text, date, col) in enumerate(alerts):
        item_y = ay + i * ah
        add_rect(slide, f"alert-{i+1}-bg", alerts_x + 12, item_y, alerts_w - 24, ah - 8,
                 RGBColor(0x4A, 0x29, 0x76))
        # Left accent bar
        add_rect(slide, f"alert-{i+1}-bar", alerts_x + 12, item_y, 4, ah - 8, col)
        add_text(slide, f"alert-{i+1}-text", text,
                 x_px=alerts_x + 24, y_px=item_y + 10, w_px=alerts_w - 36, h_px=ah - 36,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        add_text(slide, f"alert-{i+1}-date", date,
                 x_px=alerts_x + 24, y_px=item_y + ah - 26, w_px=alerts_w - 36, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT)

    # Footer (invariant zone: only page number)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "310",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "310_executive-metrics-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
