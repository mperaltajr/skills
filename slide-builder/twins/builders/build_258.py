"""
Builder for pattern 258: Diverging bar chart — net sentiment by category.

Source HTML: _pattern-library/258_diverging-bar-chart.html

Layout: title + diverging horizontal bars (8 rows, positive right, negative left)
on the left, insight panel with overall net score on the right.

LEGEND PLACEMENT: Right-aligned below subheadline (top-y ≥ 230, right edge ≈ 1240).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

POS_FULL = RGBColor(0xA1, 0x00, 0xFF)
POS_MID = RGBColor(0xB0, 0x30, 0xFF)
POS_SOFT = RGBColor(0xC7, 0x80, 0xFF)
POS_LITE = RGBColor(0xD4, 0x9F, 0xFF)

NEG_LITE = RGBColor(0xFC, 0x81, 0x81)
NEG_MID = RGBColor(0xF5, 0x65, 0x65)
NEG_STRONG = RGBColor(0xE5, 0x3E, 0x3E)
NEG_FULL = RGBColor(0xC5, 0x30, 0x30)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Customer perception is split — <strong>billing and returns drag the net score to near-zero.</strong>",
        subtitle="Net sentiment by category (n=1,240 responses). Positive = net promoter; Negative = net detractor.",
    )

    # === LEGEND — below subheadline, right-aligned ===
    leg_y = 230
    leg_h = 22
    leg_w = 340
    leg_x = 1240 - leg_w
    add_rect(slide, "legend-pos-swatch", leg_x, leg_y + 7, 10, 10, POS_FULL)
    add_text(
        slide, "legend-pos-label", "Positive perception",
        x_px=leg_x + 16, y_px=leg_y + 2, w_px=140, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )
    add_rect(slide, "legend-neg-swatch", leg_x + 170, leg_y + 7, 10, 10, NEG_STRONG)
    add_text(
        slide, "legend-neg-label", "Negative perception",
        x_px=leg_x + 186, y_px=leg_y + 2, w_px=160, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )

    # === Body ===
    body_top = 268
    body_bottom = 635
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    chart_w = int(body_w * 0.66)
    gap = 18
    panel_w = body_w - chart_w - gap

    # Chart container
    chart_x = left_x
    chart_y = body_top
    chart_bg = add_rect(slide, "chart-panel", chart_x, chart_y, chart_w, body_h, CARD_BG)
    chart_bg.line.color.rgb = CARD_BORDER
    chart_bg.line.width = 9525

    # Chart title
    add_text(
        slide, "chart-title", "NET SENTIMENT SCORE PER CATEGORY",
        x_px=chart_x + 16, y_px=chart_y + 10, w_px=chart_w - 32, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )

    # Plot area
    plot_top = chart_y + 32
    plot_bottom = chart_y + body_h - 26
    plot_h = plot_bottom - plot_top
    plot_left = chart_x + 30
    plot_right = chart_x + chart_w - 30
    plot_w = plot_right - plot_left
    center_x = plot_left + plot_w // 2
    # scale: range -50..+50, so each unit = (plot_w/2)/50
    unit = (plot_w / 2) / 50

    # zero axis line
    add_rect(slide, "zero-axis", center_x, plot_top, 1, plot_h, TEXT_MID)
    # gridlines at -50, -25, +25, +50
    for v in (-50, -25, 25, 50):
        gx = int(center_x + v * unit)
        add_rect(slide, f"grid-{v}", gx, plot_top, 1, plot_h, CARD_BORDER)
    # tick labels
    for v in (-50, -25, 0, 25, 50):
        gx = int(center_x + v * unit)
        sign = "+" if v > 0 else ""
        add_text(
            slide, f"tick-{v}", f"{sign}{v}",
            x_px=gx - 16, y_px=plot_bottom + 2, w_px=32, h_px=14,
            font_size_px=9, color=TEXT_FAINT, align="center",
        )

    # 8 rows
    rows = [
        ("Customer Satisfaction", 42, POS_FULL),
        ("Product Quality", 38, POS_MID),
        ("Price Value", 12, POS_SOFT),
        ("Delivery Speed", 8, POS_LITE),
        ("Brand Trust", -5, NEG_LITE),
        ("Support Quality", -18, NEG_MID),
        ("Return Process", -31, NEG_STRONG),
        ("Billing Clarity", -44, NEG_FULL),
    ]
    n_rows = len(rows)
    row_h = plot_h // n_rows
    bar_h = 14
    for i, (name, val, color) in enumerate(rows):
        n = i + 1
        ry_center = plot_top + i * row_h + row_h // 2
        # category label centered above
        add_text(
            slide, f"cat-{n}-label", name,
            x_px=center_x - 90, y_px=ry_center - row_h // 2 + 2, w_px=180, h_px=12,
            font_size_px=9, color=TEXT_DARK, align="center", bold=True,
        )
        bar_w_px = abs(int(val * unit))
        bar_y = ry_center - bar_h // 2 + 4
        if val >= 0:
            bar_x = center_x
            add_rect(slide, f"bar-{n}-pos", bar_x, bar_y, bar_w_px, bar_h, color)
            add_text(
                slide, f"val-{n}-pos", f"+{val}",
                x_px=bar_x + bar_w_px + 4, y_px=bar_y - 2, w_px=36, h_px=bar_h + 4,
                font_size_px=9, color=TEXT_DARK, bold=True, anchor="middle",
            )
        else:
            bar_x = center_x - bar_w_px
            add_rect(slide, f"bar-{n}-neg", bar_x, bar_y, bar_w_px, bar_h, color)
            add_text(
                slide, f"val-{n}-neg", f"{val}",
                x_px=bar_x - 38, y_px=bar_y - 2, w_px=34, h_px=bar_h + 4,
                font_size_px=9, color=NEG_FULL, bold=True, align="right", anchor="middle",
            )

    # Right insight panel
    pn_x = chart_x + chart_w + gap
    pn_y = body_top
    add_rect(slide, "insight-panel", pn_x, pn_y, panel_w, body_h, CARD_BG)
    panel_outer = slide.shapes[-1]
    panel_outer.line.color.rgb = CARD_BORDER
    panel_outer.line.width = 9525

    add_text(
        slide, "panel-eyebrow", "OVERALL NET SCORE",
        x_px=pn_x + 16, y_px=pn_y + 14, w_px=panel_w - 32, h_px=14,
        font_size_px=9, color=TEXT_MID, bold=True,
        letter_spacing_px=1.4, uppercase=True,
    )
    add_text(
        slide, "net-score-value", "+2 pts",
        x_px=pn_x + 16, y_px=pn_y + 32, w_px=panel_w - 32, h_px=44,
        font_size_px=32, color=BRAND_ACCENT, bold=True,
    )
    add_text(
        slide, "net-score-label", "Aggregate net sentiment (sum of all 8 categories ÷ 8)",
        x_px=pn_x + 16, y_px=pn_y + 80, w_px=panel_w - 32, h_px=30,
        font_size_px=10, color=TEXT_MID, italic=True,
    )
    add_text(
        slide, "insights-label", "KEY INSIGHTS",
        x_px=pn_x + 16, y_px=pn_y + 120, w_px=panel_w - 32, h_px=14,
        font_size_px=9, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=1.4, uppercase=True,
    )
    insights = [
        ("Product strength is real but narrow", "Top 2 categories (Satisfaction +42, Quality +38) carry the score; without them the net would be –38."),
        ("Billing & returns destroy value", "Billing Clarity (–44) and Return Process (–31) together erase nearly all positive sentiment. Fix these first."),
    ]
    iy = pn_y + 144
    for i, (head, body) in enumerate(insights):
        n = i + 1
        add_text(
            slide, f"insight-{n}-heading", head,
            x_px=pn_x + 16, y_px=iy, w_px=panel_w - 32, h_px=16,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"insight-{n}-body", body,
            x_px=pn_x + 16, y_px=iy + 20, w_px=panel_w - 32, h_px=60,
            font_size_px=10, color=TEXT_DARK,
        )
        iy += 90

    add_text(
        slide, "source-note",
        "Source: Q1 2026 Customer Pulse · n=1,240 · Fieldwork: March 2026",
        x_px=pn_x + 16, y_px=pn_y + body_h - 28, w_px=panel_w - 32, h_px=20,
        font_size_px=8, color=TEXT_FAINT, italic=True,
    )

    add_footer(slide, page_num=258)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "258_diverging-bar-chart.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
