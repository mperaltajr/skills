"""
Builder for pattern 69d: Tornado sensitivity (dark variant).

Source HTML: _pattern-library/69_tornado-sensitivity-dark.html
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
ANNOT_BG = RGBColor(0x1A, 0x05, 0x30)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Cycle-time sensitivity — storyline coaching is the biggest lever.",
        x_px=64, y_px=20, w_px=1100, h_px=80,
        font_size_px=27, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Six factors move cycle time; one moves it almost twice as much as the next.",
        x_px=64, y_px=108, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 80 - 56
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    annot_w = 280
    gap = 18
    chart_w = g_w - annot_w - gap

    cp = add_rect(slide, "chart-panel-bg", g_left, g_top, chart_w, g_h, CARD_BG_DARK)
    cp.line.color.rgb = CARD_BORDER_DARK
    cp.line.width = 9525

    add_text(
        slide, "chart-title", "DAYS VS. 14-DAY BASELINE",
        x_px=g_left + 20, y_px=g_top + 14, w_px=400, h_px=16,
        font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    leg_y = g_top + 14
    leg2_label_w = 130
    leg2_sw = 10
    leg2_gap = 6
    leg2_right = g_left + chart_w - 12
    leg2_x = leg2_right - leg2_label_w
    leg1_label_w = 120
    leg1_sw = 10
    leg1_x = leg2_x - leg1_label_w - leg1_sw - leg2_gap - 22
    add_rect(slide, "legend-1-swatch", leg1_x, leg_y + 3, leg1_sw, leg1_sw, BRAND_ACCENT_SOFT)
    add_text(
        slide, "legend-1-label", "Reduces cycle time",
        x_px=leg1_x + leg1_sw + 4, y_px=leg_y, w_px=leg1_label_w, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_MID,
    )
    add_rect(slide, "legend-2-swatch", leg2_x - leg2_sw - 4, leg_y + 3, leg2_sw, leg2_sw, BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "Increases cycle time",
        x_px=leg2_x, y_px=leg_y, w_px=leg2_label_w, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_MID,
    )

    chart_canvas_y = g_top + 58
    chart_canvas_h = g_h - 68
    canvas_x = g_left + 12
    canvas_w = chart_w - 24

    plot_left = canvas_x + 160
    plot_right = canvas_x + canvas_w - 20
    plot_w = plot_right - plot_left
    centerline_x = plot_left + plot_w // 2
    unit_px = plot_w / 12.0

    add_rect(slide, "chart-baseline-axis",
             centerline_x, chart_canvas_y, 2, chart_canvas_h - 30, BRAND_ACCENT_SOFT)

    tick_y = chart_canvas_y + chart_canvas_h - 22
    ticks = ["-6d", "-4d", "-2d", "0", "+2d", "+4d", "+6d"]
    for i, tx in enumerate(ticks):
        n = i + 1
        x_px = plot_left + int(i * 2 * unit_px) - 12
        add_text(
            slide, f"chart-tick-{n}-label", tx,
            x_px=x_px, y_px=tick_y, w_px=30, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_MID, align="center",
        )

    add_text(
        slide, "chart-axis-label", "Change vs. baseline (days)",
        x_px=plot_left, y_px=tick_y + 16, w_px=plot_w, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_MID, italic=True, align="center",
    )

    add_text(
        slide, "chart-subtitle", "Baseline: 14 days",
        x_px=plot_left - 16, y_px=tick_y + 16, w_px=160, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_MID, bold=True,
    )

    rows = [
        ("Storyline session present", -6, 0),
        ("Pattern library size", -3, 1),
        ("Reviewer count", 0, 4),
        ("Partner pre-read", -2, 2),
        ("Junior on team", 0, 2),
        ("Brand template complexity", 0, 1),
    ]
    bars_top = chart_canvas_y + 18
    bars_h = chart_canvas_h - 60
    row_h = bars_h // 6
    bar_h = 22

    for ri, (label, neg, pos) in enumerate(rows):
        n = ri + 1
        ry = bars_top + ri * row_h
        bar_y = ry + (row_h - bar_h) // 2

        add_text(
            slide, f"bar-{n}-label", label,
            x_px=canvas_x + 6, y_px=ry + (row_h - 16) // 2, w_px=plot_left - canvas_x - 12,
            h_px=18, font_size_px=10, color=WHITE, bold=True, align="right",
        )

        if neg < 0:
            nw = int(abs(neg) * unit_px)
            add_rect(slide, f"bar-{n}-neg-bar",
                     centerline_x - nw, bar_y, nw, bar_h, BRAND_ACCENT_SOFT)
            add_text(
                slide, f"bar-{n}-neg-val", f"{neg}d",
                x_px=centerline_x - nw - 36, y_px=bar_y + 2, w_px=32, h_px=18,
                font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="right",
            )
        if pos > 0:
            pw = int(pos * unit_px)
            add_rect(slide, f"bar-{n}-pos-bar",
                     centerline_x, bar_y, pw, bar_h, BRAND_ACCENT)
            add_text(
                slide, f"bar-{n}-pos-val", f"+{pos}d",
                x_px=centerline_x + pw + 4, y_px=bar_y + 2, w_px=36, h_px=18,
                font_size_px=10, color=BRAND_ACCENT, bold=True,
            )

    ap_x = g_left + chart_w + gap
    add_rect(slide, "annot-bg", ap_x, g_top, annot_w, g_h, ANNOT_BG)
    add_text(
        slide, "annot-header", "TOP 3 SENSITIVITIES",
        x_px=ap_x + 18, y_px=g_top + 22, w_px=annot_w - 36, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "annot-sub", "Where to invest first — and where not to bother.",
        x_px=ap_x + 18, y_px=g_top + 42, w_px=annot_w - 36, h_px=40,
        font_size_px=14, color=WHITE, bold=True,
    )

    items = [
        ("Storyline session present (-6d)",
         "Single biggest lever. Coaching upstream prevents 60% of rework cycles downstream."),
        ("Reviewer count (+4d)",
         "Each extra reviewer adds ~1.3 days. Cap at two for non-exec decks."),
        ("Pattern library size (-3d)",
         "Doubling the library cuts build time by a fifth. Keep investing in skeletons."),
    ]
    list_top = g_top + 100
    item_h = (g_h - 110) // 3
    for ai, (label, body) in enumerate(items):
        an = ai + 1
        ay = list_top + ai * item_h
        add_text(
            slide, f"annot-{an}-marker", str(an),
            x_px=ap_x + 18, y_px=ay, w_px=20, h_px=20,
            font_size_px=11, color=WHITE, bold=True, align="center",
            bg_fill=BRAND_ACCENT, padding_px=(0, 0, 0, 0),
        )
        add_text(
            slide, f"annot-{an}-label", label,
            x_px=ap_x + 44, y_px=ay - 2, w_px=annot_w - 60, h_px=18,
            font_size_px=12, color=WHITE, bold=True,
        )
        add_text(
            slide, f"annot-{an}-body", body,
            x_px=ap_x + 44, y_px=ay + 18, w_px=annot_w - 60, h_px=item_h - 24,
            font_size_px=11, color=BRAND_ACCENT_SOFT,
        )

    cv_y = g_bottom + 6
    cv_h = 36
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, ANNOT_BG)
    add_rect(slide, "convergence-accent", g_left, cv_y, 3, cv_h, BRAND_ACCENT_SOFT)
    add_text(
        slide, "convergence",
        "Invest in storyline coaching first — it moves the needle twice as much as anything else on the list.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "69",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "69d_tornado-sensitivity.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
