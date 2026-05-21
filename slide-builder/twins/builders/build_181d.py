"""
Builder for pattern 181d: Multi-Modal Dense Exec — DARK variant.

Light source: twins/builders/build_181.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

GREEN = RGBColor(0x4A, 0xDE, 0x80)
RED = RGBColor(0xFB, 0x72, 0x85)
CHART_PLACEHOLDER = RGBColor(0x2A, 0x14, 0x44)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Portfolio Performance Digest — <strong>Q2 2026</strong> Executive Summary",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Cross-stream financials, delivery velocity, and strategic inflection signals — one-slide view",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    body_bottom = 720 - 64
    body_left = 48
    body_w = 1280 - 96
    body_h = body_bottom - body_top

    zone1_w = int(body_w * 0.38)
    zone2_w = int(body_w * 0.32)
    zone3_w = body_w - zone1_w - zone2_w

    z1_x = body_left
    z1 = add_rect(slide, "zone-1-bg", z1_x, body_top, zone1_w, body_h, CARD_BG_DARK)
    z1.line.color.rgb = CARD_BORDER_DARK
    z1.line.width = 9525
    add_text(slide, "zone-1-header", "FINANCIAL & DELIVERY SCORECARD",
             z1_x + 14, body_top + 12, zone1_w - 28, 18,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "zone-1-header-rule", z1_x + 14, body_top + 36, zone1_w - 28, 1, CARD_BORDER_DARK)

    th_y = body_top + 44
    th_w = zone1_w - 28
    col1_w = int(th_w * 0.30)
    col2_w = int(th_w * 0.22)
    col3_w = int(th_w * 0.22)
    col4_w = th_w - col1_w - col2_w - col3_w
    add_text(slide, "th-stream", "Stream", z1_x + 14, th_y, col1_w, 14,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, uppercase=True)
    add_text(slide, "th-budget", "Budget ($M)", z1_x + 14 + col1_w, th_y, col2_w, 14,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, align="right", uppercase=True)
    add_text(slide, "th-actual", "Actual ($M)", z1_x + 14 + col1_w + col2_w, th_y, col3_w, 14,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, align="right", uppercase=True)
    add_text(slide, "th-delta", "Δ vs Plan", z1_x + 14 + col1_w + col2_w + col3_w, th_y, col4_w, 14,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, align="right", uppercase=True)
    add_rect(slide, "th-rule", z1_x + 14, th_y + 18, th_w, 2, CARD_BORDER_DARK)

    rows = [
        ("Cloud Infra", "42.0", "38.7", "+8.3%", GREEN, False),
        ("Data & AI", "31.5", "33.9", "−7.6%", RED, False),
        ("Cyber", "18.0", "16.4", "+8.9%", GREEN, False),
        ("Total Portfolio", "91.5", "89.0", "−2.7%", WHITE, True),
    ]
    row_y = th_y + 24
    row_h = 28
    for i, (name, budget, actual, delta, dcolor, is_total) in enumerate(rows):
        n = i + 1
        if is_total:
            add_rect(slide, f"row-{n}-bg", z1_x + 14, row_y, th_w, row_h, BRAND_ACCENT)
            txt_color = WHITE
            bold = True
        else:
            txt_color = WHITE
            bold = False
        add_text(slide, f"row-{n}-stream", name, z1_x + 14 + 4, row_y, col1_w - 4, row_h,
                 font_size_px=11, color=txt_color, bold=bold, anchor="middle")
        add_text(slide, f"row-{n}-budget", budget, z1_x + 14 + col1_w, row_y, col2_w - 4, row_h,
                 font_size_px=11, color=txt_color, bold=bold, align="right", anchor="middle")
        add_text(slide, f"row-{n}-actual", actual, z1_x + 14 + col1_w + col2_w, row_y, col3_w - 4, row_h,
                 font_size_px=11, color=txt_color, bold=bold, align="right", anchor="middle")
        add_text(slide, f"row-{n}-delta", delta, z1_x + 14 + col1_w + col2_w + col3_w, row_y,
                 col4_w - 4, row_h,
                 font_size_px=10, color=(txt_color if is_total else dcolor), bold=True,
                 align="right", anchor="middle")
        if not is_total:
            add_rect(slide, f"row-{n}-rule", z1_x + 14, row_y + row_h, th_w, 1, CARD_BORDER_DARK)
        row_y += row_h

    add_text(slide, "table-footnote",
             "Budget = approved Q2 baseline · Actuals as of 2026-05-16",
             z1_x + 14, body_top + body_h - 26, th_w, 14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, italic=True)

    z2_x = z1_x + zone1_w
    z2 = add_rect(slide, "zone-2-bg", z2_x, body_top, zone2_w, body_h, CARD_BG_DARK)
    z2.line.color.rgb = CARD_BORDER_DARK
    z2.line.width = 9525
    add_text(slide, "zone-2-header", "BUDGET VS ACTUAL ($M)",
             z2_x + 14, body_top + 12, zone2_w - 28, 18,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "zone-2-header-rule", z2_x + 14, body_top + 36, zone2_w - 28, 1, CARD_BORDER_DARK)
    leg_y = body_top + 44
    add_rect(slide, "chart-legend-1-swatch", z2_x + 14, leg_y + 3, 8, 8, BRAND_ACCENT_SOFT)
    add_text(slide, "chart-legend-1-label", "Budget", z2_x + 26, leg_y, 60, 12,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True)
    add_rect(slide, "chart-legend-2-swatch", z2_x + 84, leg_y + 3, 8, 8, BRAND_ACCENT)
    add_text(slide, "chart-legend-2-label", "Actual", z2_x + 96, leg_y, 60, 12,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True)
    chart_x = z2_x + 14
    chart_y = leg_y + 24
    chart_w = zone2_w - 28
    chart_h = body_h - 90
    add_rect(slide, "chart-canvas", chart_x, chart_y, chart_w, chart_h, CHART_PLACEHOLDER)

    # Simple grouped bar chart inside the canvas (Budget vs Actual per stream).
    bars = [
        ("Cloud", 42.0, 38.7),
        ("D&AI", 31.5, 33.9),
        ("Cyber", 18.0, 16.4),
    ]
    max_val = 45.0
    plot_left = chart_x + 36
    plot_right = chart_x + chart_w - 16
    plot_top = chart_y + 16
    plot_bot = chart_y + chart_h - 28
    plot_w = plot_right - plot_left
    plot_h = plot_bot - plot_top

    # Gridlines
    for i in range(4):
        gy = plot_top + int(i * plot_h / 3)
        add_rect(slide, f"chart-grid-{i}", plot_left, gy, plot_w, 1, CARD_BORDER_DARK)

    group_w = plot_w // len(bars)
    bar_w = 18
    bar_gap = 4
    for i, (lbl, budget, actual) in enumerate(bars):
        gx = plot_left + i * group_w + (group_w - 2 * bar_w - bar_gap) // 2
        # Budget bar
        bh = int(budget / max_val * plot_h)
        add_rect(slide, f"chart-bar-{i+1}-budget", gx, plot_bot - bh, bar_w, bh, BRAND_ACCENT_SOFT)
        # Actual bar
        ah = int(actual / max_val * plot_h)
        add_rect(slide, f"chart-bar-{i+1}-actual", gx + bar_w + bar_gap, plot_bot - ah,
                 bar_w, ah, BRAND_ACCENT)
        # X label
        add_text(slide, f"chart-bar-{i+1}-label", lbl,
                 x_px=plot_left + i * group_w, y_px=plot_bot + 4,
                 w_px=group_w, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="center")

    z3_x = z2_x + zone2_w
    z3 = add_rect(slide, "zone-3-bg", z3_x, body_top, zone3_w, body_h, CARD_BG_DARK)
    z3.line.color.rgb = CARD_BORDER_DARK
    z3.line.width = 9525
    add_text(slide, "zone-3-header", "KEY FINDINGS",
             z3_x + 14, body_top + 12, zone3_w - 28, 18,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "zone-3-header-rule", z3_x + 14, body_top + 36, zone3_w - 28, 1, CARD_BORDER_DARK)

    insights = [
        "<strong>Cloud Infra</strong> running 8% under budget — unspent capacity signals delivery slowdown or scope deferral requiring PMO review before Q3.",
        "<strong>Data & AI overrun</strong> of $2.4M driven by vendor escalations; mitigation plan due by 30 May with executive sign-off.",
        "<strong>Cyber</strong> tracking favorably; savings of $1.6M available for reallocation to offset Data & AI exposure.",
    ]
    iy = body_top + 50
    for i, text in enumerate(insights):
        n = i + 1
        add_rect(slide, f"insight-{n}-marker", z3_x + 14, iy + 6, 5, 5, BRAND_ACCENT_SOFT)
        add_text(slide, f"insight-{n}", text,
                 z3_x + 26, iy, zone3_w - 40, 54,
                 font_size_px=11, color=TEXT_ON_DARK_MID, emphasis_color=WHITE)
        iy += 52

    cb_y = body_top + body_h - 90
    add_rect(slide, "callout-bg", z3_x + 14, cb_y, zone3_w - 28, 80, BRAND_ACCENT)
    add_text(slide, "callout-label", "NET PORTFOLIO VARIANCE",
             z3_x + 24, cb_y + 10, zone3_w - 48, 14,
             font_size_px=9, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "callout-value", "−$2.5M",
             z3_x + 24, cb_y + 24, zone3_w - 48, 36,
             font_size_px=30, color=WHITE, bold=True)
    add_text(slide, "callout-sub", "vs $91.5M baseline · within 3% tolerance threshold · escalation not yet required",
             z3_x + 24, cb_y + 60, zone3_w - 48, 18,
             font_size_px=9, color=WHITE)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "181",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "181d_multi-modal-dense-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
